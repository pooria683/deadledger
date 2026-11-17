"""npm adapter.

Sources:

======================================  ====================================
registry.npmjs.org/{name}               packument: versions, maintainers,
                                        deprecation flags, repository
api.npmjs.org/downloads/point/last-month  download count for the last month
api.npmjs.org/downloads/range/...       week-by-week trend (optional)
github.com                              used for bus factor and triage
======================================  ====================================

npm is the friendliest registry of the three: the packument carries
per-version publish times, an explicit ``deprecated`` message per version and
the maintainer list.  It has no dependent count, so the orphan simulation uses
downloads.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from urllib.parse import quote

from ..errors import NotFound
from ..evidence import Maintainer, PackageEvidence, ReleasePoint, obs
from ..http import CachingClient, Fetched
from ..util import iso, parse_datetime
from .base import Adapter, AdapterCapabilities, looks_like_prerelease

PACKUMENT_TMPL = "https://registry.npmjs.org/{name}"
DOWNLOADS_TMPL = "https://api.npmjs.org/downloads/point/last-month/{name}"
TREND_TMPL = "https://api.npmjs.org/downloads/range/last-year/{name}"


class NpmAdapter(Adapter):
    ecosystem = "npm"
    lockfile_names = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml")
    capabilities = AdapterCapabilities(
        downloads=True,
        dependents=False,
        owners=True,
        advisories=False,
        usage_method="npm download count for the last month",
    )
    pace_seconds = 0.08
    max_calls_per_package = 5

    def gather(self, client: CachingClient, name: str, version: str | None) -> PackageEvidence:
        evidence = self.new_evidence(name, version)
        url = PACKUMENT_TMPL.format(name=quote(name, safe="@"))
        evidence.registry_url = url
        try:
            # Packuments for big packages are megabytes; the TTL is short
            # because the newest release is the signal we care about.
            fetched = self.fetch(client, url, profile="npm", accept="application/json")
        except NotFound:
            evidence.add_gap("registry: package does not exist on npm")
            return evidence
        if fetched is None:
            evidence.add_gap("registry: npm did not answer")
            return evidence

        self._parse_packument(evidence, fetched, version)
        self._attach_downloads(client, evidence, name)
        return evidence

    # -- packument ---------------------------------------------------------

    def _parse_packument(
        self, evidence: PackageEvidence, fetched: Fetched, requested: str | None
    ) -> None:
        payload = fetched.payload or {}
        if not isinstance(payload, dict):
            evidence.add_gap("registry: unexpected packument shape")
            return
        retrieved = fetched.fetched_at
        times = payload.get("time") or {}
        versions = payload.get("versions") or {}

        evidence.registry_ok = True
        evidence.registry_retrieved_at = retrieved
        evidence.name = str(payload.get("name") or evidence.name)
        evidence.summary = payload.get("description") or None
        evidence.license = _license(payload)
        evidence.homepage = payload.get("homepage") or None
        from ..util import parse_github_repo

        evidence.repository = parse_github_repo(
            payload.get("repository"), payload.get("homepage"), payload.get("bugs")
        )

        points: list[ReleasePoint] = []
        for version, meta in versions.items():
            if not isinstance(meta, dict):
                continue
            when = parse_datetime(times.get(version))
            if when is None:
                continue
            points.append(
                ReleasePoint(
                    version=str(version),
                    published_at=when,
                    prerelease=looks_like_prerelease(str(version)),
                )
            )
        points.sort(key=lambda p: p.published_at)
        evidence.releases = points

        dist_tags = payload.get("dist-tags") or {}
        evidence.latest_version = str(dist_tags.get("latest") or "") or None
        audited_meta = versions.get(requested or evidence.latest_version or "") or {}
        deprecated = audited_meta.get("deprecated") if isinstance(audited_meta, dict) else None
        if deprecated:
            evidence.deprecated = True
            evidence.deprecation_message = str(deprecated)

        stable = evidence.stable_releases()
        last_publish = stable[-1].published_at if stable else None
        evidence.last_publish_obs = obs(
            iso(last_publish),
            source="npm",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="publish time of the newest non-prerelease version",
            method="max(time[version])",
        )
        if last_publish is None:
            evidence.add_gap("registry: no dated release in the packument")

        window_start = retrieved - timedelta(days=365)
        evidence.releases_12mo_obs = obs(
            sum(1 for point in stable if point.published_at >= window_start),
            source="npm",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="stable versions published in the 365 days before retrieval",
            method="count(time[version] >= now - 365d)",
        )
        evidence.open_issues_obs = obs(
            None,
            source="npm",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="npm exposes no issue-tracker data",
        )

        maintainers = payload.get("maintainers") or []
        people = [
            Maintainer(
                name=str(entry.get("name")),
                role="maintainer",
                url=f"https://www.npmjs.com/~{entry.get('name')}",
            )
            for entry in maintainers
            if isinstance(entry, dict) and entry.get("name")
        ]
        evidence.maintainers = people
        evidence.maintainer_count_obs = obs(
            len(people) if people else None,
            source="npm",
            url=fetched.url,
            retrieved_at=retrieved,
            detail="accounts listed in the packument's maintainers array",
            method="len(maintainers)",
        )
        if not people:
            evidence.add_gap("registry: packument lists no maintainers")

    # -- downloads ---------------------------------------------------------

    def _attach_downloads(self, client: CachingClient, evidence: PackageEvidence, name: str) -> None:
        url = DOWNLOADS_TMPL.format(name=quote(name, safe="@"))
        try:
            fetched = self.fetch(client, url, profile="npm-downloads")
        except NotFound:
            fetched = None
        downloaded = None
        if fetched is not None:
            count = (fetched.payload or {}).get("downloads")
            if isinstance(count, int):
                downloaded = obs(
                    count,
                    source="npm",
                    url=fetched.url,
                    retrieved_at=fetched.fetched_at,
                    detail="downloads in the last month",
                    method="downloads.downloads",
                )
                evidence.download_count_obs = downloaded
        else:
            evidence.add_gap("usage: npm download API did not answer")
        self.attach_usage(evidence, downloaded=downloaded, dependents=None)

    # trend is deliberately not fetched by default: it doubles the request
    # count for a number the rubric does not currently use.  Kept as a method
    # so a future rubric version can turn it on without touching the adapter
    # surface.
    def fetch_trend(self, client: CachingClient, name: str) -> Any:  # pragma: no cover
        url = TREND_TMPL.format(name=quote(name, safe="@"))
        fetched = self.fetch(client, url, profile="npm-downloads")
        if fetched is None:
            return None
        rows = (fetched.payload or {}).get("downloads") or []
        values = [int(row.get("downloads") or 0) for row in rows if isinstance(row, dict)]
        if len(values) < 4:
            return None
        return obs(
            values,
            source="npm",
            url=fetched.url,
            retrieved_at=fetched.fetched_at,
            detail="weekly downloads over the last year",
        )


def _license(payload: dict[str, Any]) -> str | None:
    value = payload.get("license")
    if isinstance(value, str) and value:
        return value
    if isinstance(value, dict) and value.get("type"):
        return str(value["type"])
    licenses = payload.get("licenses")
    if isinstance(licenses, list) and licenses:
        first = licenses[0]
        if isinstance(first, dict):
            return str(first.get("type") or "") or None
        return str(first)
    return None
