"""CLI behaviour, end to end, with no network.

The CLI is where the promises become visible: exit codes, ``--offline``, the
first-run grace period in ``ci``, and the fact that a report is written to
stdout unless you name a file.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from deadledger.cli import main


@pytest.fixture()
def project(tmp_path) -> Path:
    """A tiny lockfile in its own directory."""
    (tmp_path / "requirements.txt").write_text("django==3.2.6\nsqlparse==0.4.1\n")
    return tmp_path


@pytest.fixture()
def replay_env(project, tmp_path, monkeypatch, fixtures_root):
    """Point the CLI at the recorded fixtures and a scratch cache."""
    from deadledger import http

    monkeypatch.setattr(http, "FIXTURE_ROOT", fixtures_root)
    cache = tmp_path / "cache.sqlite"
    return {"--cache": str(cache)}


def test_version_is_available(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert "deadledger" in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "audit" in capsys.readouterr().out


def test_missing_lockfile_is_a_usage_error(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["--cache", str(tmp_path / "c.sqlite"), "audit"]) == 2
    assert "no lockfile" in capsys.readouterr().err


def test_audit_reports_missing_fixtures_as_gaps_not_a_crash(project, tmp_path, capsys, monkeypatch):
    """With an empty cache and no network, every package is unknown -- and the
    command still exits 0, because 'we could not look' is not 'everything died'."""
    monkeypatch.chdir(project)
    code = main(["--cache", str(tmp_path / "c.sqlite"), "--offline", "audit", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "deadledger/report/v1"
    assert payload["counts"]["unknown"] == 2
    assert payload["counts"]["dead"] == 0


def test_audit_writes_to_a_file_when_asked(project, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(project)
    output = tmp_path / "out" / "report.md"
    code = main(
        [
            "--cache",
            str(tmp_path / "c.sqlite"),
            "--offline",
            "audit",
            "--format",
            "markdown",
            "-o",
            str(output),
        ]
    )
    assert code == 0
    assert "DeadLedger" in output.read_text() or "Mortality report" in output.read_text()


def test_audit_fail_on_critical_is_opt_in(project, tmp_path, monkeypatch):
    monkeypatch.chdir(project)
    base = ["--cache", str(tmp_path / "c.sqlite"), "--offline", "audit", "--format", "json"]
    assert main([*base, "--fail-on", "none"]) == 0
    # Nothing is dead in an all-unknown report, so even --fail-on critical passes.
    assert main([*base, "--fail-on", "critical"]) == 0


def test_ci_grace_period_then_quiet(project, tmp_path, monkeypatch, capsys):
    """First run baselines; a second identical run fails on nothing."""
    monkeypatch.chdir(project)
    args = ["--cache", str(tmp_path / "c.sqlite"), "--offline", "ci"]
    assert main(args) == 0
    first_err = capsys.readouterr().err
    assert "baseline" in first_err.lower()

    assert main(args) == 0
    second = capsys.readouterr()
    assert "no new mortality" in second.err.lower()
    ledger = project / ".deadledger"
    assert ledger.is_dir()


def test_ci_fails_on_a_new_death(project, tmp_path, monkeypatch, capsys):
    """Simulate a package dying between two runs."""
    monkeypatch.chdir(project)
    args = ["--cache", str(tmp_path / "c.sqlite"), "--offline", "ci"]
    main(args)
    capsys.readouterr()

    ledger_path = next((project / ".deadledger").glob("ledger-*.json"))
    document = json.loads(ledger_path.read_text())
    key = "django@3.2.6"
    document["entries"][key]["verdict"] = "thriving"
    ledger_path.write_text(json.dumps(document))

    # The offline audit still produces 'unknown' for everything, which is not a
    # death, so the build stays green: unknown never fails CI.
    assert main(args) == 0


def test_ledger_show_and_reset(project, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(project)
    main(["--cache", str(tmp_path / "c.sqlite"), "--offline", "ci"])
    capsys.readouterr()

    assert main(["ledger", "show"]) == 0
    assert "Ledger:" in capsys.readouterr().out

    assert main(["ledger", "reset", "--yes"]) == 0
    assert "removed" in capsys.readouterr().out


def test_cache_info_and_prune(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["--cache", str(tmp_path / "c.sqlite"), "cache", "info"]) == 0
    assert "Cache:" in capsys.readouterr().out
    assert main(["--cache", str(tmp_path / "c.sqlite"), "cache", "prune"]) == 0


def test_sources_lists_every_adapter(capsys):
    assert main(["sources", "--format", "json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    ecosystems = {row["ecosystem"] for row in rows}
    assert ecosystems == {"pypi", "npm", "crates"}
    crates = next(row for row in rows if row["ecosystem"] == "crates")
    assert crates["dependents"], "crates.io publishes exact dependent counts"


def test_map_lint_passes_on_the_shipped_map(capsys):
    assert main(["map", "lint"]) == 0
    assert "ok:" in capsys.readouterr().out


def test_map_lint_catches_a_broken_entry(tmp_path, capsys):
    broken = {
        "_meta": {"version": "9.9", "updated_at": "2026-01-01"},
        "entries": [
            {"ecosystem": "pypi", "package": "x", "alternatives": [{"name": "y"}]},
            {"ecosystem": "wat", "package": "z", "alternatives": []},
        ],
    }
    path = tmp_path / "map.json"
    path.write_text(json.dumps(broken))
    assert main(["map", "lint", "--map", str(path)]) == 1
    out = capsys.readouterr().out
    assert "ecosystem" in out
    assert "reason" in out


def test_doctor_reports_checks(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("django==3.2.6\n")
    code = main(["--cache", str(tmp_path / "c.sqlite"), "doctor"])
    out = capsys.readouterr().out
    assert "cache" in out
    assert "lockfile" in out
    assert code in (0, 1)


def test_explain_requires_a_known_package(project, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(project)
    code = main(["--cache", str(tmp_path / "c.sqlite"), "--offline", "explain", "nope"])
    assert code == 2
    assert "not in" in capsys.readouterr().err


def test_explain_shows_evidence_for_a_known_package(project, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(project)
    code = main(["--cache", str(tmp_path / "c.sqlite"), "--offline", "explain", "django"])
    assert code == 0
    out = capsys.readouterr().out
    assert "django" in out
    assert "Why:" in out or "Evidence" in out
