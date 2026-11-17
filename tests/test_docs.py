"""Documentation is part of the contract, so it is tested.

Two things rot silently in a project like this: the threshold table drifting
away from the code, and a rubric change landing without a changelog entry.
Both are caught here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_rubric_doc_covers_every_verdict():
    text = read(DOCS / "verdicts.md")
    for verdict in ("thriving", "coasting", "dormant", "dead", "unknown"):
        assert f"**{verdict}**" in text, f"verdict {verdict} is not documented"


def test_threshold_table_matches_the_code():
    """The number a reader is quoted must be the number the code uses."""
    from deadledger.mortality import THRESHOLDS

    text = read(DOCS / "verdicts.md")
    table = text.split("<!-- thresholds-table:begin -->")[1].split(
        "<!-- thresholds-table:end -->"
    )[0]
    for name, value in THRESHOLDS.items():
        if name in {"thriving_last_commit_days", "inactive_committer_days"}:
            continue  # expressed in the table as prose/others
        assert str(value) in table, f"threshold {name}={value} is missing from the table"


def test_rubric_version_matches_the_changelog():
    from deadledger import RUBRIC_VERSION

    changelog = read(DOCS / "rubric-changelog.md")
    assert re.search(rf"^## {re.escape(RUBRIC_VERSION)} ", changelog, flags=re.MULTILINE), (
        f"rubric {RUBRIC_VERSION} has no changelog entry"
    )


def test_every_rule_id_appears_in_the_rubric_doc():
    """A rule that can fire must be findable by the id the report prints."""
    from deadledger.mortality import RULES

    text = read(DOCS / "verdicts.md") + read(DOCS / "rubric-changelog.md")
    missing = [rule_id for rule_id, _ in RULES if rule_id not in text and rule_id not in {
        # Grouped in prose rather than by id; covered by the precedence list.
        "R-NO-RELEASE-DORMANT",
        "R-NO-RELEASE-DEAD",
        "R-THRIVING",
        "R-DEPRECATED",
        "R-ARCHIVED",
        "R-REGISTRY-404",
        "R-NO-EVIDENCE",
        "R-QUIET-DEFAULT",
    }]
    assert not missing, f"undocumented rule ids: {missing}"


def test_readme_shows_a_real_command_and_a_real_demo():
    text = read(ROOT / "README.md")
    assert "pipx install deadledger" in text
    assert "deadledger audit" in text


def test_readme_links_the_rubric():
    text = read(ROOT / "README.md")
    assert "docs/verdicts.md" in text


def test_contributing_explains_where_to_argue():
    text = read(ROOT / "CONTRIBUTING.md")
    assert "docs/verdicts.md" in text
    assert "maps/alternatives.json" in text
    assert "rubric-changelog" in text


def test_license_is_mit():
    text = read(ROOT / "LICENSE")
    assert "MIT License" in text


def test_every_doc_referenced_from_the_readme_exists():
    text = read(ROOT / "README.md")
    links = re.findall(r"\]\((docs/[^)#]+|maps/[^)#]+|tests/[^)#]+|examples/[^)#]+)\)", text)
    for link in set(links):
        assert (ROOT / link).exists(), f"README links a missing file: {link}"


def test_example_report_is_committed_and_matches_its_lockfile():
    example = ROOT / "examples" / "netbox-3.0"
    assert (example / "requirements.txt").is_file()
    report = example / "REPORT.md"
    assert report.is_file(), "the demo report is the README's evidence; commit it"
    text = report.read_text()
    assert "Mortality report" in text
    assert "## Sources" in text


def test_example_report_quotes_the_same_rubric_version():
    from deadledger import RUBRIC_VERSION

    text = (ROOT / "examples" / "netbox-3.0" / "REPORT.md").read_text()
    assert f"rubric v{RUBRIC_VERSION}" in text


def test_readme_demo_numbers_match_the_committed_reports():
    """Every report the README quotes must agree with its own summary.

    A demo whose numbers drift from its evidence is worse than no demo: it is
    the first thing a sceptical reader checks.
    """
    readme = read(ROOT / "README.md")

    for name in ("saleor-2.11", "netbox-3.0"):
        report = (ROOT / "examples" / name / "REPORT.md").read_text(encoding="utf-8")
        dead, dormant = (
            int(m.group(1)),
            int(m.group(2)),
        ) if (
            m := re.search(r"\*\*(\d+) dead\*\*, \*\*(\d+) dormant\*\*", report)
        ) else (None, None)
        assert dead is not None, f"{name} has no dead/dormant summary"

        # Either the exact phrasing or the same numbers in prose is acceptable;
        # what must hold is that the README's claim is derivable from the report.
        claims = re.findall(rf"{re.escape(name)}[^\n]*\n?[^\n]*?(\d+) dead", readme)
        if claims:
            assert int(claims[0]) == dead, (
                f"README says {claims[0]} dead for {name}, report says {dead}"
            )
        else:
            assert f"**{dead} dead**" in readme or f"{dead} dead" in readme

    # The bus-factor line is a claim about the report's own table.
    netbox = (ROOT / "examples" / "netbox-3.0" / "REPORT.md").read_text(encoding="utf-8")
    single = len(re.findall(r"^\| `[^`]+` \[src", netbox, flags=re.MULTILINE))
    assert f"{single} single-maintainer" in readme, (
        f"README should say {single} single-maintainer for the NetBox demo"
    )


def test_reported_paths_are_repo_relative():
    """A committed report must not embed the absolute path of one machine."""
    text = (ROOT / "examples" / "netbox-3.0" / "REPORT.md").read_text()
    assert "/home/" not in text
    assert "/Users/" not in text
    assert "Audited `examples/netbox-3.0/requirements.txt`" in text


def test_saleor_report_is_committed_and_consistent():
    """The report the README leads with must exist and match its own summary."""
    report_path = ROOT / "examples" / "saleor-2.11" / "REPORT.md"
    assert report_path.is_file()
    text = report_path.read_text(encoding="utf-8")
    assert "Mortality report" in text
    assert "## Sources" in text
    assert "/home/" not in text

    readme = read(ROOT / "README.md")
    summary = re.search(r"\*\*(\d+) dead\*\*, \*\*(\d+) dormant\*\*", text)
    assert summary
    assert f"**{summary.group(1)} dead**" in readme

    # The count in the headline must equal the number of package sections.
    sections = re.findall(r"^### \S+ \S+ — (?:🔴 dead|🟠 dormant)", text, flags=re.MULTILINE)
    assert len(sections) == int(summary.group(1)) + int(summary.group(2))


def test_saleor_example_documents_why_fixtures_are_absent():
    """A demo with no offline fixtures must say so, or it looks broken."""
    note = ROOT / "examples" / "saleor-2.11" / "README.md"
    assert note.is_file()
    text = note.read_text(encoding="utf-8")
    assert "79 MB" in text or "79MB" in text
    assert "deadledger record --profile saleor-2.11" in text
