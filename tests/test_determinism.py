"""Determinism: same cached data in, byte-identical report out.

Requirement 6 says ``deadledger audit`` works offline from cache.  That is only
meaningful if "offline" is *the same audit* you get online, not a different
one.  These tests pin that down:

* the verdict clock comes from the evidence, never from ``now()``;
* rendering the same result twice produces identical bytes;
* replaying recorded fixtures twice produces identical reports;
* the report's "as of" date follows the recordings, not the day the test runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import NOW, make_evidence
from deadledger.audit import Runner
from deadledger.cache import Cache
from deadledger.http import CachingClient
from deadledger.lockfiles import parse_lockfile
from deadledger.mortality import evaluate
from deadledger.render import render_json, render_markdown, render_sarif, render_text


def _replay_audit(profile: str, lockfile: Path):
    client = CachingClient(None, Cache(":memory:"), mode="replay", profile=profile)
    return Runner(client).run(parse_lockfile(lockfile))


def test_same_evidence_same_verdict():
    first = make_evidence(last_publish_obs=NOW.replace(day=1), releases_12mo_obs=3)
    snapshot = evaluate(first, now=NOW)
    for _ in range(5):
        again = evaluate(first, now=NOW)
        assert again.verdict == snapshot.verdict
        assert again.rule_ids == snapshot.rule_ids
        assert again.reasons == snapshot.reasons
        assert again.confidence == snapshot.confidence


def test_verdict_is_independent_of_dict_ordering():
    """Rule evaluation must not depend on the order observations were filled in."""
    a = make_evidence(last_publish_obs=NOW.replace(month=1, day=1), releases_12mo_obs=1)
    b = make_evidence(releases_12mo_obs=1, last_publish_obs=NOW.replace(month=1, day=1))
    assert evaluate(a, now=NOW).reasons == evaluate(b, now=NOW).reasons


def test_render_is_byte_stable(replay_audit):
    first = render_markdown(replay_audit)
    second = render_markdown(replay_audit)
    assert first == second

    assert render_json(replay_audit) == render_json(replay_audit)
    assert render_text(replay_audit) == render_text(replay_audit)
    assert json.dumps(render_sarif(replay_audit), sort_keys=True) == json.dumps(
        render_sarif(replay_audit), sort_keys=True
    )


def test_replay_twice_is_identical(fixtures_root, netbox_requirements):
    first = _replay_audit("netbox-3.0", netbox_requirements)
    second = _replay_audit("netbox-3.0", netbox_requirements)
    assert render_markdown(first) == render_markdown(second)
    assert first.evidence_fingerprint() == second.evidence_fingerprint()


def test_ledger_round_trip_is_stable(tmp_path, replay_audit):
    from deadledger.audit import Ledger

    path = tmp_path / "ledger.json"
    ledger = Ledger.load(path, "netbox")
    ledger.record(replay_audit.packages, when=replay_audit.as_of)
    ledger.save(path)

    first = path.read_text()
    reloaded = Ledger.load(path, "netbox")
    reloaded.save(path)
    assert path.read_text() == first, "saving a freshly loaded ledger must be idempotent"
    assert reloaded.last_run == ledger.last_run


def test_report_as_of_follows_the_recordings_not_the_wall_clock(replay_audit):
    """The clock is the newest retrieval in the evidence, so replay is stable."""
    newest = None
    for report in replay_audit.packages:
        for observation in report.evidence.observation_map().values():
            if newest is None or observation.retrieved_at > newest:
                newest = observation.retrieved_at
    assert replay_audit.as_of == newest


def test_offline_replay_matches_replay_mode(cache, netbox_requirements):
    """A cache built by replay can be audited offline with the same verdicts."""
    client = CachingClient(None, cache, mode="replay", profile="netbox-3.0")
    inventory = parse_lockfile(netbox_requirements)
    online_ish = Runner(client).run(inventory)

    offline = CachingClient(None, cache, mode="offline")
    offline_result = Runner(offline).run(parse_lockfile(netbox_requirements))

    assert offline_result.as_of == online_ish.as_of
    assert offline_result.counts() == online_ish.counts()
    left = {r.name: r.verdict_name for r in offline_result.packages}
    right = {r.name: r.verdict_name for r in online_ish.packages}
    assert left == right


def test_json_report_is_valid_and_ordered(replay_audit):
    payload = render_json(replay_audit)
    text = json.dumps(payload)
    assert json.loads(text)["schema"] == "deadledger/report/v1"
    names = [p["name"] for p in payload["packages"]]
    # Reports are ordered by severity then name, which is what makes a diff of
    # two runs readable: new deaths float to the top.
    severities = {"thriving": 0, "unknown": 1, "coasting": 1, "dormant": 2, "dead": 3}
    keys = [(severities[p["verdict"]], p["name"]) for p in payload["packages"]]
    assert keys == sorted(keys), "packages are emitted in a stable (severity, name) order"


def test_sarif_has_required_shape(replay_audit):
    document = render_sarif(replay_audit)
    assert document["version"] == "2.1.0"
    run = document["runs"][0]
    assert run["tool"]["driver"]["name"] == "DeadLedger"
    rule_ids = {rule["id"] for rule in run["tool"]["driver"]["rules"]}
    for result in run["results"]:
        assert result["ruleId"] in rule_ids
        assert result["locations"], "every finding points at the lockfile"
