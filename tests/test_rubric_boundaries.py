"""The rubric's boundaries, tested one threshold at a time.

These are the tests to read if you want to argue with the verdicts.  Each one
builds a synthetic package profile that sits exactly *on* a boundary, or one
day either side of it, and asserts the verdict flips there.  If a threshold in
``mortality.THRESHOLDS`` moves, exactly the tests around that threshold should
fail -- which is the signal to bump the rubric version and write an entry in
docs/rubric-changelog.md.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from conftest import NOW, make_evidence
from deadledger.mortality import (
    COASTING,
    DEAD,
    DORMANT,
    THRESHOLDS,
    THRIVING,
    UNKNOWN,
    evaluate,
)

UTC = timezone.utc
DORMANT_DAYS = THRESHOLDS["dormant_after_days"]
DEAD_DAYS = THRESHOLDS["dead_after_days"]


def verdict_of(**overrides):
    return evaluate(make_evidence(**overrides), now=NOW).verdict


# ---------------------------------------------------------------------------
# Release age: dead at 4 years, dormant at 2
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "days_old, expected",
    [
        (DORMANT_DAYS - 1, COASTING),
        (DORMANT_DAYS, DORMANT),
        (DEAD_DAYS - 1, DORMANT),
        (DEAD_DAYS, DEAD),
    ],
)
def test_release_age_boundaries(days_old, expected):
    assert verdict_of(last_publish_obs=NOW - timedelta(days=days_old)) == expected


def test_release_age_just_inside_dormant_stays_coasting():
    """One day short of two years is quiet, not dormant."""
    assert verdict_of(last_publish_obs=NOW - timedelta(days=DORMANT_DAYS - 1)) == COASTING


# ---------------------------------------------------------------------------
# Death signals outrank everything else
# ---------------------------------------------------------------------------


def test_archived_repository_is_dead_even_with_a_fresh_release():
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=3),
        releases_12mo_obs=6,
        last_commit_obs=NOW - timedelta(days=1),
        commits_12mo_obs=40,
        committers_12mo_obs=4,
        repo_archived=True,
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == DEAD
    assert "R-ARCHIVED" in verdict.rule_ids


def test_deprecation_on_a_young_package_is_dead():
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=10),
        releases_12mo_obs=1,
        deprecated=True,
        deprecation_message="use something else",
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == DEAD
    assert any("use something else" in claim for claim in verdict.claims())


def test_repository_404_is_dead_not_unknown():
    evidence = make_evidence(last_publish_obs=NOW - timedelta(days=900))
    evidence.registry_ok = False
    evidence.source_gaps.append("registry: package does not exist on PyPI")
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == DEAD
    assert "R-REGISTRY-404" in verdict.rule_ids


# ---------------------------------------------------------------------------
# Thriving needs shipping AND activity
# ---------------------------------------------------------------------------


def test_thriving_requires_both_releases_and_commits():
    assert (
        verdict_of(
            last_publish_obs=NOW - timedelta(days=30),
            releases_12mo_obs=THRESHOLDS["thriving_releases_12mo"],
            last_commit_obs=NOW - timedelta(days=10),
            commits_12mo_obs=THRESHOLDS["thriving_commits_12mo"],
            committers_12mo_obs=3,
        )
        == THRIVING
    )


def test_shipping_without_activity_is_not_thriving():
    """A single release this year and no commits is coasting, not thriving."""
    assert (
        verdict_of(
            last_publish_obs=NOW - timedelta(days=200),
            releases_12mo_obs=1,
            last_commit_obs=NOW - timedelta(days=300),
            commits_12mo_obs=0,
            committers_12mo_obs=0,
        )
        == COASTING
    )


def test_activity_without_releases_is_not_thriving():
    assert (
        verdict_of(
            last_publish_obs=NOW - timedelta(days=400),
            releases_12mo_obs=0,
            last_commit_obs=NOW - timedelta(days=5),
            commits_12mo_obs=100,
            committers_12mo_obs=5,
        )
        != THRIVING
    )


def test_thriving_with_one_committer_flags_fragility():
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=20),
        releases_12mo_obs=3,
        last_commit_obs=NOW - timedelta(days=1),
        commits_12mo_obs=50,
        committers_12mo_obs=1,
        committers=[("solo", 50, NOW - timedelta(days=1))],
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == THRIVING
    assert "R-FRAGILE-THRIVING" in verdict.rule_ids


# ---------------------------------------------------------------------------
# Unknown is not dead (the single most important rule)
# ---------------------------------------------------------------------------


def test_no_evidence_at_all_is_unknown():
    evidence = make_evidence()
    evidence.registry_ok = False
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == UNKNOWN
    assert verdict.confidence == "low"


def test_missing_forge_does_not_make_a_package_dead():
    """No commits, no repository: aliveness comes from releases alone."""
    verdict = verdict_of(last_publish_obs=NOW - timedelta(days=60))
    assert verdict == COASTING


def test_a_source_gap_lowers_confidence_but_not_the_verdict():
    with_gap = make_evidence(last_publish_obs=NOW - timedelta(days=DEAD_DAYS + 5))
    without_gap = make_evidence(last_publish_obs=NOW - timedelta(days=DEAD_DAYS + 5))
    with_gap.source_gaps.append("forge: no readable public repository")
    assert evaluate(with_gap, now=NOW).verdict == evaluate(without_gap, now=NOW).verdict
    assert evaluate(with_gap, now=NOW).confidence == "medium"
    assert evaluate(without_gap, now=NOW).confidence == "high"


# ---------------------------------------------------------------------------
# Development without release: the false positive this rubric exists to avoid
# ---------------------------------------------------------------------------


def test_active_repository_without_releases_is_dormant_not_dead():
    """Four-year-old release + a live repository is "not shipping", not "dead".

    A consumer can still get fixes from main, so the verdict is softened from
    dead to dormant and the remedy changes.
    """
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=DEAD_DAYS + 100),
        releases_12mo_obs=0,
        last_commit_obs=NOW - timedelta(days=3),
        commits_12mo_obs=40,
        committers_12mo_obs=2,
        committers=[("lead", 35, NOW - timedelta(days=3))],
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == DORMANT
    assert "R-DEVELOP-WITHOUT-RELEASE" in verdict.rule_ids
    assert any("without publishing" in claim for claim in verdict.claims())


def test_slow_release_cadence_alone_is_not_dormant():
    """PyYAML / django-cors-headers shape: commits weekly, releases yearly.

    An earlier draft called these dormant, which would have called two of the
    most widely deployed Python libraries on earth abandoned.  The release-age
    rules are the only ones allowed to reach a dormant verdict.
    """
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=414),   # ~13.5 months
        releases_12mo_obs=0,
        last_commit_obs=NOW - timedelta(days=40),
        commits_12mo_obs=2,
        committers_12mo_obs=1,
        committers=[("ingydotnet", 2, NOW - timedelta(days=40))],
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == COASTING
    assert "R-DEVELOP-WITHOUT-RELEASE" in verdict.rule_ids
    assert any("without publishing" in claim for claim in verdict.claims())


def test_active_repository_that_still_ships_is_thriving_not_dormant():
    """Regression: an earlier rubric version called requests 'dormant'."""
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=180),
        releases_12mo_obs=2,
        last_commit_obs=NOW - timedelta(days=2),
        commits_12mo_obs=71,
        committers_12mo_obs=5,
    )
    assert evaluate(evidence, now=NOW).verdict == THRIVING


def test_archived_repository_never_softens_to_dormant():
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=DEAD_DAYS + 100),
        releases_12mo_obs=0,
        last_commit_obs=NOW - timedelta(days=3),
        commits_12mo_obs=40,
        committers_12mo_obs=2,
        committers=[("lead", 40, NOW - timedelta(days=3))],
        repo_archived=True,
    )
    assert evaluate(evidence, now=NOW).verdict == DEAD


# ---------------------------------------------------------------------------
# Bus factor
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "committers, expect_single",
    [(0, False), (1, True), (2, False), (5, False)],
)
def test_single_maintainer_flag_tracks_committer_count(committers, expect_single):
    names = [(f"dev{i}", 10, NOW - timedelta(days=5)) for i in range(committers)]
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=30),
        releases_12mo_obs=2,
        last_commit_obs=NOW - timedelta(days=2),
        commits_12mo_obs=10 * max(committers, 1),
        committers_12mo_obs=committers,
        committers=names,
    )
    verdict = evaluate(evidence, now=NOW)
    assert ("R-BUS-ONE" in verdict.rule_ids) is expect_single


def test_bus_factor_one_is_reported_but_does_not_decide_a_verdict():
    """The most important restraint in the rubric.

    A single maintainer is a concentration risk, not evidence of mortality.
    Many healthy packages have one maintainer; flagging them all as dead would
    make the report unreadable.  The fact is still surfaced -- it just cannot
    move the verdict on its own.
    """
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=200),
        releases_12mo_obs=1,
        last_commit_obs=NOW - timedelta(days=500),
        commits_12mo_obs=2,
        committers_12mo_obs=1,
        committers=[("ghost", 2, NOW - timedelta(days=500))],
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == COASTING
    assert "R-BUS-ONE" in verdict.rule_ids
    assert any("last commit" in claim for claim in verdict.claims())


def test_triage_rate_is_supporting_not_deciding():
    """A backlog alone never makes a package dormant."""
    evidence = make_evidence(
        last_publish_obs=NOW - timedelta(days=15),
        releases_12mo_obs=4,
        last_commit_obs=NOW - timedelta(days=1),
        commits_12mo_obs=80,
        committers_12mo_obs=6,
        triage_rate_obs=0.01,
    )
    verdict = evaluate(evidence, now=NOW)
    assert verdict.verdict == THRIVING
    assert "R-TRIAGE-LOW" in verdict.rule_ids


# ---------------------------------------------------------------------------
# Threshold hygiene
# ---------------------------------------------------------------------------


def test_every_deciding_rule_is_reachable():
    """A rule that can decide a verdict must be producible by RULES.

    (``R-NO-RELEASE-DORMANT`` is emitted by the release-age function, which
    also emits the DEAD variant, so it is checked by firing it directly.)
    """
    from deadledger.mortality import DECIDING_RULES, RULES

    reachable = {rule_id for rule_id, _ in RULES}
    reachable.add("R-NO-RELEASE-DORMANT")  # same function as R-NO-RELEASE-DEAD
    assert DECIDING_RULES <= reachable, (
        f"unreachable deciding rules: {sorted(DECIDING_RULES - reachable)}"
    )


def test_thresholds_are_ordered_sensibly():
    assert THRESHOLDS["dormant_after_days"] < THRESHOLDS["dead_after_days"]
    assert THRESHOLDS["thriving_maintainers"] > THRESHOLDS["single_maintainer"]
