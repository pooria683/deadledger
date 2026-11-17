"""PyPI adapter.

Sources, in order of importance:

======================================  =====================================
pypi.org/pypi/{name}/json               releases, upload times, owner roles
pypistats.org/api/packages/<n>/overall   lifetime + 180-day download counts
github.com code search                   usage proxy (``import <module>``)
======================================  =====================================

PyPI publishes no "dependent packages" count, so the orphan simulation for
Python falls back to two approximations, in preference order: total recorded
downloads (pypistats) and the number of files on GitHub containing
``import <module>``.  Both are labelled as proxies wherever they appear: a
code-search total is not a download count and we never present it as one.

Every fetch is optional.  A source that does not answer becomes a *source
gap* on the evidence object -- the report says "unknown", never zero.
"""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any
from urllib.parse import quote_plus

from ..errors import NotFound
from ..evidence import Maintainer, PackageEvidence, ReleasePoint, obs
from ..http import CachingClient, Fetched, github_token
from ..util import iso, parse_datetime
from .base import Adapter, AdapterCapabilities, looks_like_prerelease

PACKUMENT_TMPL = "https://pypi.org/pypi/{name}/json"
OWNERSHIP_TMPL = "https://pypi.org/pypi/{name}/json"
STATS_TMPL = "https://pypistats.org/api/packages/{name}/overall"


