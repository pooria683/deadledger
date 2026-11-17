"""Report guarantees (Requirement 4).

The report is the product, so its promises are testable promises:

* every claim carries a citation marker, and every marker resolves;
* the sources table has a retrieval date for every entry;
* a verdict never appears without at least one reason;
* the four verdict words are used consistently in prose.
"""

from __future__ import annotations

import re

import pytest

from deadledger.render import SourceIndex, render_json, render_markdown, render_sarif, render_text

CITATION = re.compile(r"\[src (\d+)\]")


def test_markdown_has_the_adr_sections(replay_audit):
    document = render_markdown(replay_audit)
    for heading in (
        "# Mortality report",
        "## Summary",
        "## What is dead or dying",
        "## Bus factor",
        "## Orphan simulation",
        "## Migration hints",
        "## Every package",
        "## What this report does not know",
        "## Sources",
    ):
        assert heading in document, f"missing section: {heading}"


def test_every_citation_marker_resolves_to_a_source_row(replay_audit):
    document = render_markdown(replay_audit)
    markers = {int(n) for n in CITATION.findall(document)}
    assert markers, "the report cites nothing, which means it proves nothing"
    rows = len(re.findall(r"^\| \d+ \| <https?://", document, flags=re.MULTILINE))
    assert max(markers) <= rows, "a [src N] marker points past the sources table"


def test_sources_table_has_url_and_retrieval_date(replay_audit):
    document = render_markdown(replay_audit)
    rows = re.findall(r"^\| (\d+) \| <([^>]+)> \| ([^|]+) \|$", document, flags=re.MULTILINE)
    assert rows
    for number, url, retrieved in rows:
        assert url.startswith("http")
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", retrieved.strip())


def test_no_verdict_without_a_reason(replay_audit):
    for report in replay_audit.packages:
        if report.verdict_name in ("thriving", "coasting", "dormant", "dead"):
            assert report.verdict.reasons, f"{report.name} has a verdict and no reason"
            assert report.verdict.rules, f"{report.name} has a verdict and no rule hit"


def test_dead_and_dormant_packages_appear_in_the_body(replay_audit):
    document = render_markdown(replay_audit)
    for report in replay_audit.packages:
        if report.verdict_name in ("dead", "dormant"):
            assert report.name in document


def test_report_counts_match_the_packages(replay_audit):
    counts = replay_audit.counts()
    document = render_markdown(replay_audit)
    assert f"**{counts['total']} packages**" in document
    assert counts["dead"] + counts["dormant"] + counts["coasting"] + counts["thriving"] + counts[
        "unknown"
    ] == counts["total"]


def test_gaps_section_lists_every_missing_source(replay_audit):
    document = render_markdown(replay_audit)
    missing = [r.name for r in replay_audit.packages if r.evidence.source_gaps]
    if missing:
        assert "## What this report does not know" in document
        assert any(name in document.split("## What this report does not know")[1] for name in missing)


def test_thresholds_are_printed_so_a_reader_can_disagree(replay_audit):
    document = render_markdown(replay_audit)
    assert "730 days" in document
    assert "1460 days" in document
    assert "docs/verdicts.md" in document


def test_text_output_is_short_and_actionable(replay_audit):
    text = render_text(replay_audit)
    assert len(text.splitlines()) < 60
    assert replay_audit.ecosystem in text
    for report in replay_audit.packages:
        if report.verdict_name == "dead" and report.critical:
            assert report.name in text


def test_text_has_no_ansi_codes_by_default(replay_audit):
    assert "\x1b[" not in render_text(replay_audit)


def test_json_exposes_rule_ids_and_evidence_rows(replay_audit):
    payload = render_json(replay_audit)
    package = next(p for p in payload["packages"] if p["verdict"] in ("dead", "dormant"))
    assert package["rule_ids"]
    assert package["evidence"], "a verdict must ship the observations behind it"
    for row in package["evidence"]:
        assert row["citation"].startswith("http")


def test_json_orphan_answers_are_labelled(replay_audit):
    payload = render_json(replay_audit)
    for package in payload["packages"]:
        if package["critical"] and package["orphan"]:
            assert package["orphan"]["reach"] in ("exact", "approximate", "unknown")
            assert package["orphan"]["answer"]


def test_sarif_points_at_the_lockfile(replay_audit):
    document = render_sarif(replay_audit)
    results = document["runs"][0]["results"]
    if results:
        location = results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        assert location.endswith(("requirements.txt", "package-lock.json", "Cargo.lock"))


def test_source_index_numbers_are_stable():
    index = SourceIndex()
    first = index.add("https://example.invalid/a (retrieved 2026-01-01T00:00:00Z)")
    again = index.add("https://example.invalid/a (retrieved 2026-01-01T00:00:00Z)")
    second = index.add("https://example.invalid/b (retrieved 2026-01-01T00:00:00Z)")
    assert first == again == "[src 1]"
    assert second == "[src 2]"
    assert len(index.rows) == 2


def test_source_index_ignores_empty_citations():
    index = SourceIndex()
    assert index.add(None) == ""
    assert index.rows == []


def test_headline_leads_with_critical_findings(replay_audit):
    """The headline must not open with a transitive package.

    On the Saleor tree, severity-only ordering introduced the section with
    `colorama` (dormant, depth 1) while twelve dead direct dependencies sat
    below it. The headline is the only part most readers read.
    """
    markdown = render_markdown(replay_audit)
    headline = markdown.split("### The headline")[1].split("## What is dead")[0]
    bullets = [line for line in headline.splitlines() if line.startswith("- `")]
    assert bullets, "the demo tree has deaths; the headline cannot be empty"
    assert all("(critical)" in line for line in bullets), bullets
    # Deaths outrank dormancy within the critical set.
    verdicts = [line.split("**")[1] for line in bullets]
    assert verdicts == sorted(verdicts, key=lambda v: {"dead": 0, "dormant": 1}[v])
