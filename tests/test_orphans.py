"""The orphan simulation (Requirement 3).

"if this dies: who else uses it?" -- and, just as important, an honest
"unknown" when no source publishes a usage figure.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from deadledger.evidence import PackageEvidence, obs
from deadledger.orphans import REACH_BANDS, _band, _solo, simulate
from deadledger.util import human_int

NOW = datetime(2026, 11, 16, tzinfo=timezone.utc)


def evidence(**kwargs) -> PackageEvidence:
    item = PackageEvidence(ecosystem=kwargs.pop("ecosystem", "pypi"), name=kwargs.pop("name", "pkg"))
    for field, value in kwargs.items():
        setattr(item, field, value)
    return item


def observation(value, source="pypistats", detail="downloads in the last month"):
    return obs(value, source=source, url=f"https://example.invalid/{source}", retrieved_at=NOW, detail=detail)


def test_exact_dependent_count_from_crates_is_quoted_as_exact():
    item = evidence(ecosystem="crates", name="tempdir")
    item.dependents_obs = observation(1200, source="crates.io")
    answer = simulate(item)
    assert answer.reach_label == "exact"
    assert "1,200 crates depend on tempdir" in answer.answer
    assert "exact count" in answer.answer


def test_downloads_are_labelled_approximate_and_explain_themselves():
    item = evidence(name="purl")
    item.download_count_obs = observation(250_000)
    answer = simulate(item)
    assert answer.reach_label == "approximate"
    assert "250.0k downloads" in answer.answer
    assert "not a dependent count" in answer.answer
    assert answer.citation.startswith("https://example.invalid/pypistats")


def test_code_search_fallback_is_used_when_downloads_are_missing():
    item = evidence(name="purl")
    item.usage_obs = obs(
        1300,
        source="github code search",
        url="https://api.github.com/search/code",
        retrieved_at=NOW,
        detail="files containing 'import purl'",
    )
    answer = simulate(item)
    assert answer.reach_label == "approximate"
    assert "files contain it" in answer.answer


def test_no_sources_means_unknown_never_zero():
    answer = simulate(evidence(name="mystery"))
    assert answer.reach_label == "unknown"
    assert answer.usage is None
    assert answer.solo_risk == "unknown"
    # The sentence is embedded in a sentence in the report ("Orphan check:
    # no source published..."), so it must read as a clause, not a fragment.
    assert answer.answer == "no source published a usage or dependent count."


def test_failed_observation_value_is_not_treated_as_zero():
    item = evidence(name="mystery")
    item.download_count_obs = observation(None)
    assert simulate(item).reach_label == "unknown"


@pytest.mark.parametrize(
    "count, expected",
    [
        (0, "niche"),
        (999, "niche"),
        (1_000, "used by some projects"),
        (50_000, "used across the ecosystem"),
        (500_000, "widely used"),
        (5_000_000, "very widely used"),
        (50_000_000, "essentially universal"),
    ],
)
def test_reach_bands(count, expected):
    assert _band(count) == expected


def test_solo_risk_scales_with_usage():
    assert _solo(10) == "you would likely be alone"
    assert "community" in _solo(5_000)
    assert _solo(500_000) == "many would share the pain"


def test_consequence_is_ecosystem_specific():
    assert "fork" in simulate(evidence(ecosystem="pypi")).consequence
    assert "vendoring" in simulate(evidence(ecosystem="crates")).consequence
    assert "overrides" in simulate(evidence(ecosystem="npm")).consequence


def test_human_int_is_readable():
    assert human_int(999) == "999"
    assert human_int(1_500) == "1.5k"
    assert human_int(2_400_000) == "2.4M"
    assert human_int(None) == "unknown"


def test_exact_count_wins_over_downloads():
    """crates.io can publish both; the exact answer is the one to quote."""
    item = evidence(ecosystem="crates", name="tempdir")
    item.dependents_obs = observation(800, source="crates.io")
    item.download_count_obs = observation(9_000_000)
    answer = simulate(item)
    assert answer.reach_label == "exact"
    assert answer.usage == 800