class PyPIAdapter(Adapter):
    ecosystem = "pypi"
    lockfile_names = (
        "requirements.txt",
        "requirements-dev.txt",
        "requirements_dev.txt",
        "requirements-test.txt",
        "constraints.txt",
        "Pipfile.lock",
        "poetry.lock",
        "uv.lock",
        "pdm.lock",
    )
    capabilities = AdapterCapabilities(
        downloads=True,
        dependents=False,
        owners=True,
        advisories=False,
        usage_method=(
            "total downloads recorded by pypistats; falls back to a GitHub "
            "code-search count for the package's import statement"
        ),
    )
    pace_seconds = 0.12
    max_calls_per_package = 6
    #: GitHub's code-search endpoint allows ~10 requests/minute unauthenticated
    #: on a good day, so we spend at most this many per audit and then say so.
    #: Downloads are the preferred usage signal anyway; this is a fallback for
    #: packages pypistats does not cover.
    code_search_budget = 8

    def __init__(self) -> None:
        super().__init__()
        self._code_searches_used = 0

    # -- entry point -------------------------------------------------------

    def gather(self, client: CachingClient, name: str, version: str | None) -> PackageEvidence:
        evidence = self.new_evidence(name, version)
        canonical = normalise_name(name)
        url = PACKUMENT_TMPL.format(name=canonical)
        evidence.registry_url = url
        try:
            fetched = self.fetch(client, url, profile="pypi")
        except NotFound:
            evidence.add_gap("registry: package does not exist on PyPI")
            return evidence
        if fetched is None:
            evidence.add_gap("registry: PyPI did not answer")
            return evidence

        self._parse_packument(evidence, fetched)
        # Requirement 3 wants "who else uses it?"; collect the proxies we can.
        self._attach_usage(client, evidence, canonical)
        return evidence

    # -- packument ---------------------------------------------------------

    def _parse_packument(self, evidence: PackageEvidence, fetched: Fetched) -> None:
        payload = fetched.payload or {}
        info = payload.get("info") or {}
        releases = payload.get("releases") or {}
        retrieved = fetched.fetched_at

        evidence.registry_ok = True
        evidence.registry_retrieved_at = retrieved
        evidence.name = info.get("name") or evidence.name
        evidence.summary = info.get("summary") or None
        evidence.license = first_line(info.get("license_expression") or info.get("license"))
        evidence.latest_version = info.get("version")
        evidence.homepage = first_truthy(
            (info.get("project_urls") or {}).get("Homepage"),
            info.get("project_url"),
            info.get("home_page"),
        )
        evidence.repository = repository_from_info(info)
        evidence.homepage = any_repo_url(info)

        evidence.releases = _release_points(releases)
        stable = evidence.stable_releases()
        last_publish = stable[-1].published_at if stable else None
        evidence.last_publish_obs = obs(
            iso(last_publish),
            source="pypi",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="upload time of the newest non-prerelease, non-yanked release",
            method="max(releases[*].upload_time)",
        )
        if last_publish is None:
            evidence.add_gap("registry: no dated stable release in the packument")

        window_start = retrieved - timedelta(days=365)
        evidence.releases_12mo_obs = obs(
            sum(1 for point in stable if point.published_at >= window_start),
            source="pypi",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="stable releases published in the 365 days before retrieval",
        )
        evidence.open_issues_obs = obs(
            None,
            source="pypi",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="PyPI exposes no issue-tracker data",
        )

        self._parse_owners(evidence, payload, fetched)
        self._parse_deprecation(evidence, info)

    def _parse_owners(self, evidence: PackageEvidence, payload: dict[str, Any], fetched: Fetched) -> None:
        roles = (payload.get("ownership") or {}).get("roles") or []
        owners = [
            Maintainer(
                name=str(entry.get("user")),
                role=str(entry.get("role") or "Owner").lower(),
                url=f"https://pypi.org/user/{entry.get('user')}/",
            )
            for entry in roles
            if isinstance(entry, dict) and entry.get("user")
        ]
        evidence.maintainers = owners
        if owners:
            evidence.maintainer_count_obs = obs(
                len(owners),
                source="pypi",
                url=fetched.url,
                retrieved_at=fetched.fetched_at,
                detail="accounts with a role in the project's PyPI ownership record",
                method="len(ownership.roles)",
            )
        else:
            evidence.maintainer_count_obs = obs(
                None,
                source="pypi",
                url=fetched.url,
                retrieved_at=fetched.fetched_at,
                detail="PyPI published no ownership roles for this project",
            )
            evidence.add_gap("registry: no ownership roles published")

    def _parse_deprecation(self, evidence: PackageEvidence, info: dict[str, Any]) -> None:
        if info.get("yanked_reason"):
            evidence.deprecated = True
            evidence.deprecation_message = str(info["yanked_reason"])
            return
        classifiers = " ".join(info.get("classifiers") or [])
        if "Development Status :: 7 - Inactive" in classifiers:
            evidence.deprecated = True
            evidence.deprecation_message = "PyPI classifier: Development Status :: 7 - Inactive"

    # -- usage -------------------------------------------------------------

    def _attach_usage(
        self, client: CachingClient, evidence: PackageEvidence, canonical: str
    ) -> None:
        downloads = self._downloads(client, evidence, canonical)
        dependents = self._code_search_count(client, evidence, canonical)
        self.attach_usage(evidence, downloaded=downloads, dependents=dependents)

    def _downloads(
        self, client: CachingClient, evidence: PackageEvidence, canonical: str
    ) -> Any:
        url = STATS_TMPL.format(name=canonical)
        try:
            fetched = self.fetch(client, url, profile="pypistats")
        except NotFound:
            fetched = None
        if fetched is None:
            evidence.add_gap("usage: pypistats did not answer (download counts unknown)")
            return None
        rows = (fetched.payload or {}).get("data")
        if not isinstance(rows, list) or not rows:
            evidence.add_gap("usage: pypistats returned no daily rows")
            return None
        values = [int(row.get("downloads") or 0) for row in rows if isinstance(row, dict)]
        if not values:
            return None
        total = sum(values)
        evidence.download_count_obs = obs(
            total,
            source="pypistats",
            url=fetched.url,
            retrieved_at=fetched.fetched_at,
            detail=f"downloads summed over {len(values)} recent daily rows",
            method="sum(daily downloads)",
        )
        evidence.download_trend_obs = obs(
            trend(values),
            source="pypistats",
            url=fetched.url,
            retrieved_at=fetched.fetched_at,
            detail="relative change between the older and newer half of the window",
            method="(mean(newer) - mean(older)) / mean(older)",
        )
        return evidence.download_count_obs

    def _code_search_count(
        self, client: CachingClient, evidence: PackageEvidence, canonical: str
    ) -> Any:
        """How many files across GitHub import this package?  A usage *proxy*.

        Requires a GitHub token because the code-search API refuses anonymous
        callers.  Without a token we say so rather than reporting zero.
        """
        if not github_token():
            evidence.add_gap("usage: no GitHub token, import-search proxy unavailable")
            return None
        if self._code_searches_used >= self.code_search_budget:
            evidence.add_gap(
                "usage: GitHub code-search budget for this run is spent"
            )
            return None
        module = canonical.replace("-", "_")
        query = f'"import {module}" in:file'
        url = (
            "https://api.github.com/search/code?q="
            f"{quote_plus(query)}&per_page=1"
        )
        try:
            fetched = self.fetch(client, url, profile="github", accept="application/vnd.github+json")
        except NotFound:
            fetched = None
        if fetched is None:
            evidence.add_gap("usage: GitHub code search did not answer")
            return None
        if not fetched.from_cache:
            self._code_searches_used += 1
            client.consume(url)
        count = (fetched.payload or {}).get("total_count")
        if not isinstance(count, int):
            return None
        return obs(
            count,
            source="github code search",
            url=fetched.url,
            retrieved_at=fetched.fetched_at,
            detail=f"files containing {query!r}",
            method="search total_count",
        )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def normalise_name(name: str) -> str:
    """PEP 503 normalisation."""
    return re.sub(r"[-_.]+", "-", str(name)).lower()


