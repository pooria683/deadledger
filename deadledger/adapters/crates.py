"""crates.io adapter.

Sources:

==================================  ========================================
crates.io/api/v1/crates/{name}      versions, publish dates, repository
crates.io/api/v1/crates/{name}/owners  owning teams and users
crates.io/api/v1/crates/{name}/reverse_dependencies  dependent crates
github.com                          bus factor and triage
==================================  ========================================

crates.io is the only one of the three registries that publishes a real
dependent count, which makes the orphan simulation exact rather than
approximate for Rust.  It also asks clients to send a descriptive
User-Agent; that is configured on the ``crates`` profile.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from ..errors import NotFound
from ..evidence import Maintainer, PackageEvidence, ReleasePoint, obs
from ..http import CachingClient, Fetched
from ..util import iso, parse_datetime, utcnow
from .base import Adapter, AdapterCapabilities, looks_like_prerelease

API = "https://crates.io/api/v1/crates"


class CratesAdapter(Adapter):
    ecosystem = "crates"
    lockfile_names = ("Cargo.lock",)
    capabilities = AdapterCapabilities(
        downloads=True,
        dependents=True,
        owners=True,
        advisories=False,
        usage_method="crates.io reverse-dependency count (exact, not a proxy)",
    )
    pace_seconds = 1.0  # crates.io asks for 1 req/s
    max_calls_per_package = 4

    def gather(self, client: CachingClient, name: str, version: str | None) -> PackageEvidence:
        evidence = self.new_evidence(name, version)
        url = f"{API}/{name}"
        evidence.registry_url = url
        try:
            fetched = self.fetch(client, url, profile="crates")
        except NotFound:
            evidence.add_gap("registry: crate does not exist on crates.io")
            return evidence
        if fetched is None:
            evidence.add_gap("registry: crates.io did not answer")
            return evidence

        self._parse_crate(evidence, fetched, version)
        self._attach_owners(client, evidence, name)
        self._attach_reverse_dependencies(client, evidence, name)
        return evidence

    # -- crate -------------------------------------------------------------

    def _parse_crate(
        self, evidence: PackageEvidence, fetched: Fetched, requested: str | None
    ) -> None:
        payload = fetched.payload or {}
        crate = payload.get("crate") or {}
        versions = payload.get("versions") or []
        retrieved = fetched.fetched_at

        evidence.registry_ok = True
        evidence.registry_retrieved_at = retrieved
        evidence.name = str(crate.get("name") or evidence.name)
        evidence.summary = crate.get("description") or None
        evidence.homepage = crate.get("homepage") or None
        evidence.latest_version = crate.get("max_stable_version") or crate.get("newest_version")
        from ..util import parse_github_repo

        evidence.repository = parse_github_repo(crate.get("repository"))

        points: list[ReleasePoint] = []
        for entry in versions:
            if not isinstance(entry, dict):
                continue
            when = parse_datetime(entry.get("created_at"))
            version_text = str(entry.get("num") or "")
            if when is None or not version_text:
                continue
            points.append(
                ReleasePoint(
                    version=version_text,
                    published_at=when,
                    prerelease=bool(entry.get("yanked") is False)
                    and looks_like_prerelease(version_text),
                    yanked=bool(entry.get("yanked")),
                )
            )
        points.sort(key=lambda p: p.published_at)
        evidence.releases = points

        audited = next((p for p in points if p.version == (requested or evidence.latest_version)), None)
        if audited is not None and audited.yanked:
            evidence.deprecated = True
            evidence.deprecation_message = f"version {audited.version} is yanked on crates.io"

        stable = evidence.stable_releases()
        last_publish = stable[-1].published_at if stable else None
        evidence.last_publish_obs = obs(
            iso(last_publish),
            source="crates.io",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="created_at of the newest non-prerelease, non-yanked version",
            method="max(versions[*].created_at)",
        )
        if last_publish is None:
            evidence.add_gap("registry: no dated stable version")

        window_start = retrieved - timedelta(days=365)
        evidence.releases_12mo_obs = obs(
            sum(1 for point in stable if point.published_at >= window_start),
            source="crates.io",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="stable versions published in the 365 days before retrieval",
        )

        downloads = crate.get("downloads")
        if isinstance(downloads, int):
            evidence.download_count_obs = obs(
                downloads,
                source="crates.io",
                url=fetched.url,
                retrieved_at=retrieved,
                detail="lifetime downloads of all versions",
                method="crate.downloads",
            )
        recent = crate.get("recent_downloads")
        if isinstance(recent, int) and isinstance(downloads, int) and downloads:
            evidence.download_trend_obs = obs(
                round(recent / max(downloads, 1), 4),
                source="crates.io",
                url=fetched.url,
                retrieved_at=retrieved,
                detail="recent (90 day) downloads as a share of all-time downloads",
                method="recent_downloads / downloads",
            )

        evidence.open_issues_obs = obs(
            None,
            source="crates.io",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="crates.io exposes no issue-tracker data",
        )

    # -- owners ------------------------------------------------------------

    def _attach_owners(
        self, client: CachingClient, evidence: PackageEvidence, name: str
    ) -> None:
        url = f"{API}/{name}/owners"
        try:
            fetched = self.fetch(client, url, profile="crates")
        except NotFound:
            fetched = None
        if fetched is None:
            evidence.add_gap("registry: owner list unavailable")
            return
        users = (fetched.payload or {}).get("users") or []
        people = [
            Maintainer(
                name=str(user.get("login")),
                role="owner",
                url=user.get("url") or f"https://crates.io/users/{user.get('login')}",
            )
            for user in users
            if isinstance(user, dict) and user.get("login")
        ]
        evidence.maintainers = people
        evidence.maintainer_count_obs = obs(
            len(people) if people else None,
            source="crates.io",
            url=fetched.url,
            retrieved_at=fetched.fetched_at,
            detail="owners (users and teams) of the crate",
            method="len(users)",
        )

    # -- orphan simulation -------------------------------------------------

    def _attach_reverse_dependencies(
        self, client: CachingClient, evidence: PackageEvidence, name: str
    ) -> None:
        url = f"{API}/{name}/reverse_dependencies?per_page=1"
        try:
            fetched = self.fetch(client, url, profile="crates")
        except NotFound:
            fetched = None
        if fetched is None:
            evidence.add_gap("usage: reverse dependencies unavailable")
            self.attach_usage(evidence, downloaded=evidence.download_count_obs, dependents=None)
            return
        payload = fetched.payload or {}
        total = payload.get("meta", {}).get("total") if isinstance(payload, dict) else None
        if not isinstance(total, int):
            total = len(payload.get("dependencies") or []) if isinstance(payload, dict) else None
        dependents = None
        if isinstance(total, int):
            dependents = obs(
                total,
                source="crates.io",
                url=fetched.url,
                retrieved_at=fetched.fetched_at,
                detail="crates that declare a dependency on this crate",
                method="reverse_dependencies.meta.total",
            )
            evidence.dependents_obs = dependents
        self.attach_usage(evidence, downloaded=None, dependents=dependents)
