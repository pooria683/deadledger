"""CI mode: fail on NEW deaths only (Requirement 7).

The anti-fatigue property is the reason this tool can live in a pipeline.  A
build must fail the first time a critical dependency dies and then stay quiet
about it forever after -- otherwise people mute the check, and the check was
the whole point.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from conftest import NOW, make_evidence
from deadledger.audit import (
    AuditResult,
    Ledger,
    LedgerEntry,
    PackageReport,
    diff_against,
)
from deadledger.lockfiles import Node
from deadledger.mortality import evaluate

UTC = timezone.utc


def report(name: str, verdict: str, *, critical: bool = True, rule_ids=None) -> PackageReport:
    node = Node(ecosystem="pypi", name=name, version="1.0.0", key=f"{name}@1.0.0", dev=not critical)
    evidence = make_evidence(name=name)
    verdict_object = evaluate(evidence, now=NOW)
    # Override the computed verdict with the one the test wants to encode.
    verdict_object.verdict = verdict
    if rule_ids is not None:
        verdict_object.rule_ids = property(lambda self: rule_ids)  # type: ignore[assignment]
    return PackageReport(
        node=node,
        evidence=evidence,
        verdict=verdict_object,
        depth=0 if critical else 1,
        paths=1,
        parents=[],
        critical=critical,
    )


def _result(tmp_path, packages):
    """A minimal AuditResult for rendering tests (no network, no adapters)."""
    from deadledger.graph import analyse
    from deadledger.lockfiles import Inventory

    inventory = Inventory(
        ecosystem="pypi",
        lockfile=tmp_path / "requirements.txt",
        nodes={p.node.key: p.node for p in packages},
    )
    return AuditResult(
        ecosystem="pypi",
        lockfile=tmp_path / "requirements.txt",
        as_of=NOW,
        packages=packages,
        graph=analyse(inventory),
        inventory=inventory,
        map_version="1.0.0",
    )


def test_first_run_establishes_a_baseline_and_does_not_fail(tmp_path):
    ledger = Ledger(project="demo")
    fresh = [report("deadpkg", "dead")]
    diff = diff_against(ledger, fresh)
    assert diff.is_first_run
    # Nothing is "new" when there is no history to be new against.
    assert not diff.new_deaths


def test_a_death_seen_before_is_not_reported_again(tmp_path):
    ledger = Ledger(project="demo")
    first = [report("deadpkg", "dead")]
    ledger.record(first, when=NOW)
    diff = diff_against(ledger, first)
    assert not diff.has_new_risk


def test_a_newly_dead_package_is_reported(tmp_path):
    ledger = Ledger(project="demo")
    healthy = [report("alive", "thriving")]
    ledger.record(healthy, when=NOW - timedelta(days=1))
    now_dead = [report("alive", "dead")]
    diff = diff_against(ledger, now_dead)
    assert [r.name for r in diff.new_deaths] == ["alive"]
    assert diff.has_new_risk


def test_dormant_to_dead_is_a_new_death():
    ledger = Ledger(project="demo")
    ledger.record([report("pkg", "dormant")], when=NOW - timedelta(days=1))
    diff = diff_against(ledger, [report("pkg", "dead")])
    assert [r.name for r in diff.new_deaths] == ["pkg"]


def test_recovery_is_reported_but_never_fails_the_build():
    ledger = Ledger(project="demo")
    ledger.record([report("pkg", "dead")], when=NOW - timedelta(days=1))
    diff = diff_against(ledger, [report("pkg", "thriving")])
    assert [r.name for r in diff.recovered] == ["pkg"]
    assert not diff.has_new_risk


def test_a_transitive_death_does_not_fail_the_build():
    """Only critical deaths are a build problem: you cannot migrate what you
    do not declare."""
    ledger = Ledger(project="demo")
    ledger.record([report("dep", "thriving", critical=False)], when=NOW - timedelta(days=1))
    diff = diff_against(ledger, [report("dep", "dead", critical=False)])
    assert not diff.new_deaths
    assert not diff.has_new_risk


def test_ledger_file_round_trips_and_is_human_readable(tmp_path):
    path = tmp_path / "ledger.json"
    ledger = Ledger(project="demo")
    ledger.record([report("pkg", "dead")], when=NOW)
    ledger.save(path)

    text = path.read_text()
    assert "pkg@1.0.0" in text
    assert '"version"' in text

    reloaded = Ledger.load(path, "demo")
    assert reloaded.entries["pkg@1.0.0"].verdict == "dead"
    assert reloaded.runs == 1


def test_ledger_records_first_and_last_seen():
    ledger = Ledger(project="demo")
    ledger.record([report("pkg", "dead")], when=NOW - timedelta(days=30))
    ledger.record([report("pkg", "dead")], when=NOW)
    entry = ledger.entries["pkg@1.0.0"]
    assert entry.first_seen == (NOW - timedelta(days=30)).strftime("%Y-%m-%d")
    assert entry.last_seen == NOW.strftime("%Y-%m-%d")
    assert ledger.runs == 2


def test_ledger_forgets_packages_removed_from_the_tree():
    ledger = Ledger(project="demo")
    ledger.record([report("old", "dead"), report("kept", "thriving")], when=NOW)
    removed = ledger.forget_missing([report("kept", "thriving")])
    assert removed == ["old@1.0.0"]
    assert list(ledger.entries) == ["kept@1.0.0"]


def test_corrupt_ledger_is_a_clear_error(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("{not json")
    with pytest.raises(ValueError, match="not valid JSON"):
        Ledger.load(path, "demo")


def test_summary_line_reads_like_english():
    ledger = Ledger(project="demo")
    ledger.record([report("a", "thriving")], when=NOW - timedelta(days=1))
    diff = diff_against(ledger, [report("a", "dead"), report("b", "damaged")])
    assert "1 new death" in diff.summary_line()


def test_ci_summary_reports_the_previous_run_timestamp(tmp_path):
    """A CI line that says 'since the last run' must say *when* that was."""
    from deadledger.cli import _ci_summary

    fresh = [report("alive", "thriving"), report("stable", "coasting")]
    result = _result(tmp_path, fresh)

    ledger_path = tmp_path / "ledger.json"
    ledger = Ledger(project="demo")
    ledger.record(fresh, when=NOW)
    ledger.last_run = "2026-01-02T03:04:05Z"
    ledger.save(ledger_path)

    reloaded = Ledger.load(ledger_path, "demo")
    diff = diff_against(reloaded, fresh)
    assert diff.previous_run == "2026-01-02T03:04:05Z"

    summary = _ci_summary(result, diff)
    assert "(last run 2026-01-02T03:04:05Z)" in summary
    # The old bug produced a dangling "(last run " with no timestamp and no
    # closing paren, because the f-string interpolated an empty expression.
    assert "()" not in summary
    assert summary.count("(") == summary.count(")")


def test_ci_summary_first_run_has_no_previous_timestamp(tmp_path):
    from deadledger.cli import _ci_summary

    fresh = [report("deadpkg", "dead")]
    result = _result(tmp_path, fresh)
    diff = diff_against(Ledger(project="demo"), fresh)
    assert diff.is_first_run
    summary = _ci_summary(result, diff)
    assert "first run: baseline recorded" in summary
    assert "last run" not in summary


def test_removing_a_dead_package_does_not_resurrect_an_alarm(tmp_path):
    """A ledger keyed on the lockfile would re-baseline; we key on the project.

    Removing a dependency must not make its old entry look like a new finding,
    and re-adding it must not look like a new death either (it was recorded).
    """
    ledger = Ledger(project="demo")
    ledger.record([report("deadpkg", "dead"), report("alive", "thriving")], when=NOW)

    # Tree no longer contains deadpkg.
    after_removal = diff_against(ledger, [report("alive", "thriving")])
    assert after_removal.new_deaths == []
    assert not after_removal.has_new_risk

    # Re-added later: the ledger still knows it, so it is not new mortality.
    after_readd = diff_against(ledger, [report("deadpkg", "dead"), report("alive", "thriving")])
    assert after_readd.new_deaths == []
    assert not after_readd.has_new_risk
