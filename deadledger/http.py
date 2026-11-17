"""Transport, caching, and the four operating modes.

Adapters never touch the network directly.  They ask a :class:`Client` for a
JSON document and get back a :class:`Fetched` -- the payload *plus* the URL
and the moment it was retrieved, which is exactly what a citation needs.

The layering is deliberate: :class:`CachingClient` wraps any inner client, so
"cache everything" and "record every response" are policies rather than
concerns spread through adapter code.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from . import __version__
from .cache import Cache
from .errors import FixtureMissing, NotFound, OfflineCacheMiss, RateLimited, SourceUnavailable
from .profiles import FIXTURE_ROOT, Profile, get_profile, profile_for_url
from .util import iso, utcnow

DEFAULT_TIMEOUT = 25.0
MAX_RETRIES = 2

#: Wall-clock ceiling for one audit's *network* phase.
#:
#: Retries are worth having -- a 502 from a registry is usually weather -- but
#: three attempts at a 25-second timeout, multiplied by a source that is firewalled
#: rather than merely slow, is how a CI job turns into a hung job. The first
#: GitHub Actions run of the dogfood workflow sat in "Mortality check" for
#: twenty minutes with nothing in the log, because every one of fourteen
#: packages was waiting out pypistats timeouts.
#:
#: After the deadline, sources are not attempted; the rest of the audit runs
#: from cache and the report says the evidence is missing. An incomplete report
#: in two minutes beats a complete one that never arrives.
NETWORK_DEADLINE_SECONDS = 180.0


def network_deadline_seconds(default: float | None = NETWORK_DEADLINE_SECONDS) -> float | None:
    """The deadline for this process, overridable for long recordings.

    ``DEADLEDGER_NETWORK_DEADLINE=0`` disables it (``record`` does that: it is a
    deliberate, human-attended operation over hundreds of URLs). ``--offline``
    and ``--replay`` never touch the network and ignore it entirely.
    """
    raw = os.environ.get("DEADLEDGER_NETWORK_DEADLINE")
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return None if value <= 0 else value


@dataclass(frozen=True)
class Fetched:
    """A JSON document and its provenance."""

    url: str
    payload: Any
    fetched_at: datetime
    status: int = 200
    from_cache: bool = False
    stale: bool = False
    profile: str = ""
    #: Only the handful of response headers we act on; never cached.
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def citation(self) -> str:
        return f"{self.url} (retrieved {iso(self.fetched_at)})"

    @property
    def rate_limit_remaining(self) -> int | None:
        raw = self.headers.get("x-ratelimit-remaining")
        try:
            return int(raw) if raw is not None else None
        except ValueError:
            return None

    @property
    def rate_limit_reset(self) -> int | None:
        raw = self.headers.get("x-ratelimit-reset")
        try:
            return int(raw) if raw is not None else None
        except ValueError:
            return None


@runtime_checkable
class Client(Protocol):
    def get_json(self, url: str, **kwargs: Any) -> Fetched: ...


# ---------------------------------------------------------------------------
# Live transport
# ---------------------------------------------------------------------------


class HttpxClient:
    """Real network access via httpx (the one third-party runtime dependency).

    Retries idempotent GETs on 429/502/503/504, honouring ``Retry-After``.
    Raises the DeadLedger error taxonomy rather than leaking httpx types, so
    adapters never have to know which transport ran.
    """

    def __init__(self, *, timeout: float = DEFAULT_TIMEOUT, headers: dict[str, str] | None = None):
        import httpx  # imported lazily so `deadledger --help` works without it

        self._httpx = httpx
        default_headers = {
            "User-Agent": f"deadledger/{__version__} (+https://github.com/pooria683/deadledger)",
            "Accept": "application/json",
        }
        default_headers.update(headers or {})
        self._client = httpx.Client(
            timeout=timeout, follow_redirects=True, headers=default_headers
        )
        self.deadline: float | None = None

    def get_json(self, url: str, *, headers: dict[str, str] | None = None, **_: Any) -> Fetched:
        if self.deadline is not None and time.monotonic() > self.deadline:
            raise SourceUnavailable(url, "network deadline for this run has passed")
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.get(url, headers=headers)
            except Exception as exc:  # httpx.TransportError and friends
                last_error = SourceUnavailable("http", f"{type(exc).__name__}: {exc}")
                if attempt < MAX_RETRIES:
                    time.sleep(0.5 * (2**attempt))
                    continue
                raise last_error from exc

            status = response.status_code
            if status == 404:
                raise NotFound(url, "not found")
            if status in (429, 502, 503, 504):
                retry_after = _retry_after_seconds(response.headers.get("retry-after"))
                if attempt < MAX_RETRIES:
                    time.sleep(retry_after if retry_after is not None else 1.0 * (2**attempt))
                    continue
                if status == 429:
                    raise RateLimited(url, "rate limited", retry_after=retry_after)
                raise SourceUnavailable(url, f"HTTP {status}", status=status)
            if status >= 400:
                detail = _error_detail(response)
                raise SourceUnavailable(url, f"HTTP {status}: {detail}", status=status)

            try:
                payload = response.json()
            except ValueError as exc:
                raise SourceUnavailable(url, "response was not JSON", status=status) from exc
            return Fetched(
                url=url,
                payload=payload,
                fetched_at=utcnow(),
                status=status,
                headers=_interesting_headers(response.headers),
            )

        raise last_error or SourceUnavailable(url, "exhausted retries")


class UrllibClient:
    """Socket-free fallback used only when httpx is not installed.

    Kept intentionally tiny: the project is stdlib-first, and this proves the
    core does not *depend* on httpx being importable.
    """

    def __init__(self, *, timeout: float = DEFAULT_TIMEOUT, headers: dict[str, str] | None = None):
        self._timeout = timeout
        self._headers = {
            "User-Agent": f"deadledger/{__version__} (+https://github.com/pooria683/deadledger)",
            "Accept": "application/json",
        }
        self._headers.update(headers or {})

    def get_json(self, url: str, *, headers: dict[str, str] | None = None, **_: Any) -> Fetched:
        import urllib.error
        import urllib.request

        merged = dict(self._headers)
        merged.update(headers or {})
        request = urllib.request.Request(url, headers=merged)
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:  # noqa: S310
                body = response.read()
                status = response.status
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise NotFound(url, "not found") from exc
            if exc.code == 429:
                raise RateLimited(url, "rate limited") from exc
            raise SourceUnavailable(url, f"HTTP {exc.code}", status=exc.code) from exc
        except Exception as exc:
            raise SourceUnavailable("http", f"{type(exc).__name__}: {exc}") from exc
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise SourceUnavailable(url, "response was not JSON", status=status) from exc
        return Fetched(url=url, payload=payload, fetched_at=utcnow(), status=status)


def _retry_after_seconds(header: str | None) -> int | None:
    if not header:
        return None
    try:
        return max(0, int(header))
    except ValueError:
        return None


def _interesting_headers(headers: Any) -> dict[str, str]:
    """Keep only the headers we act on *during this run*, lower-cased.

    ``x-ratelimit-*`` is deliberately excluded from what gets cached: it is a
    statement about the moment of retrieval, and replaying a stale
    "remaining: 0" would make a later run believe its quota is still spent.
    ``link`` is kept because pagination must survive a cache hit.
    """
    kept = {}
    for name in ("x-ratelimit-remaining", "x-ratelimit-reset", "link"):
        value = headers.get(name) if headers is not None else None
        if value:
            kept[name] = str(value)
    return kept


CACHE_SAFE_HEADERS = ("link",)


def headers_to_cache(headers: dict[str, str]) -> dict[str, str]:
    return {name: value for name, value in headers.items() if name in CACHE_SAFE_HEADERS}


def _error_detail(response: Any) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:160]
    if isinstance(data, dict):
        return str(data.get("message") or data.get("error") or "")[:160]
    return str(data)[:160]


# ---------------------------------------------------------------------------
# Caching + modes
# ---------------------------------------------------------------------------


def cache_key(profile: str, url: str, accept: str | None = None, query: str = "") -> str:
    """Stable key for a (profile, url, representation) triple.

    The URL is canonicalised first.  Query strings that embed the current clock
    -- GitHub's ``commits?since=<now - 365d>`` is the only one today -- would
    otherwise produce a different key on every run, so ``--offline`` would miss
    data that is sitting right there in the cache and the bus factor would
    quietly disappear from the report.
    """
    raw = f"{profile}\x1f{canonical_fixture_url(url)}\x1f{accept or ''}\x1f{query}"
    return sha256(raw.encode("utf-8")).hexdigest()


class CachingClient:
    """Cache-first JSON client with honest provenance.

    Mode is set once at construction: ``online``, ``offline``, ``record`` or
    ``replay``.  The inner client is only consulted for ``online``/``record``.
    """

    def __init__(
        self,
        inner: Client | None,
        cache: Cache,
        *,
        mode: str = "online",
        profile: str | None = None,
        fixture_root: Path | None = None,
        offline_profile: bool = False,
    ):
        if mode not in {"online", "offline", "record", "replay"}:
            raise ValueError(f"unknown mode {mode!r}")
        self.inner = inner
        self.cache = cache
        self.mode = mode
        self.profile = profile
        self.fixture_root = Path(fixture_root) if fixture_root else FIXTURE_ROOT
        #: URLs we could not refresh but served from stale cache.
        self.stale_urls: list[str] = []
        #: URLs that failed entirely (nothing in cache either).
        self.failed_urls: dict[str, str] = {}
        self.calls = 0
        self.cache_hits = 0
        self.live_fetches = 0
        self.replayed = 0
        #: Per-profile rate-limit budget, learned from response headers.
        self.rate_limits: dict[str, dict[str, int | None]] = {}
        #: Profiles we must not call again this run (quota exhausted).
        self.exhausted_profiles: set[str] = set()
        if mode == "replay" and not profile:
            raise ValueError("replay mode needs a fixture profile name")
        if mode == "record" and not profile:
            raise ValueError("record mode needs a fixture profile name")

    # -- main entry point ---------------------------------------------------

    def get_json(
        self,
        url: str,
        *,
        ttl_seconds: int | None = None,
        use_stale_on_error: bool = True,
        headers: dict[str, str] | None = None,
        accept: str | None = None,
        query: str = "",
        **_: Any,
    ) -> Fetched:
        resolved = profile_for_url(url)
        profile_name = resolved.name if resolved else "other"
        key = cache_key(profile_name, url, accept, query)
        self.calls += 1

        if self.mode == "replay":
            return self._replay(url, profile_name)

        entry = self.cache.get(key)
        if self.mode == "offline":
            if entry is None:
                self.failed_urls[url] = "offline and not cached"
                raise OfflineCacheMiss(url)
            if entry.expired:
                self.stale_urls.append(url)
            self.cache_hits += 1
            return _from_entry(entry, url, profile_name)

        ttl = ttl_seconds if ttl_seconds is not None else (resolved.ttl_seconds if resolved else 3600)
        if entry is not None and not entry.expired:
            self.cache_hits += 1
            return _from_entry(entry, url, profile_name, stale=False)

        if self._exhausted(url):
            if entry is not None:
                self.stale_urls.append(url)
                self.cache_hits += 1
                return _from_entry(entry, url, profile_name)
            bucket = _budget_for(url) or profile_name
            detail = f"{bucket} quota exhausted for this run"
            self.failed_urls[url] = detail
            raise SourceUnavailable(url, detail, status=429)

        try:
            fetched = self._live(url, headers=headers, accept=accept)
        except NotFound as exc:
            # 404 is evidence, not a transient failure: cache it so offline
            # runs can reproduce "the registry says this does not exist".
            self.cache.put(
                key,
                kind=profile_name,
                url=url,
                payload={"__error__": "not_found", "detail": exc.detail},
                ttl_seconds=min(ttl, 6 * 3600),
                status=404,
                query=query,
            )
            self.failed_urls[url] = "not found"
            raise
        except SourceUnavailable as exc:
            if entry is not None and use_stale_on_error:
                self.stale_urls.append(url)
                self.cache_hits += 1
                return _from_entry(entry, url, profile_name, stale=True)
            self.failed_urls[url] = str(exc)
            raise

        self._learn_rate_limit(profile_name, fetched)
        self.cache.put(
            key,
            kind=profile_name,
            url=url,
            payload=fetched.payload,
            ttl_seconds=ttl,
            status=fetched.status,
            etag=None,
            query=query,
            fetched_at=fetched.fetched_at,
            headers=headers_to_cache(fetched.headers),
        )
        if self.mode == "record":
            self._write_fixture(url, fetched)
        return Fetched(
            url=url,
            payload=fetched.payload,
            fetched_at=fetched.fetched_at,
            status=fetched.status,
            from_cache=False,
            stale=False,
            profile=profile_name,
        )

    def learn_rate_limits(self, url: str = "https://api.github.com/rate_limit") -> None:
        """Ask GitHub for its budgets and pre-emptively go cache-only.

        Without this, a 100-package audit on a 30-request search budget would
        burn one request per package discovering the limit the hard way, and
        every discovery would be a *failed source*.  Knowing the budget up
        front turns those failures into "skipped, quota exhausted" gaps, which
        is accurate: we chose not to spend a request, rather than the source
        not answering.
        """
        if self.mode not in {"online", "record"} or self.inner is None:
            return
        try:
            fetched = self._live(url, headers=None, accept=None)
        except SourceUnavailable:
            return
        resources = (fetched.payload or {}).get("resources") or {}
        buckets = {
            "github": resources.get("core"),
            "github-search": resources.get("search"),
            "github-code-search": resources.get("code_search"),
        }
        for name, block in buckets.items():
            if not isinstance(block, dict):
                continue
            remaining = block.get("remaining")
            if isinstance(remaining, int):
                self.rate_limits[name] = {
                    "remaining": remaining,
                    "reset": block.get("reset"),
                }
                if remaining <= 0:
                    self.exhausted_profiles.add(name)

    def budget(self, url: str) -> int | None:
        """How many more requests may we spend on this URL's budget?

        GitHub bills ``/search/code``, ``/search/*`` and everything else to
        three *separate* buckets with very different sizes (10, 30 and 5,000
        per hour for an authenticated token).  Mixing them up is how an audit
        talks itself into cache-only mode on a budget it never touched, so the
        mapping lives in one function and is tested.
        """
        name = _budget_for(url)
        if name is None:
            return None
        block = self.rate_limits.get(name)
        if block is None:
            return None
        remaining = block.get("remaining")
        return remaining if isinstance(remaining, int) else None

    def spend(self, url: str, *, hit_cache: bool = False) -> None:
        """Record that one live request against this URL's budget was spent."""
        if hit_cache:
            return
        name = _budget_for(url)
        if name is None:
            return
        block = self.rate_limits.get(name)
        if block is None:
            return
        remaining = block.get("remaining")
        if not isinstance(remaining, int):
            return
        block["remaining"] = max(0, remaining - 1)
        if block["remaining"] == 0:
            self.exhausted_profiles.add(name)
            self.failed_urls.setdefault(
                url, f"{name}: quota exhausted, remaining calls served from cache"
            )

    # Back-compat alias used by the adapters.
    def consume(self, url: str) -> None:
        self.spend(url)

    def _exhausted(self, url: str) -> bool:
        """Is *this specific bucket* spent?  (Not the whole profile.)"""
        name = _budget_for(url)
        return name is not None and name in self.exhausted_profiles

    def _learn_rate_limit(self, profile: str, fetched: Fetched) -> None:
        """Record what a response says about the quota it was billed to.

        Keyed by *bucket*, not by profile, because that is how ``budget()`` and
        ``spend()`` look it up.  Filing it under the profile name meant a
        learned "github: 4999 left" was invisible to the code that was checking
        "github-search: 30" -- and, worse, a single 4xx from PyPI taught us
        "pypi: 0 remaining", which then blocked every subsequent PyPI lookup
        for the rest of the run.
        """
        remaining = fetched.rate_limit_remaining
        if remaining is None:
            return
        bucket = _budget_for(fetched.url)
        if bucket is None:
            return
        self.rate_limits[bucket] = {
            "remaining": remaining,
            "reset": fetched.rate_limit_reset,
        }
        if remaining <= 0:
            # A 0 recorded on a real response is authoritative for its bucket.
            self.exhausted_profiles.add(bucket)

    # -- modes --------------------------------------------------------------

    def _live(self, url: str, *, headers: dict[str, str] | None, accept: str | None) -> Fetched:
        if self.inner is None:  # pragma: no cover - guards misconfiguration
            raise SourceUnavailable(url, "no transport configured")
        self.live_fetches += 1
        resolved = profile_for_url(url)
        merged: dict[str, str] = {}
        token = github_token() if resolved and resolved.name == "github" else None
        if token and resolved and resolved.auth_header:
            merged[resolved.auth_header] = f"Bearer {token}"
        if resolved and resolved.user_agent:
            merged.setdefault("User-Agent", resolved.user_agent.format(version=__version__))
        if accept:
            merged["Accept"] = accept
        elif resolved and resolved.accepts:
            merged.setdefault("Accept", resolved.accepts)
        merged.update(headers or {})
        return self.inner.get_json(url, headers=merged)

    def _replay(self, url: str, profile_name: str) -> Fetched:
        recorded = read_fixture(self.fixture_root, self.profile or "", url)
        if recorded is None:
            raise FixtureMissing(self.profile or "", url)
        self.replayed += 1
        payload, recorded_at, status = recorded
        if status == 404:
            raise NotFound(url, "not found (recorded)")
        if status == 0:
            # A recorded *failure*.  Replaying it faithfully is the point:
            # the report must degrade identically whether the source is down
            # today or was down when the fixtures were made.
            detail = ""
            if isinstance(payload, dict):
                detail = str(payload.get("__error_detail__") or "")
            raise SourceUnavailable(url, detail or "recorded source failure")
        # Mirror the recording into the cache so replay builds a real cache:
        # `deadledger --offline` can then reuse it, and the cache's newest
        # timestamp becomes the audit clock.
        self.cache.put(
            cache_key(profile_name, url),
            kind=profile_name,
            url=url,
            payload=payload,
            ttl_seconds=30 * 24 * 3600,
            status=status,
            fetched_at=recorded_at,
        )
        return Fetched(
            url=url,
            payload=payload,
            fetched_at=recorded_at,
            status=status,
            from_cache=True,
            profile=profile_name,
        )

    def _write_fixture(self, url: str, fetched: Fetched) -> None:
        # A recording with no profile cannot be written anywhere meaningful:
        # tests use `mode="record"` purely to drive an in-memory PlaybackClient,
        # and writing those to the default fixture root used to litter
        # tests/fixtures/t/ with whatever URL a stub happened to serve.
        if not self.profile:
            return
        write_fixture(self.fixture_root, self.profile, url, fetched)

    # -- introspection ------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "calls": self.calls,
            "cache_hits": self.cache_hits,
            "live_fetches": self.live_fetches,
            "replayed": self.replayed,
            "stale_urls": len(self.stale_urls),
            "failed_urls": len(self.failed_urls),
            "rate_limits": self.rate_limits,
            "exhausted_profiles": sorted(self.exhausted_profiles),
        }


#: Profiles that publish a request quota in their response headers.
#: Everything else is unlimited for our purposes, and pretending otherwise is
#: how PyPI's 206 lookups once drained GitHub's 5,000-request budget: every
#: non-GitHub URL used to be filed under "github".
RATE_LIMITED_PROFILES = frozenset({"github"})


def _budget_for(url: str) -> str | None:
    """Which quota bucket does this URL spend from?  ``None`` means unbounded."""
    resolved = profile_for_url(url)
    profile = resolved.name if resolved else None
    if profile not in RATE_LIMITED_PROFILES:
        return None
    if "/search/code" in url:
        return "github-code-search"
    if "/search/" in url:
        return "github-search"
    return "github"


def _from_entry(
    entry: Any, url: str, profile: str, *, stale: bool | None = None
) -> Fetched:
    return Fetched(
        url=url,
        payload=entry.payload,
        fetched_at=entry.fetched_at,
        status=entry.status,
        from_cache=True,
        stale=entry.expired if stale is None else stale,
        profile=profile,
        headers=dict(entry.headers or {}),
    )


def github_token() -> str | None:
    for name in get_profile("github").auth_env:
        value = os.environ.get(name)
        if value:
            return value.strip()
    return None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_VOLATILE_QUERY = re.compile(r"(since|until)=\d{4}-\d{2}-\d{2}T[0-9:%A-Za-z+.-]*")


def canonical_fixture_url(url: str) -> str:
    """Strip query values that change every run.

    ``?since=<now - 365d>`` makes a commit URL different on every recording and
    on every replay, which would mean an untouched repository re-records as a
    "gap".  The window is part of the *test scenario*, not the URL, so it is
    normalised away here and reconstructed by the caller when it matters.
    """
    return _VOLATILE_QUERY.sub(r"\1=<window>", url)


def _fixture_path(root: Path, profile: str, url: str) -> Path:
    url = canonical_fixture_url(url)
    digest = sha256(url.encode("utf-8")).hexdigest()[:20]
    safe = (
        url.split("://", 1)[-1]
        .replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace(":", "_")
    )[:90]
    return root / profile / f"{safe}.{digest}.json"


class PlaybackClient:
    """Serves JSON from memory while remembering *which* URLs were asked for.

    Recording goes through the real adapter code twice: once live (to learn
    what to fetch), once in playback (to learn what an audit actually needs).
    Only the playback pass's URLs are written, so the shipped fixtures stay
    small instead of archiving verbose packuments nobody reads.
    """

    def __init__(self, documents: dict[str, Any], errors: dict[str, str] | None = None):
        # Index by canonical URL: a commit window is derived from the clock, so
        # pass 1 and pass 2 of a recording ask for slightly different
        # `?since=` values for the same underlying document.
        self._documents = {canonical_fixture_url(url): body for url, body in documents.items()}
        self._errors = {canonical_fixture_url(url): reason for url, reason in (errors or {}).items()}
        self.asked: list[str] = []
        self.mode = "record"

    # A playback client is not a network client: adapters may ask it for a
    # budget, and the honest answer is "unknown" (None), never zero -- telling
    # an adapter its quota is spent would make it skip sources entirely.
    def budget(self, url: str) -> int | None:
        return None

    def consume(self, url: str) -> None:
        return None

    def learn_rate_limits(self, url: str = "") -> None:
        return None

    def get_json(self, url: str, **_: Any) -> Fetched:
        self.asked.append(url)
        canonical = canonical_fixture_url(url)
        if canonical in self._documents:
            return Fetched(url=url, payload=self._documents[canonical], fetched_at=utcnow())
        raise SourceUnavailable(url, self._errors.get(canonical, "not recorded"))


def trim_payload(url: str, payload: Any) -> Any:
    """Shrink a recorded document to the fields the adapters actually read.

    Trimming is lossy on purpose: a 4 MB Pillow packument makes the fixture
    suite slow to clone for no extra coverage, because the rubric never looks
    at the release notes.  Each branch below is covered by an adapter test that
    would fail if a field the code needs disappeared.
    """
    if not isinstance(payload, dict):
        return payload
    if "pypi.org/pypi/" in url:
        info = payload.get("info") or {}
        keep_info = {
            key: info.get(key)
            for key in (
                "name",
                "version",
                "summary",
                "license",
                "license_expression",
                "home_page",
                "project_url",
                "project_urls",
                "bugtrack_url",
                "classifiers",
                "yanked",
                "yanked_reason",
            )
        }
        releases = {}
        for version, files in (payload.get("releases") or {}).items():
            if not isinstance(files, list):
                continue
            releases[version] = [
                {
                    "upload_time_iso_8601": item.get("upload_time_iso_8601"),
                    "upload_time": item.get("upload_time"),
                    "yanked": item.get("yanked"),
                    "packagetype": item.get("packagetype"),
                }
                for item in files
                if isinstance(item, dict)
            ]
        return {
            "info": keep_info,
            "releases": releases,
            "ownership": payload.get("ownership"),
        }
    if "registry.npmjs.org" in url:
        versions = payload.get("versions") or {}
        trimmed = {}
        for version, meta in versions.items():
            if isinstance(meta, dict):
                trimmed[version] = {
                    "version": meta.get("version"),
                    "deprecated": meta.get("deprecated"),
                    "repository": meta.get("repository"),
                }
        return {
            "name": payload.get("name"),
            "description": payload.get("description"),
            "license": payload.get("license"),
            "homepage": payload.get("homepage"),
            "repository": payload.get("repository"),
            "bugs": payload.get("bugs"),
            "dist-tags": payload.get("dist-tags"),
            "maintainers": payload.get("maintainers"),
            "time": payload.get("time"),
            "versions": trimmed,
        }
    if "api.github.com/repos/" in url and "/commits" in url:
        if isinstance(payload, list):
            return [
                {
                    "sha": entry.get("sha"),
                    "author": entry.get("author"),
                    "commit": {
                        "author": (entry.get("commit") or {}).get("author"),
                    },
                }
                for entry in payload
                if isinstance(entry, dict)
            ]
        return payload
    if "api.github.com/repos/" in url:
        keep = {
            key: payload.get(key)
            for key in (
                "full_name",
                "html_url",
                "archived",
                "pushed_at",
                "open_issues_count",
                "stargazers_count",
                "default_branch",
            )
        }
        return keep
    return payload


def write_fixture(root: Path, profile: str, url: str, fetched: Fetched) -> Path:
    path = _fixture_path(root, profile, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "url": canonical_fixture_url(url),
        "status": fetched.status,
        "recorded_at": iso(fetched.fetched_at),
        "recorded_with": f"deadledger {__version__}",
        "body": trim_payload(url, fetched.payload),
    }
    path.write_text(json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return path


def write_failure(root: Path, profile: str, url: str, reason: str) -> Path:
    """Record a source that did *not* answer, so replay reproduces the gap."""
    path = _fixture_path(root, profile, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "url": canonical_fixture_url(url),
        "status": 0,
        "recorded_at": iso(utcnow()),
        "error": reason,
    }
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    return path


def read_fixture(root: Path, profile: str, url: str) -> tuple[Any, datetime, int] | None:
    path = _fixture_path(root, profile, url)
    if not path.exists():
        return None
    document = json.loads(path.read_text())
    from .util import parse_datetime

    recorded_at = parse_datetime(document.get("recorded_at")) or utcnow()
    status = int(document.get("status", 200))
    payload = document.get("body")
    if status == 0:
        payload = {"__error_detail__": document.get("error") or "recorded failure"}
    return payload, recorded_at, status


def fixture_index(root: Path, profile: str) -> list[dict[str, Any]]:
    directory = root / profile
    if not directory.is_dir():
        return []
    rows = []
    for path in sorted(directory.glob("*.json")):
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError:  # pragma: no cover
            continue
        rows.append(
            {
                "file": path.name,
                "url": document.get("url"),
                "recorded_at": document.get("recorded_at"),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------


@dataclass
class ClientBundle:
    """The client plus the knobs the CLI wants to report on."""

    client: CachingClient
    notes: list[str] = field(default_factory=list)


def build_client(
    *,
    cache: Cache,
    mode: str = "online",
    fixture_profile: str | None = None,
    fixture_root: Path | None = None,
    offline: bool = False,
) -> CachingClient:
    """Construct the right client for a mode, with httpx if available."""
    effective = "offline" if offline else mode
    inner: Client | None = None
    if effective in {"online", "record"}:
        try:
            inner = HttpxClient()
        except Exception:  # pragma: no cover - httpx missing
            inner = UrllibClient()
        budget = network_deadline_seconds()
        inner.deadline = time.monotonic() + budget if budget else None
    return CachingClient(
        inner,
        cache,
        mode=effective,
        profile=fixture_profile,
        fixture_root=fixture_root,
    )
