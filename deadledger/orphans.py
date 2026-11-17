"""The orphan simulation (Requirement 3).

For every *critical* package (direct, non-dev) we answer one question in one
line: **if this dies, who else uses it?**

The answer is an estimate with a named basis, because no registry publishes
"number of projects that depend on X" in a uniformly true way:

* crates.io publishes an exact reverse-dependency count -- we say "exact".
* npm and PyPI publish downloads.  Millions of monthly downloads mean you
  would not be alone in noticing; it does not mean N teams depend on it.  We
  say "approximate" and show the number with its basis.
* When a source gives us nothing, the line says "unknown" and the report
  treats that as a gap, never as zero.

The simulation also classifies *consequence*: whether an orphaned package
could be patched by the user (a small pure-python package), or whether it is
a binary/ABI/security problem.  That distinction is what an ADR actually needs.
"""

from __future__ import annotations

from dataclasses import dataclass

from .evidence import Observation, PackageEvidence
from .util import human_int

#: Download thresholds used only to *describe* ecosystem reach, never to
#: decide a verdict.  Kept here rather than in the rubric so that disagreement
#: about them cannot change a mortality verdict.
REACH_BANDS = (
    (10_000_000, "essentially universal"),
    (1_000_000, "very widely used"),
    (100_000, "widely used"),
    (10_000, "used across the ecosystem"),
    (1_000, "used by some projects"),
    (0, "niche"),
)


@dataclass
class OrphanAnswer:
    package: str
    ecosystem: str
    answer: str           # the one-line sentence
    reach_label: str      # 'exact' | 'approximate' | 'unknown'
    usage: int | None
    basis: str
    citation: str | None
    consequence: str
    solo_risk: str        # 'you would be alone' | 'many would share the pain' | 'unknown'


def simulate(evidence: PackageEvidence) -> OrphanAnswer:
    usage_obs: Observation[int] | None = evidence.usage_obs
    dependents_obs: Observation[int] | None = evidence.dependents_obs
    download_obs: Observation[int] | None = evidence.download_count_obs

    exact = dependents_obs is not None and dependents_obs.known and (
        dependents_obs.source.startswith("crates.io")
    )
    if exact and dependents_obs is not None:
        count = int(dependents_obs.value)  # type: ignore[arg-type]
        answer = (
            f"{count:,} crates depend on {evidence.name} directly "
            f"(exact count from crates.io)."
        )
        return OrphanAnswer(
            package=evidence.name,
            ecosystem=evidence.ecosystem,
            answer=answer,
            reach_label="exact",
            usage=count,
            basis=dependents_obs.detail or "crates.io reverse_dependencies",
            citation=dependents_obs.citation,
            consequence=_consequence(evidence),
            solo_risk=_solo(count),
        )

    if download_obs is not None and download_obs.known:
        count = int(download_obs.value)  # type: ignore[arg-type]
        band = _band(count)
        answer = (
            f"About {human_int(count)} downloads ({band}); if it dies you would "
            f"not be alone, but the number is a usage proxy, not a dependent count."
        )
        return OrphanAnswer(
            package=evidence.name,
            ecosystem=evidence.ecosystem,
            answer=answer,
            reach_label="approximate",
            usage=count,
            basis=download_obs.detail or "registry download count",
            citation=download_obs.citation,
            consequence=_consequence(evidence),
            solo_risk=_solo(count),
        )

    if usage_obs is not None and usage_obs.known:
        count = int(usage_obs.value)  # type: ignore[arg-type]
        return OrphanAnswer(
            package=evidence.name,
            ecosystem=evidence.ecosystem,
            answer=(
                f"About {human_int(count)} files contain it "
                f"({usage_obs.source}); an approximate reach signal only."
            ),
            reach_label="approximate",
            usage=count,
            basis=usage_obs.detail or usage_obs.source,
            citation=usage_obs.citation,
            consequence=_consequence(evidence),
            solo_risk=_solo(count),
        )

    # Quote only the gaps that are actually about usage, not whatever happened
    # to be last in the list.
    usage_gaps = [gap for gap in evidence.source_gaps if gap.startswith("usage:")]
    return OrphanAnswer(
        package=evidence.name,
        ecosystem=evidence.ecosystem,
        answer="no source published a usage or dependent count.",
        reach_label="unknown",
        usage=None,
        basis="; ".join(usage_gaps) or "no usage source was queried",
        citation=None,
        consequence=_consequence(evidence),
        solo_risk="unknown",
    )


def _band(count: int) -> str:
    for threshold, label in REACH_BANDS:
        if count >= threshold:
            return label
    return "niche"


def _solo(count: int) -> str:
    if count >= 100_000:
        return "many would share the pain"
    if count >= 1_000:
        return "a community would share the pain"
    return "you would likely be alone"


def _consequence(evidence: PackageEvidence) -> str:
    """What actually breaks for *you* when this package stops being fixed."""
    if evidence.ecosystem == "pypi":
        return "pure-python packages can usually be forked or vendored in an afternoon"
    if evidence.ecosystem == "npm":
        return "source is fetched at install time, so a fork can be pinned via overrides"
    if evidence.ecosystem == "crates":
        return "vendoring is supported natively (cargo vendor), but FFI/bindings may need patching"
    return "unknown consequences for this ecosystem"