def first_truthy(*values: Any) -> str | None:
    for value in values:
        if value:
            return str(value)
    return None


def first_line(value: Any) -> str | None:
    text = first_truthy(value)
    if not text:
        return None
    line = text.strip().splitlines()[0].strip()
    return line[:120] or None


def any_repo_url(info: dict[str, Any]) -> str | None:
    """The project's source/homepage URL, whichever forge hosts it.

    ``repository`` is the *GitHub* slug, because that is the only forge we can
    read.  When a project is hosted elsewhere (openpyxl lives on Heptapod,
    many others on GitLab or SourceHut) the report must say "we cannot read
    this forge", not "there is no repository" -- the latter is simply false and
    a reader will catch it.
    """
    urls = info.get("project_urls") or {}
    for preferred in ("Source", "Source Code", "Repository", "Code", "Homepage"):
        value = urls.get(preferred)
        if value:
            return str(value)
    for key, value in urls.items():
        if any(word in str(key).lower() for word in ("source", "repo", "code", "home")):
            if value:
                return str(value)
    for value in (info.get("home_page"), info.get("project_url")):
        if value:
            return str(value)
    return None


def repository_from_info(info: dict[str, Any]) -> str | None:
    """Find ``owner/name`` from whatever URL fields the project filled in."""
    from ..util import parse_github_repo

    urls = info.get("project_urls") or {}
    candidates: list[Any] = []
    for preferred in ("Source", "Source Code", "Repository", "Code", "GitHub", "Homepage"):
        if preferred in urls:
            candidates.append(urls[preferred])
    for key, value in urls.items():
        if any(word in str(key).lower() for word in ("source", "repo", "code", "github")):
            candidates.append(value)
    candidates.extend(
        [info.get("home_page"), info.get("project_url"), info.get("bugtrack_url")]
    )
    return parse_github_repo(*candidates)


def _release_points(releases: dict[str, Any]) -> list[ReleasePoint]:
    points: list[ReleasePoint] = []
    for version, files in releases.items():
        if not isinstance(files, list) or not files:
            # Zero files means the release was deleted or fully yanked.
            continue
        timestamps = []
        all_yanked = True
        for item in files:
            if not isinstance(item, dict):
                continue
            if not item.get("yanked"):
                all_yanked = False
            parsed = parse_datetime(item.get("upload_time_iso_8601") or item.get("upload_time"))
            if parsed:
                timestamps.append(parsed)
        if not timestamps:
            continue
        points.append(
            ReleasePoint(
                version=str(version),
                published_at=max(timestamps),
                prerelease=looks_like_prerelease(str(version)),
                yanked=all_yanked,
            )
        )
    points.sort(key=lambda p: p.published_at)
    return points


def trend(values: list[int]) -> float | None:
    if len(values) < 4:
        return None
    mid = len(values) // 2
    older = sum(values[:mid]) / mid
    newer = sum(values[mid:]) / (len(values) - mid)
    if older == 0:
        return None
    return round((newer - older) / older, 4)
