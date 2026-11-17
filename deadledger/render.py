"""Renderers.

One :class:`~deadledger.audit.AuditResult` in, four artefacts out:

* **markdown** -- the ADR-ready mortality report.  Every claim carries a
  ``[src]`` marker resolved in a numbered sources table with the retrieval
  date, so a reviewer can check any sentence without trusting the tool.
* **text** -- the terminal summary.  Short, colour-free by default (colour is
  opt-in so logs are diffable), and always says how many criticals are dead.
* **json** -- the machine format, also what `--format json` writes for CI.
* **sarif 2.1.0** -- so a dead dependency appears in GitHub's Security tab
  next to CVEs.

Every renderer is deterministic: same ``AuditResult`` in, byte-identical out.
No timestamps are invented at render time (``generated_at`` comes from the
runner).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from . import RUBRIC_VERSION, __version__
from .audit import AuditResult, LedgerDiff, PackageReport
from .mortality import DEAD, DORMANT, THRESHOLDS, UNKNOWN
from .util import human_age, human_int, iso, iso_day

VERDICT_BADGES = {
    "thriving": "🟢 thriving",
    "coasting": "🟡 coasting",
    "dormant": "🟠 dormant",
    "dead": "🔴 dead",
    "unknown": "⚪ unknown",
}

VERDICT_LABEL = {
    "thriving": "thriving",
    "coasting": "coasting",
    "dormant": "dormant",
    "dead": "dead",
    "unknown": "unknown",
}


# ---------------------------------------------------------------------------
# Sources table: stable numbering so [src N] markers mean the same thing
# ---------------------------------------------------------------------------


class SourceIndex:
    """Collects citations and hands back stable ``[src N]`` markers."""

    def __init__(self) -> None:
        self._rows: list[dict[str, str]] = []
        self._index: dict[str, int] = {}

    def add(self, citation: str | None, *, note: str = "") -> str:
        if not citation:
            return ""
        if citation in self._index:
            return f"[src {self._index[citation]}]"
        url, _, retrieved = citation.partition(" (retrieved ")
        retrieved = retrieved.rstrip(")") if retrieved else ""
        self._rows.append({"url": url, "retrieved_at": retrieved, "note": note})
        number = len(self._rows)
        self._index[citation] = number
        return f"[src {number}]"

    def add_many(self, citations: Iterable[str], *, note: str = "") -> str:
        markers = [self.add(citation, note=note) for citation in citations]
        return " ".join(marker for marker in markers if marker)

    @property
    def rows(self) -> list[dict[str, str]]:
        return self._rows

    def table(self) -> str:
        if not self._rows:
            return "_No external sources were consulted._"
        lines = ["| # | Source | Retrieved |", "|---|---|---|"]
        for number, row in enumerate(self._rows, start=1):
            note = f" — {row['note']}" if row.get("note") else ""
            lines.append(f"| {number} | <{row['url']}>{note} | {row['retrieved_at']} |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def render_markdown(
    result: AuditResult,
    *,
    title: str | None = None,
    diff: LedgerDiff | None = None,
    include_packages: bool = True,
    max_minor: int | None = None,
) -> str:
    sources = SourceIndex()
    counts = result.counts()
    heading = title or _default_title(result)

    out: list[str] = []
    out.append(f"# {heading}")
    out.append("")
    out.append(
        f"**Verdict as of {iso_day(result.as_of)}** · ecosystem `{result.ecosystem}` · "
        f"{counts['total']} packages · rubric v{result.rubric_version} · "
        f"alternatives map v{result.map_version} · DeadLedger {__version__}"
    )
    out.append("")
    out.append(
        f"Audited `{_display_path(result.lockfile)}`. The report describes the tree as observed on "
        f"**{iso_day(result.as_of)}**; every claim below is followed by a source "
        f"marker resolved at the bottom."
    )
    out.append("")

    # -- executive summary -------------------------------------------------
    out.extend(_markdown_summary(result, sources, diff))
    out.append("")

    # -- the dead and the dying -------------------------------------------
    dead_or_dormant = [
        r for r in result.packages if r.verdict_name in (DEAD, DORMANT)
    ]
    dead_or_dormant.sort(key=lambda r: (0 if r.critical else 1, _verdict_rank(r), r.name))
    if dead_or_dormant:
        out.append("## What is dead or dying")
        out.append("")
        for report in dead_or_dormant:
            out.extend(_markdown_package(result, report, sources, depth=3))
    else:
        out.append("## What is dead or dying")
        out.append("")
        out.append(
            "Nothing. Every package in this tree either shows current maintenance "
            "activity or lacks the evidence to be called dead."
        )
        out.append("")

    # -- single maintainers ------------------------------------------------
    single = [
        r for r in result.packages if getattr(r.bus, "single_maintainer", False)
    ]
    out.append("## Bus factor: who is one person away from a fork")
    out.append("")
    out.append(
        "A package appears here when exactly one account committed to its public "
        "repository in the 12 months before retrieval. That is a fact about the "
        "repository, not a prediction."
    )
    out.append("")
    if single:
        out.append("| package | critical | last commit by that person | commits |")
        out.append("|---|---|---|---|")
        for report in sorted(single, key=lambda r: (not r.critical, r.name)):
            lead = report.bus.lead or "unknown"
            last = iso_day(report.bus.lead_last_activity) or "unknown"
            commits = _lead_commits(report)
            mark = sources.add_many(report.bus.citations)
            out.append(
                f"| `{report.name}` {mark} | {'yes' if report.critical else 'no'} | "
                f"{lead}, {last} | {commits} |"
            )
    else:
        out.append("No package in this tree had exactly one committer in the last year.")
    out.append("")

    # -- orphan simulation -------------------------------------------------
    critical = [r for r in result.packages if r.critical and r.orphan]
    out.append("## Orphan simulation: if this dies, who else uses it?")
    out.append("")
    out.append(
        "One line per critical (direct, non-dev) dependency. `exact` means the "
        "registry publishes a dependent count; `approximate` means the number is "
        "downloads or import sites, which measure use, not dependents."
    )
    out.append("")
    if critical:
        out.append("| package | if it dies | basis |")
        out.append("|---|---|---|")
        ranked = sorted(
            critical,
            key=lambda r: (r.orphan.usage if r.orphan and r.orphan.usage is not None else -1, r.name),
        )
        for report in ranked:
            assert report.orphan is not None
            mark = sources.add(report.orphan.citation)
            answer = report.orphan.answer.rstrip()
            out.append(
                f"| `{report.name}` | {answer} {mark} | "
                f"{report.orphan.reach_label}: {report.orphan.basis} |"
            )
    else:
        out.append("No critical dependencies were identified in this tree.")
    out.append("")

    # -- migration hints ---------------------------------------------------
    migrations = [r for r in result.packages if r.alternatives]
    if migrations:
        out.append("## Migration hints for dead and dormant criticals")
        out.append("")
        out.append(
            f"From the community alternatives map v{result.map_version} "
            f"(`maps/alternatives.json`). The cost label is a migration *proxy*: "
            f"`near drop-in` means the measured public API mostly overlaps, "
            f"`rewrite-shaped` means it does not. Entries with no measurement say so."
        )
        out.append("")
        for report in migrations:
            out.append(f"### {report.name}")
            out.append("")
            for alternative in report.alternatives:
                out.append(
                    f"- **{alternative['name']}** — {alternative['reason']} "
                    f"*Cost: {alternative['cost']}.*"
                )
                if alternative.get("notes"):
                    out.append(f"  - {alternative['notes']}")
                if alternative.get("basis"):
                    out.append(f"  - Basis: {alternative['basis']}")
                if alternative.get("links"):
                    links = ", ".join(f"<{link}>" for link in alternative["links"])
                    out.append(f"  - {links}")
            out.append("")
    else:
        out.append("## Migration hints for dead and dormant criticals")
        out.append("")
        out.append(
            "No dead or dormant *critical* dependency has an entry in the "
            "alternatives map yet. Adding one is a PR against `maps/alternatives.json`."
        )
        out.append("")

    # -- full table --------------------------------------------------------
    if include_packages:
        out.append("## Every package")
        out.append("")
        out.append(
            "`depth 0` is declared by this project. `critical` means direct and "
            "not dev. Verdicts without enough evidence say `unknown`."
        )
        out.append("")
        out.append("| package | version | verdict | critical | depth | last release | last commit | maintainers | bus factor |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        shown = result.packages
        if max_minor is not None:
            interesting = [r for r in shown if r.verdict_name not in ("thriving", "coasting")]
            shown = interesting
        for report in shown:
            metrics = report.verdict
            release = _fmt_day(_last_release(report))
            commit = _fmt_day(_last_commit(report))
            maintainers = _maintainer_count(report)
            bus = (
                str(report.bus.committers_12mo)
                if getattr(report.bus, "committers_12mo", None) is not None
                else "?"
            )
            critical = "yes" if report.critical else ("dev" if report.node.dev else "no")
            out.append(
                f"| `{report.name}` | {report.node.version or '?'} | "
                f"{VERDICT_BADGES.get(report.verdict_name, report.verdict_name)} | "
                f"{critical} | {report.depth if report.depth is not None else '?'} | "
                f"{release} | {commit} | {maintainers} | {bus} |"
            )
        out.append("")

    # -- limits of this report --------------------------------------------
    out.append("## What this report does not know")
    out.append("")
    gaps = _collect_gaps(result)
    if gaps:
        for gap in gaps:
            out.append(f"- {gap}")
    else:
        out.append("- No source gaps were recorded on this run; every package answered.")
    for warning in result.warnings:
        out.append(f"- {warning}")
    out.append("")
    out.append(
        f"Verdicts follow rubric v{RUBRIC_VERSION} (`docs/verdicts.md`). "
        f"Dormant means no stable release for {THRESHOLDS['dormant_after_days']} days; "
        f"dead means an archived repository, an explicit deprecation, or no release "
        f"for {THRESHOLDS['dead_after_days']} days. If you think a threshold is wrong, "
        f"that is a PR to the rubric, not a footnote."
    )
    out.append("")

    # -- sources -----------------------------------------------------------
    out.append("## Sources")
    out.append("")
    out.append(sources.table())
    out.append("")
    out.append(
        "_Retrieved-at dates are when DeadLedger first stored each response. "
        "Re-running offline reuses those dates rather than pretending the world "
        "was re-observed._"
    )
    out.append("")
    return "\n".join(out)


def _markdown_summary(
    result: AuditResult, sources: SourceIndex, diff: LedgerDiff | None
) -> list[str]:
    counts = result.counts()
    criticals = [r for r in result.packages if r.critical and r.verdict_name in (DEAD, DORMANT)]
    lines = ["## Summary", ""]
    lines.append(
        f"- **{counts['total']} packages** audited ({counts['critical']} critical: direct, non-dev; "
        f"{counts['total'] - counts['critical']} transitive or dev)."
    )
    lines.append(
        f"- **{counts['dead']} dead**, **{counts['dormant']} dormant**, "
        f"{counts['coasting']} coasting, {counts['thriving']} thriving, "
        f"{counts['unknown']} unknown."
    )
    if criticals:
        lines.append(
            f"- **{len(criticals)} critical package(s) need a decision**: "
            + ", ".join(f"`{r.name}` ({r.verdict_name})" for r in criticals)
            + "."
        )
    else:
        lines.append(
            "- **No critical dependency is dead or dormant.** The fragile parts of "
            "this tree are transitive or dev-only; see the table for details."
        )
    if counts["single_maintainer"]:
        lines.append(
            f"- **{counts['single_maintainer']} package(s) have a bus factor of 1** "
            f"in the last 12 months of commits."
        )
    if diff is not None:
        summary = diff.summary_line().rstrip(".")
        lines.append(f"- Ledger: {summary}.")
    lines.append("")
    lines.append("### The headline")
    lines.append("")
    # Critical-first, then severity. `result.packages` is sorted by severity
    # alone, so listing it directly led the report with a dormant transitive
    # dependency while a dead direct one sat further down -- and the headline
    # is the only part many readers read.
    headline = result.headline_findings(limit=5)
    if not headline:
        lines.append(
            "Nothing in this tree is dead by the rubric. The most interesting risk "
            "is concentration (single maintainers), covered below."
        )
        return lines
    for report in headline[:5]:
        if report.critical:
            lead = "critical"
        elif report.node.dev:
            lead = "dev-only"
        else:
            lead = f"transitive, depth {report.depth}"
        reasons = report.verdict.reasons[0] if report.verdict.reasons else ""
        mark = sources.add_many(report.verdict.citations())
        lines.append(f"- `{report.name}` **{report.verdict_name}** ({lead}) — {reasons} {mark}".rstrip())
    return lines


def _markdown_package(
    result: AuditResult, report: PackageReport, sources: SourceIndex, *, depth: int
) -> list[str]:
    hashes = "#" * depth
    verdict = report.verdict
    out = [f"{hashes} {report.name} {report.node.version or ''} — {VERDICT_BADGES.get(report.verdict_name, report.verdict_name)}".rstrip(), ""]
    out.append(
        f"*{report.node.ecosystem} · {_criticality_phrase(report)} · "
        f"verdict confidence: {verdict.confidence} · rubric v{verdict.rubric_version}*"
    )
    out.append("")
    if report.evidence.summary:
        out.append(f"{report.evidence.summary}")
        out.append("")
    out.append("**Evidence**")
    out.append("")
    for hit in verdict.rules:
        mark = sources.add_many(hit.citations)
        out.append(f"- {hit.claim} {mark}".rstrip())
        if hit.metrics:
            rendered = ", ".join(
                f"`{key}`={_fmt_metric(value)}" for key, value in hit.metrics if value is not None
            )
            if rendered:
                out.append(f"  - {rendered}")
    if report.orphan:
        mark = sources.add(report.orphan.citation)
        # When the number is unknown, the *gaps* are the basis and the table
        # already explains them; only quote a basis for a real measurement.
        basis = (
            f" _(basis: {report.orphan.basis})_"
            if report.orphan.reach_label != "unknown" and report.orphan.basis
            else ""
        )
        if report.orphan.reach_label == "unknown":
            line = f"- Orphan check: {report.orphan.answer}{basis}"
        else:
            line = f"- Orphan check ({report.orphan.reach_label}): {report.orphan.answer}{basis}"
        out.append(f"{line} {mark}".rstrip())
    out.append("")
    if verdict.evidence_gaps:
        out.append("**Gaps**")
        out.append("")
        for gap in verdict.evidence_gaps:
            out.append(f"- {gap}")
        out.append("")
    out.append(f"**What to do**")
    out.append("")
    out.extend(_advice(report, result))
    out.append("")
    return out


def _advice(report: PackageReport, result: AuditResult) -> list[str]:
    lines: list[str] = []
    if report.verdict_name == DEAD:
        if report.node.dev:
            lines.append("- Dev-only: nothing ships to production. Remove it when convenient.")
        elif not report.critical:
            lines.append(
                "- Transitive: pin the version you have, then track the parent that pulls it in."
            )
        else:
            lines.append(
                "- Critical: this is your decision. Fork, vendor, or migrate — the "
                "alternatives below are the starting point for that ADR."
            )
    elif report.verdict_name == DORMANT:
        if "R-DEVELOP-WITHOUT-RELEASE" in report.verdict.rule_ids:
            lines.append(
                "- Alive but not publishing: the fixes you want may already be on "
                "main. Pin a git ref (or ask for a release) before you fork."
            )
        else:
            lines.append(
                "- Dormant but not dead: pin a version, watch for a successor, and if you "
                "depend on bug fixes, budget a fork."
            )
    if getattr(report.bus, "single_maintainer", False):
        lines.append(
            f"- {report.bus.sentence()} Vendoring is cheaper than waiting for a crisis "
            f"if this package is critical."
        )
    if not lines:
        lines.append("- No action required by the rubric.")
    return lines


def _criticality_phrase(report: PackageReport) -> str:
    if report.critical:
        return "critical (direct, non-dev)"
    if report.node.dev:
        return "dev dependency"
    depth = report.depth
    return f"transitive, depth {depth}" if depth is not None else "transitive"


# ---------------------------------------------------------------------------
# Terminal
# ---------------------------------------------------------------------------


def render_text(result: AuditResult, *, colour: bool = False, verbose: bool = False) -> str:
    counts = result.counts()
    c = _colours(colour)
    lines: list[str] = []
    lines.append(
        f"{c['bold']}DeadLedger{c['reset']} — {result.ecosystem} · "
        f"{result.lockfile.name} · {counts['total']} package(s) · "
        f"as of {iso_day(result.as_of)} · rubric v{result.rubric_version}"
    )
    if result.warnings:
        for warning in result.warnings[:3]:
            lines.append(f"{c['dim']}{warning}{c['reset']}")
    lines.append("")
    bar = _bar(counts)
    lines.append(bar)
    lines.append("")
    criticals = [r for r in result.packages if r.critical and r.needs_attention]
    if criticals:
        lines.append(f"{c['bold']}{c['red']}Critical dependencies needing a decision{c['reset']}")
        for report in criticals:
            reason = report.verdict.reasons[0] if report.verdict.reasons else ""
            lines.append(f"  {_verdict_tag(report.verdict_name, c)} {report.name}")
            lines.append(f"    {reason}")
            if getattr(report.bus, "single_maintainer", False):
                lines.append(f"    {report.bus.sentence()}")
            for alternative in report.alternatives[:2]:
                lines.append(
                    f"    → {alternative['name']}: {alternative['cost']} "
                    f"(map v{result.map_version})"
                )
        lines.append("")
    transitives = [
        r for r in result.packages if r.needs_attention and not r.critical
    ]
    if transitives:
        label = "Transitive and dev-only mortality (not your decision today)"
        lines.append(f"{c['bold']}{label}{c['reset']}")
        for report in transitives[:12]:
            depth = f"depth {report.depth}" if report.depth is not None else "dev"
            lines.append(f"  {_verdict_tag(report.verdict_name, c)} {report.name} ({depth})")
        if len(transitives) > 12:
            lines.append(f"  … and {len(transitives) - 12} more (see --format markdown)")
        lines.append("")
    single = [r for r in result.packages if getattr(r.bus, "single_maintainer", False)]
    if single:
        lines.append(f"{c['bold']}Bus factor 1{c['reset']}")
        for report in single[:10]:
            last = iso_day(report.bus.lead_last_activity) or "unknown"
            lines.append(
                f"  {report.bus.lead or 'one account'} — last commit {last} — {report.name}"
                + (" (critical)" if report.critical else "")
            )
        if len(single) > 10:
            lines.append(f"  … and {len(single) - 10} more")
        lines.append("")
    if verbose:
        lines.append(f"{c['bold']}All packages{c['reset']}")
        for report in result.packages:
            depth = "direct" if report.depth == 0 else f"d{report.depth}"
            lines.append(
                f"  {_verdict_tag(report.verdict_name, c)} "
                f"{report.name}@{report.node.version or '?'} [{depth}]"
            )
        lines.append("")
    gaps = _collect_gaps(result)
    if gaps:
        lines.append(f"{c['dim']}{len(gaps)} source gap(s) — verdicts that say 'unknown' "
                     f"do so because evidence was missing, not because a package is healthy.{c['reset']}")
        for gap in gaps[:5]:
            lines.append(f"{c['dim']}  - {gap}{c['reset']}")
        if len(gaps) > 5:
            lines.append(f"{c['dim']}  … run `deadledger explain <package>` for details{c['reset']}")
        lines.append("")
    summary = result.client_summary
    if summary:
        lines.append(
            f"{c['dim']}{summary['calls']} queries · {summary['cache_hits']} cached · "
            f"{summary['live_fetches']} live · {summary['stale_urls']} stale · "
            f"{summary['failed_urls']} failed · mode {summary['mode']}{c['reset']}"
        )
    return "\n".join(lines)


def _bar(counts: dict[str, int]) -> str:
    total = max(1, counts["total"])
    parts = []
    for name, glyph in (
        ("thriving", "●"),
        ("coasting", "◐"),
        ("dormant", "○"),
        ("dead", "✕"),
        ("unknown", "?"),
    ):
        n = counts.get(name, 0)
        if n:
            parts.append(f"{glyph} {name} {n}")
    return " · ".join(parts) + f"   ({total} total)"


def _verdict_tag(verdict: str, colours: dict[str, str]) -> str:
    palette = {
        "thriving": "green",
        "coasting": "yellow",
        "dormant": "yellow",
        "dead": "red",
        "unknown": "dim",
    }
    return f"{colours[palette.get(verdict, 'dim')]}{verdict:<9}{colours['reset']}"


def _colours(enabled: bool) -> dict[str, str]:
    if not enabled:
        return {key: "" for key in ("bold", "red", "yellow", "green", "dim", "reset")}
    return {
        "bold": "\x1b[1m",
        "red": "\x1b[31m",
        "yellow": "\x1b[33m",
        "green": "\x1b[32m",
        "dim": "\x1b[2m",
        "reset": "\x1b[0m",
    }


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


def render_json(result: AuditResult, *, diff: LedgerDiff | None = None) -> dict[str, Any]:
    counts = result.counts()
    return {
        "schema": "deadledger/report/v1",
        "deadledger_version": __version__,
        "rubric_version": result.rubric_version,
        "alternatives_map_version": result.map_version,
        "generated_at": iso(result.generated_at),
        "as_of": iso(result.as_of),
        "ecosystem": result.ecosystem,
        "lockfile": str(result.lockfile),
        "project": result.project_name,
        "counts": counts,
        "warnings": result.warnings,
        "client": result.client_summary,
        "diff": None
        if diff is None
        else {
            "first_run": diff.is_first_run,
            "summary": diff.summary_line(),
            "new_deaths": [r.key for r in diff.new_deaths],
            "worsened": [r.key for r in diff.worsened],
            "recovered": [r.key for r in diff.recovered],
        },
        "packages": [_package_json(report) for report in result.packages],
        "sources": _json_sources(result),
    }


def _package_json(report: PackageReport) -> dict[str, Any]:
    evidence = report.evidence
    return {
        "key": report.key,
        "name": report.name,
        "version": report.node.version,
        "ecosystem": report.node.ecosystem,
        "dev": report.node.dev,
        "critical": report.critical,
        "depth": report.depth,
        "paths": report.paths,
        "parents": report.parents,
        "verdict": report.verdict_name,
        "confidence": report.verdict.confidence,
        "reasons": report.verdict.reasons,
        "rule_ids": report.verdict.rule_ids,
        "bus_factor": {
            "committers_12mo": getattr(report.bus, "committers_12mo", None),
            "lead": getattr(report.bus, "lead", None),
            "lead_last_activity": iso(getattr(report.bus, "lead_last_activity", None)),
            "single_maintainer": getattr(report.bus, "single_maintainer", False),
            "sentence": report.bus.sentence() if report.bus else None,
        },
        "orphan": None
        if report.orphan is None
        else {
            "answer": report.orphan.answer,
            "reach": report.orphan.reach_label,
            "usage": report.orphan.usage,
            "basis": report.orphan.basis,
            "citation": report.orphan.citation,
        },
        "alternatives": report.alternatives,
        "evidence": evidence.evidence_rows(),
        "repository": evidence.repository,
        "evidence_gaps": evidence.source_gaps,
    }


def _json_sources(result: AuditResult) -> list[dict[str, str]]:
    seen: dict[str, dict[str, str]] = {}
    for report in result.packages:
        for observation in report.evidence.observation_map().values():
            seen.setdefault(
                observation.url,
                {
                    "url": observation.url,
                    "retrieved_at": iso(observation.retrieved_at) or "",
                    "source": observation.source,
                },
            )
    return [seen[url] for url in sorted(seen)]


# ---------------------------------------------------------------------------
# SARIF
# ---------------------------------------------------------------------------


def render_sarif(result: AuditResult) -> dict[str, Any]:
    """SARIF 2.1.0 so dead dependencies show up in code-scanning UIs."""
    rules = [
        {
            "id": "deadledger/dead",
            "name": "DeadDependency",
            "shortDescription": {"text": "Dependency is dead"},
            "fullDescription": {
                "text": "The dependency has an archived repository, an explicit "
                "deprecation, or no release for four years."
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "deadledger/dormant",
            "name": "DormantDependency",
            "shortDescription": {"text": "Dependency is dormant"},
            "fullDescription": {"text": "No stable release for two years."},
            "defaultConfiguration": {"level": "warning"},
        },
        {
            "id": "deadledger/single-maintainer",
            "name": "SingleMaintainerDependency",
            "shortDescription": {"text": "Dependency has a bus factor of one"},
            "defaultConfiguration": {"level": "note"},
        },
    ]
    results: list[dict[str, Any]] = []
    for report in result.packages:
        if report.verdict_name not in (DEAD, DORMANT) and not getattr(
            report.bus, "single_maintainer", False
        ):
            continue
        rule_id = (
            "deadledger/dead"
            if report.verdict_name == DEAD
            else "deadledger/dormant"
            if report.verdict_name == DORMANT
            else "deadledger/single-maintainer"
        )
        results.append(
            {
                "ruleId": rule_id,
                "level": "error" if rule_id.endswith("dead") else "warning",
                "message": {
                    "text": " ".join(report.verdict.reasons[:2]) or report.verdict_name,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": str(result.lockfile)},
                        }
                    }
                ],
                "properties": {
                    "package": report.name,
                    "version": report.node.version,
                    "verdict": report.verdict_name,
                    "confidence": report.verdict.confidence,
                    "critical": report.critical,
                    "sources": list(report.verdict.citations()),
                },
            }
        )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "DeadLedger",
                        "informationUri": "https://github.com/pooria683/deadledger",
                        "version": __version__,
                        "rules": rules,
                    }
                },
                "invocations": [
                    {"executionSuccessful": True, "endTimeUtc": iso(result.generated_at)}
                ],
                "results": results,
            }
        ],
    }


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _default_title(result: AuditResult) -> str:
    project = result.project_name or _guess_project(result.lockfile)
    return f"Mortality report: {project}"


def _display_path(path: Any) -> str:
    """A stable, machine-independent name for the audited file.

    A committed report must not contain the absolute path of the machine that
    generated it.  It also should not depend on which directory the command was
    run from, or two contributors regenerate the same demo report and get two
    different headers.  So: relative to the project root (the nearest directory
    holding a ``.git`` or ``pyproject.toml``), falling back to the bare name.
    """
    resolved = Path(path).resolve()
    ancestry = [resolved.parent, *resolved.parents]
    # A `.git` boundary is authoritative; a bare pyproject.toml is a weaker
    # signal, and inside a checkout the demo trees carry the *original*
    # project's pyproject.toml (that is the point of a demo), which would
    # otherwise win and reduce the path to "poetry.lock".
    for parent in ancestry:
        if (parent / ".git").exists():
            try:
                return str(resolved.relative_to(parent))
            except ValueError:
                break
    for parent in ancestry:
        if (parent / "pyproject.toml").is_file():
            try:
                return str(resolved.relative_to(parent))
            except ValueError:
                break
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except (ValueError, OSError):
        return resolved.name


def _guess_project(path: Any) -> str:
    return path.parent.name or "this project"


def _verdict_rank(report: PackageReport) -> int:
    return 0 if report.verdict_name == DEAD else 1


def _last_release(report: PackageReport) -> datetime | None:
    observation = report.evidence.last_publish_obs
    if observation is None or observation.value is None:
        return None
    from .util import parse_datetime

    return parse_datetime(observation.value)


def _last_commit(report: PackageReport) -> datetime | None:
    observation = report.evidence.last_commit_obs
    if observation is None or observation.value is None:
        return None
    from .util import parse_datetime

    return parse_datetime(observation.value)


def _fmt_day(value: datetime | None) -> str:
    return iso_day(value) or "—"


def _fmt_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _maintainer_count(report: PackageReport) -> str:
    observation = report.evidence.maintainer_count_obs
    if observation is None or observation.value is None:
        return "?"
    return str(observation.value)


def _lead_commits(report: PackageReport) -> str:
    committers = report.evidence.committers
    if not committers:
        return "?"
    return str(committers[0].commits or "?")


def _collect_gaps(result: AuditResult) -> list[str]:
    gaps: list[str] = []
    for report in result.packages:
        for gap in report.evidence.source_gaps:
            text = f"`{report.name}`: {gap}"
            if text not in gaps:
                gaps.append(text)
    return gaps
