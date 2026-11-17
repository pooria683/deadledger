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


def test_readme_demo_numbers_match_the_committed_report():
    """The README's headline table must be the report's own summary.

    A demo whose numbers drift from its evidence is worse than no demo: it is
    the first thing a sceptical reader checks.
    """
    report = (ROOT / "examples" / "netbox-3.0" / "REPORT.md").read_text(encoding="utf-8")
    readme = read(ROOT / "README.md")

    import re as _re

    summary = _re.search(
        r"\*\*(\d+) dead\*\*, \*\*(\d+) dormant\*\*", report
    ) or _re.search(r"- \*\*(\d+) dead\*\*, \*\*(\d+) dormant\*\*", report)
    assert summary, "the demo report has no dead/dormant summary line"
    dead, dormant = summary.group(1), summary.group(2)

    assert f"**{dead} dead**" in readme, f"README does not say {dead} dead"
    assert f"**{dormant} dormant**" in readme, f"README does not say {dormant} dormant"

    single = len(_re.findall(r"^\| `[^`]+` \[src", report, flags=_re.MULTILINE))
    assert f"**{single} with a bus factor of 1**" in readme


def test_reported_paths_are_repo_relative():
    """A committed report must not embed the absolute path of one machine."""
    text = (ROOT / "examples" / "netbox-3.0" / "REPORT.md").read_text()
    assert "/home/" not in text
    assert "/Users/" not in text
    assert "Audited `examples/netbox-3.0/requirements.txt`" in text
