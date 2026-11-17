"""The alternatives map is a community asset, so it is tested like one.

Every entry must have a reason, a migration label, and -- if it claims an
``api_diff`` -- a stated basis.  An unexplained number in a community file is
how a curated asset becomes folklore.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from deadledger.alternatives import (
    Alternative,
    AlternativeMap,
    annotate,
    estimate_api_diff,
    load_map,
    normalise,
    validate,
)

MAP_PATH = Path(__file__).parent.parent / "maps" / "alternatives.json"


@pytest.fixture(scope="module")
def shipped_map() -> dict:
    return json.loads(MAP_PATH.read_text())


def test_shipped_map_is_valid(shipped_map):
    assert validate(shipped_map) == []


def test_shipped_map_meets_the_first_release_bar(shipped_map):
    """The first-release checklist says ~50 commonly-dead packages."""
    entries = shipped_map["entries"]
    assert len(entries) >= 50, f"only {len(entries)} entries; the bar is ~50"
    ecosystems = {entry["ecosystem"] for entry in entries}
    assert ecosystems == {"pypi", "npm", "crates"}


def test_every_alternative_has_a_reason_and_links_where_possible(shipped_map):
    missing_reason = []
    for entry in shipped_map["entries"]:
        for alternative in entry["alternatives"]:
            if not alternative.get("reason"):
                missing_reason.append(f"{entry['package']} -> {alternative.get('name')}")
    assert not missing_reason


def test_measured_api_diffs_state_their_basis(shipped_map):
    offenders = []
    for entry in shipped_map["entries"]:
        for alternative in entry["alternatives"]:
            if alternative.get("api_diff") is not None and not alternative.get("basis"):
                offenders.append(f"{entry['package']} -> {alternative['name']}")
    assert not offenders, "an api_diff without a basis is an unsourced number"


def test_estimates_are_labelled_as_estimates_or_measurements(shipped_map):
    honoured = {"measured", "estimated", "reported"}
    offenders = []
    for entry in shipped_map["entries"]:
        for alternative in entry["alternatives"]:
            basis = (alternative.get("basis") or "").strip()
            if not basis:
                continue
            if not any(basis.lower().startswith(word) for word in honoured):
                offenders.append(f"{entry['package']}: {basis[:60]}")
    assert not offenders


def test_map_metadata_is_versioned(shipped_map):
    meta = shipped_map["_meta"]
    assert meta["version"]
    assert meta["updated_at"]
    assert meta["license"] == "MIT"


# ---------------------------------------------------------------------------
# Loading and layering
# ---------------------------------------------------------------------------


def test_shipped_map_loads_and_looks_up():
    map_object = load_map()
    assert map_object.entries
    assert map_object.version != "none"
    alternatives = map_object.lookup("pypi", "purl")
    assert alternatives
    assert alternatives[0].name


def test_lookup_normalises_package_names():
    map_object = load_map()
    assert map_object.lookup("pypi", "PURL") == map_object.lookup("pypi", "purl")
    assert normalise("Django_Filter") == "django-filter"


def test_explicit_map_overrides_the_shipped_one(tmp_path):
    custom = {
        "_meta": {"version": "test-1", "updated_at": "2026-01-01"},
        "entries": [
            {
                "ecosystem": "pypi",
                "package": "purl",
                "alternatives": [
                    {"name": "internal-url-lib", "reason": "we wrote our own", "migration": "rewrite"}
                ],
            }
        ],
    }
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(custom))
    map_object = load_map(explicit=path)
    assert map_object.version == "test-1"
    assert [a.name for a in map_object.lookup("pypi", "purl")] == ["internal-url-lib"]


def test_missing_explicit_map_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_map(explicit=tmp_path / "nope.json")


def test_empty_map_is_usable_and_says_so():
    map_object = AlternativeMap(version="none", updated_at=None, entries={}, source="none")
    assert map_object.lookup("pypi", "anything") == []
    assert "none" in map_object.describe()


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------


def test_api_diff_is_a_fraction_of_covered_names():
    old = {"package": "old", "names": {"a", "b", "c", "d"}}
    new = {"package": "new", "names": {"a", "b", "x"}}
    fraction, basis = estimate_api_diff(old, new)
    assert fraction == 0.5
    assert "2 of 4" in basis


def test_api_diff_is_unknown_without_surfaces():
    fraction, basis = estimate_api_diff({"names": set()}, {"names": {"a"}})
    assert fraction is None
    assert "no comparable API surface" in basis


def test_cost_labels_read_like_english():
    assert "near drop-in" in Alternative("x", "pypi", "r", api_diff=0.95).cost_label
    assert "moderate" in Alternative("x", "pypi", "r", api_diff=0.7).cost_label
    assert "significant" in Alternative("x", "pypi", "r", api_diff=0.4).cost_label
    assert "rewrite-shaped" in Alternative("x", "pypi", "r", api_diff=0.1).cost_label
    # No measurement falls back to the curator's label, not an invented number.
    assert Alternative("x", "pypi", "r", migration="minor").cost_label == "minor"


def test_annotate_attaches_measured_costs():
    map_object = load_map()
    alternatives = annotate(
        map_object,
        "pypi",
        "purl",
        measured_surfaces={
            "purl": {"package": "purl", "names": {"a", "b", "c"}},
            "yarl": {"package": "yarl", "names": {"a", "b"}},
        },
    )
    assert alternatives
    assert any(alt["api_diff"] == pytest.approx(0.667) for alt in alternatives)


def test_validate_flags_the_things_that_matter():
    broken = {
        "_meta": {},
        "entries": [
            {"ecosystem": "nope", "package": "x", "alternatives": [{"name": "y"}]},
            {
                "ecosystem": "pypi",
                "package": "dupe",
                "alternatives": [{"name": "y", "reason": "r", "api_diff": 2.0}],
            },
            {"ecosystem": "pypi", "package": "dupe", "alternatives": []},
        ],
    }
    problems = validate(broken)
    text = "\n".join(problems)
    assert "missing _meta.version" in text
    assert "ecosystem" in text
    assert "duplicate" in text
    assert "at least one alternative" in text
    assert "within [0, 1]" in text
