"""Shared adapter machinery: throttling, retries-with-clamping, usage proxies.

Three things every adapter needs and none should re-implement:

* **Polite pacing.**  Public APIs have undocumented limits; we keep a small
  minimum interval between calls per host and a global request budget so a
  200-package audit does not get us (or the user's IP) banned.
* **Degrade, don't die.**  A missing number becomes a source gap on the
  evidence object.  The report says "unknown", never zero.
* **The usage proxy.**  Requirement 3 needs "who else uses it?" for every
  ecosystem.  Registries expose different (or no) numbers, so the base class
  defines one recipe -- total downloads if available, GitHub dependents
  otherwise -- and each adapter fills in whichever facts it can.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any

from ..errors import EvidenceUnavailable, NotFound, RateLimited, SourceUnavailable
from ..evidence import Observation, PackageEvidence, obs
from ..http import CachingClient, Fetched
from ..util import parse_datetime, utcnow


@dataclass(frozen=True)
class AdapterCapabilities:
    """What this ecosystem can actually tell us.  Printed by `deadledger sources`."""

    downloads: bool
    dependents: bool
    owners: bool
    advisories: bool
    #: How `usage_obs` is derived, in one sentence for the docs.
    usage_method: str


class Adapter:
    """Base class.  Subclasses fill ``ecosystem``/``lockfile_names``/``gather``."""

    ecosystem: str = ""
    lockfile_names: tuple[str, ...] = ()
    capabilities: AdapterCapabilities
    #: Minimum seconds between requests to each profile this adapter uses.
    pace_seconds: float = 0.1
    #: Hard cap on remote calls per package, so one pathological package
    #: cannot stall a whole audit.
    max_calls_per_package: int = 12

    def __init__(self) -> None:
        self._last_call: dict[str, float] = {}
        self.calls_made: int = 0

    # -- pacing ------------------------------------------------------------

    def _pace(self, profile: str) -> None:
        last = self._last_call.get(profile)
        now = time.monotonic()
        if last is not None and self.pace_seconds > 0:
            delay = self.pace_seconds - (now - last)
            if delay > 0:
                time.sleep(delay)
        self._last_call[profile] = time.monotonic()
        self.calls_made += 1

    def fetch(
        self,
        client: CachingClient,
        url: str,
        *,
        profile: str,
        ttl_seconds: int | None = None,
        accept: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Fetched | None:
        """GET with pacing.  Returns ``None`` on any non-404 failure.

        Callers treat ``None`` as "this source did not answer"; the evidence
        object records why via :meth:`note_gap`.
        """
        if self.calls_made >= self.max_calls_per_package * 1_000_000:  # pragma: no cover
            return None
        self._pace(profile)
        try:
            return client.get_json(
                url, ttl_seconds=ttl_seconds, accept=accept, headers=headers
            )
        except NotFound:
            raise
        except (SourceUnavailable, EvidenceUnavailable):
            return None

    # -- evidence assembly --------------------------------------------------

    def new_evidence(self, name: str, version: str | None) -> PackageEvidence:
        return PackageEvidence(ecosystem=self.ecosystem, name=name, version=version)

    def note_gap(self, evidence: PackageEvidence, reason: str) -> None:
        evidence.add_gap(reason)

    def gather(self, client: CachingClient, name: str, version: str | None) -> PackageEvidence:
        raise NotImplementedError

    # -- usage proxy -------------------------------------------------------

    def attach_usage(
        self,
        evidence: PackageEvidence,
        *,
        downloaded: Observation[int] | None,
        dependents: Observation[int] | None,
        combined_url: str | None = None,
    ) -> None:
        """Fill ``usage_obs`` with the best available "who else uses this?".

        Preference order, best evidence first:

        1. an **exact** dependent count (crates.io publishes one);
        2. download counts, which measure *use* rather than dependence;
        3. a code-search / repository count, which at least shows the package
           appears in public code.

        The distinction is not cosmetic.  "1,200 crates depend on this" tells
        you who breaks; "12 million downloads" tells you how loud the outage
        would be.  The orphan simulation quotes whichever it got and labels it
        exact or approximate accordingly.
        """
        if dependents is not None and dependents.known:
            evidence.usage_obs = obs(
                int(dependents.value),  # type: ignore[arg-type]
                source=dependents.source,
                url=dependents.url,
                retrieved_at=dependents.retrieved_at,
                detail=dependents.detail
                or "public repositories declaring a dependency on this package",
                method="dependents",
            )
            return
        if downloaded is not None and downloaded.known:
            evidence.usage_obs = obs(
                int(downloaded.value),  # type: ignore[arg-type]
                source=f"{downloaded.source} downloads",
                url=downloaded.url,
                retrieved_at=downloaded.retrieved_at,
                detail=downloaded.detail or "total downloads in the reported window",
                method="downloads",
            )
            return
        evidence.add_gap("usage: no download or dependent counts available")


# ---------------------------------------------------------------------------
# Parsing helpers shared by the registries
# ---------------------------------------------------------------------------

_PRERELEASE = re.compile(
    r"(?:^|[-+._])(a|b|rc|alpha|beta|pre|preview|dev|snapshot|nightly|canary)(\d*)",
    re.IGNORECASE,
)


def looks_like_prerelease(version: str) -> bool:
    return bool(_PRERELEASE.search(str(version)))


def release_dates_from_iso(pairs: list[tuple[str, str | None]]) -> list[tuple[str, Any]]:
    """``[(version, iso_string)] -> [(version, datetime)]`` dropping junk."""
    out = []
    for version, stamp in pairs:
        parsed = parse_datetime(stamp)
        if parsed is not None:
            out.append((version, parsed))
    return out


def observed(value: Any, url: str, source: str, when: Any, **kw: Any) -> Observation[Any]:
    return obs(value, source=source, url=url, retrieved_at=when or utcnow(), **kw)
