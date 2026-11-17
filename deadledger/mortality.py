"""The rubric, as code.  Version: 1.0  (see docs/verdicts.md)

Design rules, all of them consequences of Requirement 4 ("no score without
its source"):

1. **Every rule that contributes to a verdict returns a :class:`RuleHit` with
   the evidence that fired it.**  Rules live in a registry keyed by a stable
   ``rule_id``; the report prints ids so a reader can look them up in
   docs/verdicts.md and disagree with a specific rule rather than with a
   number.
2. **Unknown is not dead.**  Missing evidence never counts against a package.
   A package with no releases *and* no readable repo is ``unknown``, not
   ``dead`` -- it might be a private mirror, a rename, or a rate limit.
3. **Death signals outrank life signals.**  An archived repository or an
   explicit deprecation is a statement by the maintainers; it cannot be
   outweighed by historical download volume.  This ordering is what makes a
   verdict defensible in an ADR.
4. **Determinism.**  The only clock consulted is the ``now`` passed in (which
   the runner takes from the newest citation).  Rules never call
   ``datetime.now()``, never read the environment, and never iterate a set in
   an order-dependent way.

The four verdicts:

===========  ==============================================================
thriving     alive, and there is current evidence of maintenance activity
coasting     alive but quiet: no *death* signal, and the activity thresholds
             are not met.  "Nobody is actively tending this, but it works."
dormant      a death signal (archive/deprecation) or no release for the
             dormant threshold, while nothing suggests it is coming back
dead         an explicit death signal: archived repository, yanked/deprecated
             project, or no release for the dead threshold
===========  ==============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Iterable

from . import RUBRIC_VERSION
from .evidence import Observation, PackageEvidence
from .util import age_in_days, human_age, human_int, iso_day, parse_datetime

THRIVING = "thriving"
COASTING = "coasting"
DORMANT = "dormant"
DEAD = "dead"
UNKNOWN = "unknown"

VERDICTS = (THRIVING, COASTING, DORMANT, DEAD, UNKNOWN)
#: Worst-first ordering, used for report sorting and CI exit codes.
SEVERITY = {THRIVING: 0, COASTING: 1, DORMANT: 2, DEAD: 3, UNKNOWN: 1}

#: The thresholds, in one place, so docs/verdicts.md and the code cannot drift.
#: Changing any value here is a rubric version bump (docs/rubric-changelog.md).
THRESHOLDS: dict[str, Any] = {
    # age of the most recent stable release
    "dormant_after_days": 730,          # 2 years: dormant
    "dead_after_days": 1460,            # 4 years: dead
    # current activity
    "thriving_releases_12mo": 2,
    "thriving_commits_12mo": 12,
    "thriving_last_commit_days": 90,
    "thriving_maintainers": 2,
    # supporting signals (never sufficient alone)
    "healthy_bus_factor": 3,
    "single_maintainer": 1,
    "low_triage_rate": 0.35,
    "inactive_committer_days": 365,
    # If the repository moved *after* the last release, the project is not
    # dead, it stopped publishing. That is a different conversation (fork from
    # main, pin a git SHA) and the rubric has to say so or it will libel a
    # maintainer who is still working.
    "development_without_release_days": 90,
}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleHit:
    """One piece of reasoning, with the evidence that produced it."""

    rule_id: str
    verdict: str
    claim: str
    citations: tuple[str, ...] = ()
    metrics: tuple[tuple[str, Any], ...] = ()

    @property
    def metric_map(self) -> dict[str, Any]:
        return dict(self.metrics)


@dataclass
class Verdict:
    verdict: str
    confidence: str  # "high" | "medium" | "low"
    rules: list[RuleHit] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    rubric_version: str = RUBRIC_VERSION
    as_of: datetime | None = None

    @property
    def rule_ids(self) -> list[str]:
        return [hit.rule_id for hit in self.rules]

    def claims(self) -> list[str]:
        return [hit.claim for hit in self.rules]

    def citations(self) -> list[str]:
        seen: list[str] = []
        for hit in self.rules:
            for citation in hit.citations:
                if citation not in seen:
                    seen.append(citation)
        return seen


@dataclass
class PackageMetrics:
    """The derived quantities the rubric reasons over.  All may be ``None``."""

    last_release_at: datetime | None
    last_release_age_days: int | None
    last_commit_at: datetime | None
    last_commit_age_days: int | None
    releases_12mo: int | None
    commits_12mo: int | None
    committers_12mo: int | None
    maintainers: int | None
    triage_rate: float | None
    lead_committer: str | None
    lead_committer_last_activity: datetime | None
    lead_committer_share: float | None
    archived: bool
    deprecated: bool
    downloads: int | None
    dependents: int | None
    usage: int | None

    @property
    def top_actor(self) -> str | None:
        """Who is keeping this alive: lead committer, else a maintainer name."""
        return self.lead_committer


# ---------------------------------------------------------------------------
# Metric derivation (pure)
# ---------------------------------------------------------------------------


def _when(observation: Observation[Any] | None) -> datetime | None:
    if observation is None or observation.value is None:
        return None
    return parse_datetime(observation.value)


def derive_metrics(evidence: PackageEvidence, now: datetime) -> PackageMetrics:
    lead = evidence.committers[0] if evidence.committers else None
    last_release = _when(evidence.last_publish_obs)
    last_commit = _when(evidence.last_commit_obs)
    return PackageMetrics(
        last_release_at=last_release,
        last_release_age_days=age_in_days(last_release, now),
        last_commit_at=last_commit,
        last_commit_age_days=age_in_days(last_commit, now),
        releases_12mo=_value(evidence.releases_12mo_obs),
        commits_12mo=_value(evidence.commits_12mo_obs),
        committers_12mo=_value(evidence.committers_12mo_obs),
        maintainers=_value(evidence.maintainer_count_obs),
        triage_rate=_value(evidence.triage_rate_obs),
        lead_committer=lead.name if lead else None,
        lead_committer_last_activity=lead.last_commit_at if lead else None,
        lead_committer_share=_value(evidence.top_committer_share_obs),
        archived=bool(evidence.repo_archived),
        deprecated=bool(evidence.deprecated),
        downloads=_value(evidence.download_count_obs),
        dependents=_value(evidence.dependents_obs),
        usage=_value(evidence.usage_obs),
    )


def _value(observation: Observation[Any] | None) -> Any:
    return None if observation is None else observation.value


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

#: Each rule takes (evidence, metrics, now) and returns RuleHits.
RuleFn = Callable[[PackageEvidence, PackageMetrics, datetime], Iterable[RuleHit]]


def rule_archived(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    if not metrics.archived:
        return ()
    citation = _citation(evidence.last_commit_obs) or evidence.repo_url or ""
    return (
        RuleHit(
            rule_id="R-ARCHIVED",
            verdict=DEAD,
            claim=(
                f"The repository {evidence.repo or ''} is archived, so no further "
                f"commits or releases can land without a deliberate revival."
            ).replace("  ", " "),
            citations=(citation,) if citation else (),
            metrics=(("archived", True),),
        ),
    )


def rule_deprecated(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    if not metrics.deprecated:
        return ()
    detail = evidence.deprecation_message or "the registry marks this package deprecated"
    citation = _citation(evidence.last_publish_obs)
    return (
        RuleHit(
            rule_id="R-DEPRECATED",
            verdict=DEAD,
            claim=f"The package is deprecated: {detail}.",
            citations=(citation,) if citation else (),
            metrics=(("deprecated", True),),
        ),
    )


def rule_registry_missing(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """The registry answered 404: the name no longer exists there."""
    if evidence.registry_ok or not evidence.source_gaps:
        return ()
    if "registry: package does not exist on PyPI" not in evidence.source_gaps:
        return ()
    return (
        RuleHit(
            rule_id="R-REGISTRY-404",
            verdict=DEAD,
            claim="The package name no longer resolves in the registry.",
            citations=(evidence.registry_url,),
        ),
    )


def rule_release_age(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    age = metrics.last_release_age_days
    if age is None:
        return ()
    citation = _citation(evidence.last_publish_obs)
    when = iso_day(metrics.last_release_at)
    if age >= THRESHOLDS["dead_after_days"]:
        return (
            RuleHit(
                rule_id="R-NO-RELEASE-DEAD",
                verdict=DEAD,
                claim=(
                    f"The newest stable release is {human_age(age)} old ({when}); "
                    f"nothing has shipped in {THRESHOLDS['dead_after_days'] // 365}+ years."
                ),
                citations=(citation,) if citation else (),
                metrics=(("last_release_age_days", age),),
            ),
        )
    if age >= THRESHOLDS["dormant_after_days"]:
        return (
            RuleHit(
                rule_id="R-NO-RELEASE-DORMANT",
                verdict=DORMANT,
                claim=(
                    f"The newest stable release is {human_age(age)} old ({when}); "
                    f"the project has not published for two years."
                ),
                citations=(citation,) if citation else (),
                metrics=(("last_release_age_days", age),),
            ),
        )
    return ()


def rule_development_without_release(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """Commits after the last release: alive, but not publishing.

    This is the most common false positive a naive "old release date" rubric
    produces.  If the repository saw non-bot commits in the last year and the
    last commit is newer than the last release, the project is not abandoned:
    the code is moving, the releases are not.

    The rule does **not** decide the verdict.  A project that ships once every
    eighteen months and commits every week is not dying -- PyYAML and
    django-cors-headers are exactly that shape, and calling them dead would
    destroy the report's credibility in one paragraph.  What this rule changes
    is the *remedy*: "pin a git ref or ask for a release" instead of "migrate".
    Only the release-age rules (730/1460 days) get to call a package dormant or
    dead.

    It does soften a four-year-old release from `dead` to `dormant` when the
    repository is still moving, because a consumer can still obtain fixes by
    pinning a commit -- see ``_decide``.
    """
    release_at = metrics.last_release_at
    commit_at = metrics.last_commit_at
    if release_at is None or commit_at is None:
        return ()
    if metrics.archived or metrics.deprecated:
        return ()
    # The *only* thing that makes "still developing, not publishing" true is
    # that publication has stopped: zero releases in the last year.  A project
    # that shipped twice this year and committed this morning is thriving, no
    # matter how many days separate its last release from its last commit.
    # (An earlier version of this rule used that gap alone and libelled
    # requests, which is exactly the false positive this comment exists to
    # prevent.)
    releases = metrics.releases_12mo
    if releases is None or releases > 0:
        return ()
    if metrics.last_release_age_days is None or (
        metrics.last_release_age_days < THRESHOLDS["dormant_after_days"] // 4
    ):
        return ()
    commits = metrics.commits_12mo
    if commits is None or commits <= 0:
        return ()
    gap = (commit_at - release_at).days
    if gap < THRESHOLDS["development_without_release_days"]:
        return ()
    who = metrics.lead_committer or "the maintainers"
    return (
        RuleHit(
            rule_id="R-DEVELOP-WITHOUT-RELEASE",
            verdict=COASTING,
            claim=(
                f"The repository is still moving ({commits} commit(s) in the last year, "
                f"latest by {who} on {iso_day(commit_at)}) but the newest release is "
                f"{human_age(metrics.last_release_age_days)} old: development continues "
                f"without publishing."
            ),
            citations=_dedupe(
                _citation(evidence.last_publish_obs),
                _citation(evidence.last_commit_obs),
            ),
            metrics=(
                ("commits_12mo", commits),
                ("days_commits_after_release", gap),
            ),
        ),
    )


def rule_thriving(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """Live evidence of maintenance.  Requires shipping *and* some activity."""
    hits: list[RuleHit] = []
    releases = metrics.releases_12mo
    commits = metrics.commits_12mo
    last_commit_age = metrics.last_commit_age_days
    committers = metrics.committers_12mo

    shipped = releases is not None and releases >= THRESHOLDS["thriving_releases_12mo"]
    moving = (
        commits is not None and commits >= THRESHOLDS["thriving_commits_12mo"]
    ) or (
        last_commit_age is not None
        and last_commit_age <= THRESHOLDS["thriving_last_commit_days"]
    )

    if not (shipped and moving):
        return ()
    # A single committer is not disqualifying, but it is the difference
    # between "thriving" and "thriving, fragile" -- recorded as a separate hit.
    fragility = (
        committers is not None
        and committers <= THRESHOLDS["single_maintainer"]
    )
    citations = _dedupe(
        _citation(evidence.releases_12mo_obs),
        _citation(evidence.last_commit_obs),
        _citation(evidence.commits_12mo_obs),
    )
    detail = []
    if releases is not None:
        detail.append(f"{releases} release(s) in 12 months")
    if commits is not None:
        detail.append(f"{commits} commit(s) in 12 months")
    if last_commit_age is not None:
        detail.append(f"last commit {human_age(last_commit_age)} ago")
    hits.append(
        RuleHit(
            rule_id="R-THRIVING",
            verdict=THRIVING,
            claim="Actively maintained: " + ", ".join(detail) + ".",
            citations=citations,
            metrics=(
                ("releases_12mo", releases),
                ("commits_12mo", commits),
                ("last_commit_age_days", last_commit_age),
            ),
        )
    )
    if fragility:
        hits.append(
            RuleHit(
                rule_id="R-FRAGILE-THRIVING",
                verdict=THRIVING,
                claim=(
                    f"Only {committers} person commits to it, so the project is "
                    f"thriving on a single pair of hands."
                ),
                citations=_dedupe(_citation(evidence.committers_12mo_obs)),
                metrics=(("committers_12mo", committers),),
            )
        )
    return hits


def rule_single_maintainer(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """Requirement 2: flag single maintainers *explicitly*, with a date."""
    hits: list[RuleHit] = []
    committers = metrics.committers_12mo
    maintainers = metrics.maintainers
    if committers == THRESHOLDS["single_maintainer"]:
        who = metrics.lead_committer or "one account"
        last = metrics.lead_committer_last_activity
        seen = iso_day(last) if last else None
        age = age_in_days(last, now)
        claim = f"Exactly one person has committed in the last year ({who}"
        if seen:
            claim += f", last commit {seen} — {human_age(age)} ago"
        claim += ")."
        hits.append(
            RuleHit(
                rule_id="R-BUS-ONE",
                verdict=DORMANT if _stale(age) else COASTING,
                claim=claim,
                citations=_dedupe(
                    _citation(evidence.committers_12mo_obs),
                    _citation(evidence.last_commit_by_author_obs),
                ),
                metrics=(
                    ("committers_12mo", committers),
                    ("lead_committer_last_activity", seen),
                    ("lead_committer_last_activity_days", age),
                ),
            )
        )
    elif maintainers == THRESHOLDS["single_maintainer"] and committers is None:
        names = ", ".join(m.name for m in evidence.maintainers) or "one account"
        hits.append(
            RuleHit(
                rule_id="R-BUS-ONE-REGISTRY",
                verdict=COASTING,
                claim=f"The registry lists a single owner ({names}); the forge was not readable.",
                citations=_dedupe(_citation(evidence.maintainer_count_obs)),
                metrics=(("maintainers", maintainers),),
            )
        )
    return hits


def _stale(age_days: int | None) -> bool:
    return age_days is not None and age_days > THRESHOLDS["inactive_committer_days"]


def rule_bus_factor_risk(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """Low bus factor with a dominant committer share.  Support, never a verdict."""
    committers = metrics.committers_12mo
    share = metrics.lead_committer_share
    if committers is None or share is None:
        return ()
    if committers > 1 and share >= 0.9:
        lead = metrics.lead_committer or "one account"
        return (
            RuleHit(
                rule_id="R-BUS-CONCENTRATED",
                verdict=COASTING,
                claim=(
                    f"{lead} authored {share:.0%} of last year's commits "
                    f"({committers} committers in total)."
                ),
                citations=_dedupe(_citation(evidence.top_committer_share_obs)),
                metrics=(("committers_12mo", committers), ("lead_committer_share", share)),
            ),
        )
    return ()


def rule_triage(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    rate = metrics.triage_rate
    if rate is None or rate > THRESHOLDS["low_triage_rate"]:
        return ()
    created = _value(evidence.issue_created_12mo_obs)
    closed = _value(evidence.issue_closed_12mo_obs)
    return (
        RuleHit(
            rule_id="R-TRIAGE-LOW",
            verdict=COASTING,
            claim=(
                f"Only {rate:.0%} of issues opened in the last year were closed "
                f"({closed} of {created}); inbound reports are piling up."
            ),
            citations=_dedupe(_citation(evidence.triage_rate_obs)),
            metrics=(("triage_rate", rate), ("issues_created_12mo", created)),
        ),
    )


def rule_advisories(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    count = _value(evidence.advisory_obs)
    if not count:
        return ()
    return (
        RuleHit(
            rule_id="R-ADVISORIES",
            verdict=COASTING,
            claim=f"{count} published security advisory(ies) affect the audited version.",
            citations=_dedupe(_citation(evidence.advisory_obs)),
            metrics=(("advisories", count),),
        ),
    )


def rule_quiet_default(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """The coasting default, stated with numbers instead of left implicit.

    Requirement 4 forbids a score without its source, and "coasting" is a
    score.  When no deciding rule fires we say so in a sentence that carries the
    observations behind it: what shipped, how long ago, and what the repository
    looked like.  This rule never *decides* anything -- ``_decide`` only uses it
    as the fallback -- it exists so the fallback has a citation.
    """
    if metrics.last_release_age_days is None:
        return ()
    pieces: list[str] = []
    if metrics.last_release_age_days is not None:
        pieces.append(
            f"last stable release {human_age(metrics.last_release_age_days)} ago"
            + (f" ({iso_day(metrics.last_release_at)})" if metrics.last_release_at else "")
        )
    if metrics.releases_12mo is not None:
        pieces.append(f"{metrics.releases_12mo} release(s) in the last year")
    if metrics.commits_12mo is not None:
        pieces.append(f"{metrics.commits_12mo} commit(s) in the last year")
    elif metrics.committers_12mo is None and not evidence.forge_ok:
        pieces.append("repository history unavailable")
    if metrics.maintainers is not None:
        pieces.append(f"{metrics.maintainers} registry maintainer(s)")
    claim = "No death signal fired: " + "; ".join(pieces) + "."
    return (
        RuleHit(
            rule_id="R-QUIET-DEFAULT",
            verdict=COASTING,
            claim=claim,
            citations=_dedupe(
                _citation(evidence.last_publish_obs),
                _citation(evidence.last_commit_obs),
                _citation(evidence.maintainer_count_obs),
            ),
            metrics=(
                ("last_release_age_days", metrics.last_release_age_days),
                ("releases_12mo", metrics.releases_12mo),
                ("commits_12mo", metrics.commits_12mo),
            ),
        ),
    )


def rule_no_release_history(
    evidence: PackageEvidence, metrics: PackageMetrics, now: datetime
) -> Iterable[RuleHit]:
    """Nothing to reason from: say so instead of guessing a verdict."""
    if metrics.last_release_age_days is not None:
        return ()
    return (
        RuleHit(
            rule_id="R-NO-EVIDENCE",
            verdict=UNKNOWN,
            claim="No released version could be observed, so no verdict is offered.",
            citations=_dedupe(evidence.registry_url),
        ),
    )


RULES: tuple[tuple[str, RuleFn], ...] = (
    ("R-ARCHIVED", rule_archived),
    ("R-DEPRECATED", rule_deprecated),
    ("R-REGISTRY-404", rule_registry_missing),
    ("R-NO-RELEASE-DEAD", rule_release_age),
    ("R-DEVELOP-WITHOUT-RELEASE", rule_development_without_release),
    ("R-THRIVING", rule_thriving),
    ("R-BUS-ONE", rule_single_maintainer),
    ("R-BUS-CONCENTRATED", rule_bus_factor_risk),
    ("R-TRIAGE-LOW", rule_triage),
    ("R-ADVISORIES", rule_advisories),
    ("R-QUIET-DEFAULT", rule_quiet_default),
    ("R-NO-EVIDENCE", rule_no_release_history),
)

#: Rules that can *cause* the verdict they name.  Everything else is support:
#: it contributes a claim, and may be listed under "what to do", but cannot
#: decide a verdict on its own.
#:
#: Bus factor deliberately lives outside this set.  "One person maintains it"
#: is a concentration *risk*, not evidence of mortality: many excellent
#: packages have a single maintainer, and a tool that calls them all dead is
#: ignored within a week.  The risk is reported as its own section.
DECIDING_RULES = {
    "R-ARCHIVED",
    "R-DEPRECATED",
    "R-REGISTRY-404",
    "R-NO-RELEASE-DEAD",
    "R-NO-RELEASE-DORMANT",
    "R-THRIVING",
    "R-NO-EVIDENCE",
}


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate(evidence: PackageEvidence, *, now: datetime) -> Verdict:
    """Apply the rubric.  Pure: same evidence + same ``now`` -> same verdict."""
    metrics = derive_metrics(evidence, now)
    all_hits: list[RuleHit] = []
    for _, rule in RULES:
        for hit in rule(evidence, metrics, now):
            all_hits.append(hit)

    deciding = [hit for hit in all_hits if hit.rule_id in DECIDING_RULES]
    verdict, used_default = _decide(
        deciding,
        all_hits,
        metrics,
        [hit for hit in all_hits if hit.rule_id not in DECIDING_RULES],
    )
    support = [
        hit
        for hit in all_hits
        if hit.rule_id not in DECIDING_RULES
        and not (hit.rule_id == "R-QUIET-DEFAULT" and not used_default)
    ]

    reasons = [hit.claim for hit in deciding] + [hit.claim for hit in support]
    gaps = list(evidence.source_gaps)
    if used_default and not any(hit.rule_id == "R-QUIET-DEFAULT" for hit in support):
        gaps.append("no deciding evidence: the verdict is the quiet default")
    return Verdict(
        verdict=verdict,
        confidence=_confidence(verdict, used_default, gaps, deciding),
        rules=_dedupe_hits(deciding + support),
        reasons=reasons,
        evidence_gaps=gaps,
        as_of=now,
    )


def _decide(
    deciding: list[RuleHit],
    all_hits: list[RuleHit],
    metrics: PackageMetrics,
    supporting: list[RuleHit] | None = None,
) -> tuple[str, bool]:
    seen = {hit.verdict for hit in deciding}
    if UNKNOWN in seen:
        return UNKNOWN, False
    if DEAD in seen:
        # One exception, and it is a deliberate one: an old release date plus a
        # live repository is "not shipping", not "dead".  Explicit death
        # signals (archive, deprecation) always win.
        explicit_death = any(
            hit.rule_id in {"R-ARCHIVED", "R-DEPRECATED", "R-REGISTRY-404"}
            for hit in deciding
        )
        developing = any(
            hit.rule_id == "R-DEVELOP-WITHOUT-RELEASE" for hit in supporting
        )
        if developing and not explicit_death:
            return DORMANT, False
        return DEAD, False
    if DORMANT in seen:
        return DORMANT, False
    if THRIVING in seen:
        return THRIVING, False
    # Nothing decisive fired: the package is quiet, not dead.  Coasting is the
    # honest answer for "alive, shipping occasionally, nobody is watching".
    return COASTING, True


def _confidence(
    verdict: str, used_default: bool, gaps: list[str], deciding: list[RuleHit]
) -> str:
    if used_default:
        return "low"
    if verdict == UNKNOWN:
        return "low"
    forge_gaps = [g for g in gaps if g.startswith(("forge:", "commits:", "triage:"))]
    if forge_gaps:
        return "medium"
    return "high"


def _citation(observation: Observation[Any] | None) -> str | None:
    return observation.citation if observation is not None else None


def _dedupe(*values: str | None) -> tuple[str, ...]:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return tuple(out)


def _dedupe_hits(hits: list[RuleHit]) -> list[RuleHit]:
    seen: set[str] = set()
    out: list[RuleHit] = []
    for hit in hits:
        if hit.rule_id in seen:
            continue
        seen.add(hit.rule_id)
        out.append(hit)
    return out


# ---------------------------------------------------------------------------
# Bus factor (requirement 2), separated from verdicting
# ---------------------------------------------------------------------------


@dataclass
class BusFactor:
    committers_12mo: int | None
    lead: str | None
    lead_last_activity: datetime | None
    lead_share: float | None
    single_maintainer: bool
    citations: list[str] = field(default_factory=list)

    def sentence(self) -> str:
        if self.committers_12mo is None:
            return "Bus factor unknown: no readable commit history."
        if self.single_maintainer:
            lead = self.lead or "one account"
            if self.lead_last_activity:
                return (
                    f"Bus factor 1 — {lead} is the only committer in the last 12 "
                    f"months (last commit {iso_day(self.lead_last_activity)}). "
                    f"If they stop, this stops."
                )
            return f"Bus factor 1 — {lead} is the only committer in the last 12 months."
        return (
            f"Bus factor {self.committers_12mo}: {self.committers_12mo} distinct "
            f"committers in the last 12 months"
            + (f", led by {self.lead}." if self.lead else ".")
        )


def bus_factor(evidence: PackageEvidence, *, now: datetime) -> BusFactor:
    metrics = derive_metrics(evidence, now)
    lead = evidence.committers[0] if evidence.committers else None
    citations = _dedupe(
        _citation(evidence.committers_12mo_obs),
        _citation(evidence.last_commit_by_author_obs),
    )
    return BusFactor(
        committers_12mo=metrics.committers_12mo,
        lead=lead.name if lead else None,
        lead_last_activity=lead.last_commit_at if lead else None,
        lead_share=metrics.lead_committer_share,
        single_maintainer=metrics.committers_12mo == THRESHOLDS["single_maintainer"],
        citations=list(citations),
    )
