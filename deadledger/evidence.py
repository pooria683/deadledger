"""The evidence contract.

Every number the mortality engine uses arrives as an :class:`Observation`
carrying its own citation.  That is the whole trick behind requirement 4
("no score without its source"): it is *impossible* to compute a verdict from
a number that does not know where it came from, because the verdict function
only accepts ``Observation``s.

An adapter's job is to turn registry payloads into one :class:`PackageEvidence`.
Adapters never decide anything; they collect.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Generic, Iterable, TypeVar

from .util import iso, iso_day

T = TypeVar("T")


@dataclass(frozen=True)
class Observation(Generic[T]):
    """One fact, where it came from, and when we looked.

    ``value`` may be ``None`` to record "we asked and the source had nothing"
    -- which is itself a fact the rubric treats as a source gap, not a zero.
    """

    value: T | None
    source: str
    url: str
    retrieved_at: datetime
    detail: str | None = None
    #: Free-form provenance (pagination counts, how a number was derived).
    method: str | None = None

    @property
    def known(self) -> bool:
        return self.value is not None

    @property
    def citation(self) -> str:
        return f"{self.url} (retrieved {iso(self.retrieved_at)})"

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "url": self.url,
            "retrieved_at": iso(self.retrieved_at),
            "detail": self.detail,
            "method": self.method,
        }


def obs(
    value: T | None,
    *,
    source: str,
    url: str,
    retrieved_at: datetime,
    detail: str | None = None,
    method: str | None = None,
) -> Observation[T]:
    """Convenience constructor; keeps adapter code readable."""
    return Observation(
        value=value,
        source=source,
        url=url,
        retrieved_at=retrieved_at,
        detail=detail,
        method=method,
    )


@dataclass
class ReleasePoint:
    """One published version.  ``prerelease``/``yanked`` are excluded upstream."""

    version: str
    published_at: datetime
    prerelease: bool = False
    yanked: bool = False


@dataclass
class Maintainer:
    """A person (or org) with publish rights."""

    name: str
    role: str = "maintainer"
    url: str | None = None
    #: For GitHub-sourced committers: SHA of their most recent commit, so the
    #: report can cite a specific commit rather than a vague "recently".
    last_commit_sha: str | None = None
    last_commit_at: datetime | None = None
    commits: int | None = None


@dataclass
class PackageEvidence:
    """Everything we know about one package, all of it cited.

    Field naming: ``*_obs`` fields are :class:`Observation`s (fact + citation);
    the plain fields are structural facts gathered while parsing (e.g. the list
    of releases) whose citation is the packument URL recorded in
    ``registry_url``.
    """

    # -- identity ----------------------------------------------------------
    ecosystem: str
    name: str
    version: str | None = None
    summary: str | None = None
    homepage: str | None = None
    repository: str | None = None
    license: str | None = None

    # -- registry facts ----------------------------------------------------
    registry_url: str = ""
    registry_retrieved_at: datetime | None = None
    releases: list[ReleasePoint] = field(default_factory=list)
    maintainers: list[Maintainer] = field(default_factory=list)
    latest_version: str | None = None
    registry_ok: bool = False
    deprecated: bool = False
    deprecation_message: str | None = None

    # -- registry observations --------------------------------------------
    last_publish_obs: Observation[str] | None = None
    maintainer_count_obs: Observation[int] | None = None
    releases_12mo_obs: Observation[int] | None = None
    open_issues_obs: Observation[int] | None = None
    download_count_obs: Observation[int] | None = None
    download_trend_obs: Observation[float] | None = None
    dependents_obs: Observation[int] | None = None
    usage_obs: Observation[int] | None = None
    advisory_obs: Observation[int] | None = None

    # -- forge facts (GitHub today) ----------------------------------------
    repo: str | None = None
    repo_url: str | None = None
    repo_archived: bool = False
    forge_ok: bool = False
    last_commit_obs: Observation[str] | None = None
    commits_12mo_obs: Observation[int] | None = None
    committers_12mo_obs: Observation[int] | None = None
    last_commit_by_author_obs: Observation[str] | None = None
    top_committer_share_obs: Observation[float] | None = None
    issue_created_12mo_obs: Observation[int] | None = None
    issue_closed_12mo_obs: Observation[int] | None = None
    triage_rate_obs: Observation[float] | None = None
    committers: list[Maintainer] = field(default_factory=list)

    # -- bookkeeping -------------------------------------------------------
    advisories: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_gaps: list[str] = field(default_factory=list)

    # -- derived helpers ---------------------------------------------------

    def add_gap(self, reason: str) -> None:
        if reason not in self.source_gaps:
            self.source_gaps.append(reason)

    def stable_releases(self) -> list[ReleasePoint]:
        """Releases we trust as "shipped something": no prereleases, no yanks."""
        return [r for r in self.releases if not r.prerelease and not r.yanked]

    def observation_map(self) -> dict[str, Observation[Any]]:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name.endswith("_obs") and getattr(self, f.name) is not None
        }

    def evidence_rows(self) -> list[dict[str, Any]]:
        """Flatten to ``{claim, value, age, citation}`` for tabular output."""
        rows = []
        for name, observation in self.observation_map().items():
            rows.append(
                {
                    "metric": name.removesuffix("_obs"),
                    "value": observation.value,
                    "source": observation.source,
                    "citation": observation.citation,
                    "detail": observation.detail,
                    "method": observation.method,
                }
            )
        return rows

    def fingerprint(self) -> dict[str, Any]:
        """Inputs that determine the verdict (used by determinism tests)."""
        payload: dict[str, Any] = {
            "ecosystem": self.ecosystem,
            "name": self.name,
            "releases": [
                [r.version, iso(r.published_at)] for r in self.releases if not r.yanked
            ],
            "deprecated": self.deprecated,
            "archived": self.repo_archived,
        }
        for name, observation in sorted(self.observation_map().items()):
            payload[name] = observation.value
        return payload


def cited_date(observation: Observation[str] | None) -> str | None:
    """Render a date-valued observation for prose (``2023-06-01``)."""
    if not observation or observation.value is None:
        return None
    from .util import parse_datetime

    parsed = parse_datetime(observation.value)
    return iso_day(parsed) if parsed else str(observation.value)


def collect_gaps(evidence: Iterable[PackageEvidence]) -> list[str]:
    gaps: list[str] = []
    for item in evidence:
        for gap in item.source_gaps:
            label = f"{item.ecosystem}:{item.name} — {gap}"
            if label not in gaps:
                gaps.append(label)
    return gaps
