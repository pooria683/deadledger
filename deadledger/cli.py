"""The command line.

Commands, and the question each answers:

==========================  ==================================================
deadledger audit            "what in this tree is already dead?"
deadledger explain PKG      "why did you call this one dead?" (full evidence)
deadledger ci               "did anything die since the last run?"
deadledger ledger show      "what does the ledger remember?"
deadledger ledger reset     "forget everything, re-baseline"
deadledger cache info       "what is cached, how old, where is it?"
deadledger cache prune      "drop expired entries"
deadledger sources          "which APIs does each adapter use?"
deadledger map lint         "is the alternatives map valid?"
deadledger record           "re-record the shipped fixtures"
deadledger doctor           "is my environment able to audit?"
==========================  ==================================================

Exit codes are part of the interface:

===  ==========================================================================
0    success; in ``ci`` mode: no new mortality since the last run
1    a checking command found something (``ci``: new deaths; ``map lint``: errors)
2    usage or configuration error (no lockfile, bad flag, unreadable map)
3    the audit could not be completed (offline with an empty cache, etc.)
===  ==========================================================================

Nothing is ever uploaded: every request the CLI makes is a GET for public
package metadata, and the ledger and cache live under your working directory.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from . import RUBRIC_VERSION, __version__
from .adapters import ADAPTERS, get_adapter
from .alternatives import load_map, validate
from .audit import (
    AuditResult,
    Ledger,
    PackageReport,
    Runner,
    default_ledger_path,
    diff_against,
)
from .cache import Cache, default_db_path
from .errors import DeadLedgerError, NoLockfile, OfflineCacheMiss, SourceUnavailable
from .http import CachingClient, build_client, github_token
from .lockfiles import LOCKFILE_ORDER, detect_lockfile, parse_lockfile
from .mortality import THRESHOLDS, VERDICTS
from .render import render_json, render_markdown, render_sarif, render_text
from .util import human_age, human_int, iso, iso_day, slugify, utcnow

PROG = "deadledger"

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2
EXIT_INCOMPLETE = 3


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Mortality reports for dependency trees: for every direct and "
            "transitive dependency, the evidence of its aliveness and a "
            "plain-language verdict, each backed by a checkable citation."
        ),
        epilog=(
            "Start with `deadledger audit`. Reports are Markdown by default; "
            "`--format json|sarif` is for machines. Exit code 1 from `ci` means "
            "something NEW died since the last run, not that old deaths exist."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"{PROG} {__version__} (rubric v{RUBRIC_VERSION})")
    parser.add_argument(
        "--cache",
        metavar="PATH",
        help=f"SQLite cache file (default: {default_db_path()})",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="serve everything from the cache; never open a socket",
    )
    parser.add_argument(
        "--replay",
        metavar="PROFILE",
        help=(
            "replay recorded fixtures from tests/fixtures/PROFILE instead of the "
            "network. Used to regenerate the committed demo report."
        ),
    )
    parser.add_argument(
        "--no-color", action="store_true", help="disable ANSI colour in terminal output"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    audit = subparsers.add_parser(
        "audit",
        help="audit the lockfile in (or above) the current directory",
        description=(
            "Read the lockfile, collect evidence for every package, and print a "
            "mortality report. Works offline from the cache once a cache exists."
        ),
    )
    _add_audit_options(audit)
    audit.add_argument(
        "--ledger",
        metavar="PATH",
        help="also record this run in the ledger at PATH (default: .deadledger/ledger-<project>.json)",
    )
    audit.add_argument(
        "--no-ledger", action="store_true", help="do not touch the ledger"
    )

    ci = subparsers.add_parser(
        "ci",
        help="record the run and fail only on NEW deaths since the last run",
        description=(
            "The anti-fatigue command: the ledger remembers which deaths were "
            "already reported, so a build only fails when mortality is new."
        ),
    )
    _add_audit_options(ci)
    ci.set_defaults(format="text")
    ci.add_argument("--ledger", metavar="PATH", help="ledger file to use")
    ci.add_argument(
        "--report",
        metavar="PATH",
        help="write the full Markdown report to PATH even when the build passes",
    )
    ci.add_argument(
        "--sarif", metavar="PATH", help="also write a SARIF file for code scanning"
    )
    ci.add_argument(
        "--no-update-ledger",
        action="store_true",
        help="diff against the ledger without writing this run into it",
    )

    explain = subparsers.add_parser(
        "explain",
        help="show all evidence behind one package's verdict",
        description="Like `audit` for one package, with the raw citations printed.",
    )
    explain.add_argument("package", help="package name as it appears in the lockfile")
    explain.add_argument("--lockfile", metavar="PATH", help="lockfile to read")
    explain.add_argument("--ecosystem", choices=sorted(ADAPTERS), help="override ecosystem detection")
    explain.add_argument("--format", choices=("text", "json"), default="text")
    explain.add_argument("--version", dest="package_version", metavar="VERSION", help="pin a version")

    ledger = subparsers.add_parser("ledger", help="inspect or reset the local ledger")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", metavar="ACTION")
    show = ledger_sub.add_parser("show", help="print the ledger's remembered verdicts")
    show.add_argument("--ledger", metavar="PATH", help="ledger file")
    show.add_argument("--lockfile", metavar="PATH", help="lockfile, to derive the default ledger path")
    show.add_argument("--format", choices=("text", "json"), default="text")
    reset = ledger_sub.add_parser("reset", help="forget the ledger (re-baselines CI)")
    reset.add_argument("--ledger", metavar="PATH", help="ledger file")
    reset.add_argument("--lockfile", metavar="PATH", help="lockfile, to derive the default ledger path")
    reset.add_argument("--yes", action="store_true", help="do not ask for confirmation")

    cache = subparsers.add_parser("cache", help="inspect or prune the local cache")
    cache_sub = cache.add_subparsers(dest="cache_command", metavar="ACTION")
    cache_info = cache_sub.add_parser("info", help="show cache size, age and contents")
    cache_info.add_argument("--format", choices=("text", "json"), default="text")
    cache_sub.add_parser("prune", help="delete expired cache entries")
    cache_sub.add_parser("clear", help="delete the whole cache file")

    sources = subparsers.add_parser(
        "sources", help="list the registry APIs each adapter uses"
    )
    sources.add_argument("--format", choices=("text", "json"), default="text")

    map_parser = subparsers.add_parser("map", help="work with the alternatives map")
    map_sub = map_parser.add_subparsers(dest="map_command", metavar="ACTION")
    map_lint = map_sub.add_parser("lint", help="validate the alternatives map")
    map_lint.add_argument("--map", metavar="PATH", help="map file to lint")
    map_lint.add_argument("--format", choices=("text", "json"), default="text")
    map_show = map_sub.add_parser("show", help="print the map's metadata and entry count")
    map_show.add_argument("--map", metavar="PATH", help="map file")

    record = subparsers.add_parser(
        "record",
        help="re-record the shipped test fixtures from live APIs",
        description=(
            "Writes recorded API responses into tests/fixtures/<profile>/. "
            "The test suite replays these, so recording is the only step that "
            "needs the network."
        ),
    )
    record.add_argument("--profile", required=True, help="fixture profile name, e.g. saleor-2.11.1")
    record.add_argument("--lockfile", required=True, help="lockfile whose packages to record")
    record.add_argument("--fixture-root", metavar="PATH", help="where to write (default: tests/fixtures)")
    record.add_argument("--include-dev", action="store_true", help="also record dev dependencies")
    record.add_argument("--max-packages", type=int, default=0, help="stop after N packages (0 = all)")

    doctor = subparsers.add_parser(
        "doctor", help="check the environment: cache, token, map, lockfile"
    )
    doctor.add_argument("--format", choices=("text", "json"), default="text")

    return parser


def _add_audit_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--lockfile",
        metavar="PATH",
        help="lockfile to audit (default: auto-detect from the current directory upward)",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "text", "json", "sarif"),
        default="markdown",
        help="output format (default: markdown)",
    )
    parser.add_argument("-o", "--output", metavar="PATH", help="write the report to PATH instead of stdout")
    parser.add_argument(
        "--include-dev",
        action="store_true",
        help="audit dev dependencies too (they are parsed but excluded by default)",
    )
    parser.add_argument(
        "--no-forge",
        action="store_true",
        help="skip GitHub entirely: no bus factor, no triage rate",
    )
    parser.add_argument(
        "--only",
        metavar="NAMES",
        help="comma-separated package names to audit (others are skipped)",
    )
    parser.add_argument(
        "--map", metavar="PATH", help="alternatives map to use instead of the shipped one"
    )
    parser.add_argument(
        "--ci-summary",
        action="store_true",
        help="print the CI summary instead of the full report",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "any", "critical", "new"),
        default="none",
        help=(
            "exit 1 if the run finds deaths: 'any' (any dead package), "
            "'critical' (dead critical package), 'new' (new since the ledger). "
            "Default: none, because `audit` is for reading."
        ),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_OK
    try:
        return _dispatch(args)
    except NoLockfile as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except FileNotFoundError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except OfflineCacheMiss as exc:
        print(
            f"{PROG}: {exc}\n"
            f"  the cache at {_cache_path(args)} has no record of that URL.\n"
            f"  run once without --offline to build it.",
            file=sys.stderr,
        )
        return EXIT_INCOMPLETE
    except DeadLedgerError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return EXIT_INCOMPLETE
    except KeyboardInterrupt:
        print(f"\n{PROG}: interrupted; partial results are not written.", file=sys.stderr)
        return 130


def _dispatch(args: argparse.Namespace) -> int:
    command = args.command
    if command == "audit":
        return _cmd_audit(args)
    if command == "ci":
        return _cmd_ci(args)
    if command == "explain":
        return _cmd_explain(args)
    if command == "ledger":
        return _cmd_ledger(args)
    if command == "cache":
        return _cmd_cache(args)
    if command == "sources":
        return _cmd_sources(args)
    if command == "map":
        return _cmd_map(args)
    if command == "record":
        return _cmd_record(args)
    if command == "doctor":
        return _cmd_doctor(args)
    raise SystemExit(EXIT_USAGE)


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------


def _cache_path(args: argparse.Namespace) -> Path:
    return Path(args.cache).expanduser() if getattr(args, "cache", None) else default_db_path()


def _run_audit(args: argparse.Namespace, *, quiet: bool = False) -> tuple[AuditResult, Any]:
    lockfile = detect_lockfile(".", explicit=getattr(args, "lockfile", None))
    cache = Cache(_cache_path(args), create=True)
    replay = getattr(args, "replay", None)
    client = build_client(
        cache=cache,
        offline=getattr(args, "offline", False),
        mode="replay" if replay else "online",
        fixture_profile=replay,
    )
    alternatives = load_map(explicit=getattr(args, "map", None))
    inventory = parse_lockfile(lockfile)

    if getattr(args, "only", None):
        wanted = {name.strip().lower() for name in args.only.split(",") if name.strip()}
        keep = {
            key: node
            for key, node in inventory.nodes.items()
            if node.name.lower() in wanted
        }
        missing = wanted - {node.name.lower() for node in keep.values()}
        for name in sorted(missing):
            print(f"{PROG}: warning: --only {name!r} matched no package", file=sys.stderr)
        inventory.nodes = keep
        inventory.direct &= set(keep)
        inventory.edges = [
            edge for edge in inventory.edges if edge.child in keep and (edge.parent in keep or edge.parent is None)
        ]

    runner = Runner(
        client,
        alternatives=alternatives,
        include_dev=getattr(args, "include_dev", False),
        forge=not getattr(args, "no_forge", False),
    )
    result = runner.run(inventory)
    cache.close()
    if not quiet:
        _warn_about_gaps(result, client)
    return result, client


def _warn_about_gaps(result: AuditResult, client: Any) -> None:
    summary = client.summary()
    if summary["failed_urls"]:
        print(
            f"{PROG}: {summary['failed_urls']} source(s) did not answer; affected "
            f"evidence is reported as unknown rather than assumed healthy.",
            file=sys.stderr,
        )
    if summary["stale_urls"]:
        print(
            f"{PROG}: served {summary['stale_urls']} expired cache entrie(s) because "
            f"the source was unreachable; the report cites the original retrieval dates.",
            file=sys.stderr,
        )
    if summary["mode"] == "offline":
        print(f"{PROG}: offline mode, as of {iso(result.as_of)}", file=sys.stderr)


def _cmd_audit(args: argparse.Namespace) -> int:
    result, client = _run_audit(args)
    ledger_path = None
    diff = None
    if not getattr(args, "no_ledger", False):
        ledger_path = _ledger_path(args, result)
        ledger = Ledger.load(ledger_path, result.project_name or result.lockfile.parent.name)
        diff = diff_against(ledger, result.packages)
        ledger.record(result.packages, when=result.as_of)
        ledger.save(ledger_path)

    payload = _render(args.format, result, diff=diff)
    _emit(payload, getattr(args, "output", None))
    if not getattr(args, "output", None) and args.format == "markdown":
        print(
            f"\n_{len(result.packages)} packages audited. Ledger: "
            f"{ledger_path or 'disabled'}._",
            file=sys.stderr,
        )
    return _fail_on_status(args, result, diff)


def _render(fmt: str, result: AuditResult, *, diff: Any = None) -> str:
    if fmt == "markdown":
        return render_markdown(result, diff=diff)
    if fmt == "json":
        return json.dumps(render_json(result, diff=diff), indent=2, sort_keys=False) + "\n"
    if fmt == "sarif":
        return json.dumps(render_sarif(result), indent=2) + "\n"
    return render_text(result)


def _emit(payload: str, output: str | None) -> None:
    if output:
        path = Path(output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        print(f"{PROG}: wrote {path}", file=sys.stderr)
    else:
        sys.stdout.write(payload)
        if not payload.endswith("\n"):
            sys.stdout.write("\n")


def _fail_on_status(args: argparse.Namespace, result: AuditResult, diff: Any) -> int:
    mode = getattr(args, "fail_on", "none")
    if mode == "none":
        return EXIT_OK
    if mode == "any" and any(r.is_dead for r in result.packages):
        return EXIT_FINDINGS
    if mode == "critical" and any(r.is_dead and r.critical for r in result.packages):
        return EXIT_FINDINGS
    if mode == "new" and diff is not None and diff.has_new_risk:
        return EXIT_FINDINGS
    return EXIT_OK


# ---------------------------------------------------------------------------
# ci
# ---------------------------------------------------------------------------


def _cmd_ci(args: argparse.Namespace) -> int:
    result, client = _run_audit(args, quiet=True)
    ledger_path = _ledger_path(args, result)
    ledger = Ledger.load(ledger_path, result.project_name or result.lockfile.parent.name)
    previous_rubric = None
    diff = diff_against(ledger, result.packages, previous_rubric=previous_rubric)
    if not getattr(args, "no_update_ledger", False):
        ledger.record(result.packages, when=result.as_of)
        ledger.save(ledger_path)

    if getattr(args, "sarif", None):
        path = Path(args.sarif).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(render_sarif(result), indent=2) + "\n", encoding="utf-8")

    if getattr(args, "report", None) or diff.has_new_risk:
        path = Path(getattr(args, "report", None) or "deadledger-report.md")
        path.write_text(render_markdown(result, diff=diff), encoding="utf-8")

    if args.format == "json":
        payload = json.dumps(render_json(result, diff=diff), indent=2) + "\n"
    elif args.format == "markdown":
        payload = render_markdown(result, diff=diff)
    else:
        payload = _ci_summary(result, diff)
    sys.stdout.write(payload if payload.endswith("\n") else payload + "\n")

    failing = list(diff.new_deaths) + list(diff.worsened)
    if diff.is_first_run:
        print(
            f"{PROG}: first run for this project; baseline recorded at {ledger_path}.\n"
            f"  {len(result.attention())} package(s) are already dead or dormant. "
            f"Future runs fail only on NEW mortality.",
            file=sys.stderr,
        )
        return EXIT_OK
    if failing:
        print(
            f"{PROG}: {len(failing)} NEW mortality finding(s) since {ledger.last_run}. "
            f"Ledger updated at {ledger_path}.",
            file=sys.stderr,
        )
        return EXIT_FINDINGS
    print(
        f"{PROG}: no new mortality since {ledger.last_run}; "
        f"{len(result.attention())} known finding(s) unchanged.",
        file=sys.stderr,
    )
    return EXIT_OK


def _ci_summary(result: AuditResult, diff: Any) -> str:
    counts = result.counts()
    lines = [
        f"DeadLedger CI — {result.ecosystem} · {result.lockfile.name} · as of {iso_day(result.as_of)}",
        f"  {counts['dead']} dead · {counts['dormant']} dormant · "
        f"{counts['thriving']} thriving · {counts['coasting']} coasting · "
        f"{counts['unknown']} unknown",
    ]
    if diff.is_first_run:
        lines.append("  first run: baseline recorded, nothing to compare against yet")
        return "\n".join(lines)
    previous = getattr(diff, "previous_run", None)
    when = f" (last run {previous})" if previous else ""
    lines.append(f"  ledger: {diff.summary_line().rstrip('.')}{when}")
    for report in diff.new_deaths:
        lines.append(f"  NEW DEATH  {report.name}@{report.node.version or '?'} ({report.verdict_name})")
        for reason in report.verdict.reasons[:2]:
            lines.append(f"             {reason}")
    for report in diff.worsened:
        lines.append(f"  WORSENED   {report.name}@{report.node.version or '?'} ({report.verdict_name})")
    for report in diff.recovered:
        lines.append(f"  RECOVERED  {report.name}@{report.node.version or '?'} ({report.verdict_name})")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# explain
# ---------------------------------------------------------------------------


def _cmd_explain(args: argparse.Namespace) -> int:
    lockfile = detect_lockfile(".", explicit=args.lockfile)
    inventory = parse_lockfile(lockfile)
    wanted = args.package.lower()
    matches = [
        node
        for node in inventory.nodes.values()
        if node.name.lower() == wanted
        or f"{node.name}@{node.version}".lower() == wanted
        or (args.package_version and node.name.lower() == wanted and node.version == args.package_version)
    ]
    if not matches:
        close = sorted(
            node.name for node in inventory.nodes.values() if wanted in node.name.lower()
        )[:5]
        print(f"{PROG}: {args.package!r} is not in {lockfile.name}", file=sys.stderr)
        if close:
            print(f"  did you mean: {', '.join(close)}", file=sys.stderr)
        return EXIT_USAGE

    node = matches[0]
    # `explain` is a question about one package. Auditing the whole tree first
    # made it take minutes on a 140-package lockfile -- and spend the entire
    # GitHub search budget answering a question nobody asked.
    inventory.nodes = {node.key: node}
    inventory.direct &= {node.key}
    inventory.edges = [
        edge for edge in inventory.edges if edge.child == node.key or edge.parent == node.key
    ]
    cache = Cache(_cache_path(args), create=True)
    client = build_client(
        cache=cache,
        offline=args.offline,
        mode="replay" if getattr(args, "replay", None) else "online",
        fixture_profile=getattr(args, "replay", None),
    )
    runner = Runner(client, alternatives=load_map())
    result = runner.run(inventory)
    cache.close()
    report = next((r for r in result.packages if r.key == node.key), None)
    if report is None:
        print(f"{PROG}: {node.key} was filtered out of the audit", file=sys.stderr)
        return EXIT_USAGE
    if args.format == "json":
        sys.stdout.write(json.dumps(_explain_json(report, result), indent=2) + "\n")
        return EXIT_OK
    sys.stdout.write(_explain_text(report, result) + "\n")
    return EXIT_OK


def _explain_text(report: PackageReport, result: AuditResult) -> str:
    lines = [
        f"{report.name} {report.node.version or ''} — {report.verdict_name.upper()} "
        f"(confidence: {report.verdict.confidence})",
        f"  ecosystem: {report.node.ecosystem}   lockfile: {result.lockfile}",
        f"  criticality: {'critical (direct, non-dev)' if report.critical else 'not critical'}"
        f"   depth: {report.depth if report.depth is not None else 'unknown'}"
        f"   paths: {report.paths}",
    ]
    if report.parents:
        lines.append(f"  pulled in by: {', '.join(report.parents[:6])}")
    lines.append("")
    lines.append("Why:")
    for hit in report.verdict.rules:
        lines.append(f"  [{hit.rule_id}] {hit.claim}")
        for citation in hit.citations:
            lines.append(f"      {citation}")
    if report.verdict.evidence_gaps:
        lines.append("")
        lines.append("Gaps (facts we could not obtain):")
        for gap in report.verdict.evidence_gaps:
            lines.append(f"  - {gap}")
    lines.append("")
    lines.append("Evidence table:")
    rows = report.evidence.evidence_rows()
    if not rows:
        lines.append("  (none)")
    for row in rows:
        lines.append(f"  {row['metric']:<26} {row['value']!s:<18} {row['citation']}")
    if report.bus:
        lines.append("")
        lines.append(f"Bus factor: {report.bus.sentence()}")
    if report.orphan:
        lines.append("")
        lines.append(f"Orphan check: {report.orphan.answer}")
        lines.append(f"  basis: {report.orphan.basis} [{report.orphan.reach_label}]")
    if report.alternatives:
        lines.append("")
        lines.append("Migration options:")
        for alternative in report.alternatives:
            lines.append(f"  - {alternative['name']}: {alternative['cost']}")
            lines.append(f"    {alternative['reason']}")
    return "\n".join(lines)


def _explain_json(report: PackageReport, result: AuditResult) -> dict[str, Any]:
    payload = render_json(result)
    entry = next(item for item in payload["packages"] if item["key"] == report.key)
    return {
        "schema": "deadledger/explain/v1",
        "rubric_version": result.rubric_version,
        "as_of": iso(result.as_of),
        "package": entry,
        "rules": [
            {"rule_id": hit.rule_id, "claim": hit.claim, "citations": list(hit.citations)}
            for hit in report.verdict.rules
        ],
    }


# ---------------------------------------------------------------------------
# ledger
# ---------------------------------------------------------------------------


def _ledger_path(args: argparse.Namespace, result: AuditResult | None = None) -> Path:
    explicit = getattr(args, "ledger", None)
    if explicit:
        return Path(explicit).expanduser()
    if result is not None:
        return default_ledger_path(
            result.project_name or result.lockfile.parent.name, result.ecosystem
        )
    lockfile = detect_lockfile(".", explicit=getattr(args, "lockfile", None))
    inventory = parse_lockfile(lockfile)
    name = inventory.project_name or lockfile.parent.name
    return default_ledger_path(name, inventory.ecosystem)


def _cmd_ledger(args: argparse.Namespace) -> int:
    action = getattr(args, "ledger_command", None)
    if action is None:
        print(f"{PROG}: ledger needs an action: show | reset", file=sys.stderr)
        return EXIT_USAGE
    path = _ledger_path(args)
    if action == "show":
        ledger = Ledger.load(path, path.stem)
        if args.format == "json":
            payload = {
                "path": str(path),
                "project": ledger.project,
                "runs": ledger.runs,
                "last_run": ledger.last_run,
                "entries": [entry.as_dict() for entry in ledger.entries.values()],
            }
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            return EXIT_OK
        if not ledger.entries:
            print(f"{PROG}: no ledger yet at {path}")
            print("  run `deadledger audit` or `deadledger ci` to create one.")
            return EXIT_OK
        print(f"Ledger: {path}")
        print(f"  project: {ledger.project}   runs: {ledger.runs}   last: {ledger.last_run}")
        print("")
        print(f"  {'verdict':<10} {'package':<40} {'first seen':<12} {'last seen':<12} rules")
        for entry in sorted(ledger.entries.values(), key=lambda e: (e.verdict, e.name)):
            print(
                f"  {entry.verdict:<10} {entry.name:<40} {entry.first_seen:<12} "
                f"{entry.last_seen:<12} {','.join(entry.rule_ids)}"
            )
        return EXIT_OK
    if action == "reset":
        if not path.exists():
            print(f"{PROG}: nothing to reset at {path}")
            return EXIT_OK
        if not args.yes:
            answer = input(f"Delete {path}? This re-baselines CI. [y/N] ").strip().lower()
            if answer not in {"y", "yes"}:
                print("kept.")
                return EXIT_OK
        path.unlink()
        print(f"reset: {path} removed.")
        return EXIT_OK
    return EXIT_USAGE


# ---------------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------------


def _cmd_cache(args: argparse.Namespace) -> int:
    action = getattr(args, "cache_command", None)
    path = _cache_path(args)
    if action is None:
        action = "info"
    if action == "clear":
        if path.exists():
            shutil.rmtree(path.parent) if path.parent.name == ".deadledger" else path.unlink()
            print(f"{PROG}: cache cleared ({path})")
        else:
            print(f"{PROG}: no cache at {path}")
        return EXIT_OK
    if not path.exists():
        # `info` on a cache that was never built is not an error: it is the
        # answer ("empty"), and CI jobs inspecting a fresh runner should get 0.
        if action == "info":
            if getattr(args, "format", "text") == "json":
                sys.stdout.write(
                    json.dumps(
                        {
                            "path": str(path),
                            "entries": 0,
                            "fresh": 0,
                            "expired": 0,
                            "bytes": 0,
                            "oldest": None,
                            "newest": None,
                            "by_kind": {},
                            "exists": False,
                        },
                        indent=2,
                    )
                    + "\n"
                )
            else:
                print(f"Cache: {path} (not created yet -- run an audit to build it)")
            return EXIT_OK
        print(f"{PROG}: no cache at {path}")
        return EXIT_OK
    cache = Cache(path, create=True)
    if action == "prune":
        removed = cache.purge_expired()
        print(f"pruned {removed} expired entrie(s) from {path}")
        cache.close()
        return EXIT_OK
    stats = cache.stats()
    cache.close()
    if getattr(args, "format", "text") == "json":
        sys.stdout.write(json.dumps(stats, indent=2) + "\n")
        return EXIT_OK
    print(f"Cache: {stats['path']}")
    print(f"  {stats['entries']} entries ({stats['fresh']} fresh, {stats['expired']} expired)")
    print(f"  {stats['bytes'] / 1024:.1f} KiB")
    print(f"  oldest: {stats['oldest'] or '—'}   newest: {stats['newest'] or '—'}")
    if stats["by_kind"]:
        print("  by source: " + ", ".join(f"{k}={v}" for k, v in stats["by_kind"].items()))
    return EXIT_OK


# ---------------------------------------------------------------------------
# sources / map / record / doctor
# ---------------------------------------------------------------------------


def _cmd_sources(args: argparse.Namespace) -> int:
    rows = []
    for name, adapter in sorted(ADAPTERS.items()):
        rows.append(
            {
                "ecosystem": name,
                "lockfiles": list(adapter.lockfile_names),
                "downloads": adapter.capabilities.downloads,
                "dependents": adapter.capabilities.dependents,
                "owners": adapter.capabilities.owners,
                "advisories": adapter.capabilities.advisories,
                "usage_method": adapter.capabilities.usage_method,
            }
        )
    if args.format == "json":
        sys.stdout.write(json.dumps(rows, indent=2) + "\n")
        return EXIT_OK
    print("Adapters and what each ecosystem can tell us:")
    for row in rows:
        print(f"\n  {row['ecosystem']}")
        print(f"    lockfiles:  {', '.join(row['lockfiles'])}")
        caps = [
            label
            for label, key in (
                ("downloads", "downloads"),
                ("dependents", "dependents"),
                ("owners", "owners"),
                ("advisories", "advisories"),
            )
            if row[key]
        ]
        print(f"    signals:    {', '.join(caps) or 'none'}")
        print(f"    usage:      {row['usage_method']}")
    print("\nAll adapters also use GitHub for bus factor and issue triage when the")
    print("package declares a public repository.")
    return EXIT_OK


def _cmd_map(args: argparse.Namespace) -> int:
    action = getattr(args, "map_command", None)
    if action is None:
        print(f"{PROG}: map needs an action: lint | show", file=sys.stderr)
        return EXIT_USAGE
    path = Path(args.map).expanduser() if getattr(args, "map", None) else None
    if path is None:
        from .alternatives import default_map_path

        path = default_map_path()
    if path is None or not path.is_file():
        print(f"{PROG}: no alternatives map found", file=sys.stderr)
        return EXIT_USAGE
    document = json.loads(path.read_text(encoding="utf-8"))
    if action == "show":
        meta = document.get("_meta") or {}
        entries = document.get("entries") or []
        print(f"map: {path}")
        print(f"  version: {meta.get('version')}   updated: {meta.get('updated_at')}")
        print(f"  entries: {len(entries)}")
        from collections import Counter

        by_eco = Counter(str(entry.get("ecosystem")) for entry in entries)
        print("  by ecosystem: " + ", ".join(f"{k}={v}" for k, v in sorted(by_eco.items())))
        return EXIT_OK
    problems = validate(document)
    if getattr(args, "format", "text") == "json":
        sys.stdout.write(json.dumps({"path": str(path), "problems": problems}, indent=2) + "\n")
    elif problems:
        print(f"{PROG}: {len(problems)} problem(s) in {path}")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print(f"ok: {path} is a valid alternatives map ({len(document.get('entries') or [])} entries)")
    return EXIT_FAILURE if problems else EXIT_OK


def _cmd_record(args: argparse.Namespace) -> int:
    """Record fixtures in two passes.

    Pass 1 runs the real adapters live, capturing every JSON document and every
    failure.  Pass 2 replays through the *same* adapter code with those
    documents, and only the URLs pass 2 asks for are written.  That keeps the
    fixture set to what an audit genuinely consumes (small) and proves the
    replay path works before the fixtures are committed.
    """
    from .http import (
        FIXTURE_ROOT,
        PlaybackClient,
        build_client as _build,
        canonical_fixture_url,
        write_failure,
        write_fixture,
    )

    lockfile = detect_lockfile(".", explicit=args.lockfile)
    inventory = parse_lockfile(lockfile)
    root = Path(args.fixture_root) if args.fixture_root else FIXTURE_ROOT
    cache = Cache(_cache_path(args), create=True)

    nodes = [n for n in inventory.nodes.values() if args.include_dev or not n.dev]
    nodes.sort(key=lambda n: n.name)
    if args.max_packages:
        nodes = nodes[: args.max_packages]

    # ---- pass 1: live, remembering responses ---------------------------------
    # Recording is a deliberate, human-attended crawl of hundreds of URLs; the
    # per-audit network deadline that keeps CI from hanging does not apply.
    os.environ.setdefault("DEADLEDGER_NETWORK_DEADLINE", "0")
    live = _build(cache=cache, mode="online")
    documents: dict[str, Any] = {}
    failures: dict[str, str] = {}
    recorder = _RecordingClient(live, documents, failures)
    print(
        f"{PROG}: pass 1/2 recording {len(nodes)} package(s) live "
        f"into profile {args.profile!r}",
        file=sys.stderr,
    )
    _exercise(nodes, recorder, args, progress=True)
    cache.close()
    print(
        f"{PROG}:   captured {len(documents)} response(s), {len(failures)} failure(s)",
        file=sys.stderr,
    )

    # ---- pass 2: replay, discovering what an audit needs ---------------------
    #
    # The replay client is given a *fresh* cache so the fixtures' recorded-at
    # timestamps stay visible, and it is never told a rate limit exists: it is
    # not making requests, so a budget makes no sense and "0 remaining" would
    # silently drop sources.
    playback_cache = Cache(":memory:")
    playback = PlaybackClient(documents, failures)
    replay_client = CachingClient(playback, playback_cache, mode="record", profile=args.profile)
    print(f"{PROG}: pass 2/2 replaying to find the URLs a real audit uses", file=sys.stderr)
    _exercise(nodes, replay_client, args, progress=False)

    written = 0
    gaps = 0
    canonical_docs = {canonical_fixture_url(u) for u in documents}
    canonical_fails = {canonical_fixture_url(u): r for u, r in failures.items()}
    for url in dict.fromkeys(playback.asked):
        canonical = canonical_fixture_url(url)
        if canonical in canonical_docs:
            write_fixture(root, args.profile, url, replay_client_last(recorder, url))
            written += 1
        else:
            write_failure(root, args.profile, url, canonical_fails.get(canonical, "not recorded"))
            gaps += 1
    print(
        f"{PROG}: recorded {written} response(s) and {gaps} gap(s) into {root / args.profile}",
        file=sys.stderr,
    )
    print(
        f"{PROG}: tests replay this profile with no network; re-run this command when "
        f"an API changes shape.",
        file=sys.stderr,
    )
    return EXIT_OK


class _RecordingClient:
    """Wraps a live client and remembers the response for each URL."""

    def __init__(self, inner: Any, documents: dict, failures: dict):
        self.inner = inner
        self.documents = documents
        self.failures = failures
        # Delegate the budget bookkeeping the adapters expect from a client.
        for attribute in ("consume", "budget", "learn_rate_limits", "summary", "mode"):
            if hasattr(inner, attribute):
                setattr(self, attribute, getattr(inner, attribute))
        self.mode = getattr(inner, "mode", "online")

    def get_json(self, url: str, **kwargs: Any) -> Any:
        try:
            fetched = self.inner.get_json(url, **kwargs)
        except SourceUnavailable as exc:
            self.failures[url] = str(exc)
            raise
        self.documents[url] = fetched.payload
        self._fetched = fetched
        return fetched


def replay_client_last(recorder: Any, url: str) -> Any:
    """Rebuild the Fetched for a recorded URL (canonical matching applies)."""
    from .http import Fetched, canonical_fixture_url
    from .util import parse_datetime, utcnow

    canonical = canonical_fixture_url(url)
    payload = recorder.documents.get(url)
    if payload is None:
        for candidate, body in recorder.documents.items():
            if canonical_fixture_url(candidate) == canonical:
                payload = body
                break
    if payload is None:
        payload = {}
    when = getattr(recorder, "recorded_at", None) or utcnow()
    return Fetched(url=url, payload=payload, fetched_at=when)


def _exercise(
    nodes: list, client: Any, args: argparse.Namespace, *, progress: bool
) -> list[str]:
    """Run every adapter (and the forge stage) exactly as a real audit does.

    This must mirror ``audit.Runner.run``: gather evidence, then attach forge
    facts when the registry yielded a repository.  Pass 2 replays these same
    calls to decide which URLs belong in the fixtures, so any step this
    function forgets shows up later as a recorded *gap* -- which is how the
    first version of this command shipped a profile with no commit history.
    """
    from .adapters import get_adapter
    from .forge import attach_repo_facts, fetch_repo_facts

    total = len(nodes)
    for index, node in enumerate(nodes, start=1):
        adapter = get_adapter(node.ecosystem)
        evidence = adapter.gather(client, node.name, node.version)
        if evidence.repository:
            facts = fetch_repo_facts(client, evidence.repository)
            attach_repo_facts(evidence, facts)
        if progress:
            print(f"  [{index}/{total}] {node.ecosystem}:{node.name}", file=sys.stderr)
    if progress and not nodes:
        print("  (no packages)", file=sys.stderr)
    return [node.key for node in nodes]


def _cmd_doctor(args: argparse.Namespace) -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: str, *, hint: str = "") -> None:
        checks.append({"check": name, "ok": ok, "detail": detail, "hint": hint})

    cache_path = _cache_path(args)
    try:
        cache = Cache(cache_path, create=True)
        stats = cache.stats()
        cache.close()
        check("cache", True, f"{stats['entries']} entries at {cache_path}")
    except Exception as exc:  # noqa: BLE001 - doctor must not crash
        check("cache", False, f"unusable: {exc}", hint="check permissions or pass --cache PATH")

    token = github_token()
    check(
        "github token",
        token is not None,
        "available" if token else "not set",
        hint="export GITHUB_TOKEN to enable bus factor, triage rate and offline code search"
        if not token
        else "",
    )
    try:
        lockfile = detect_lockfile(".")
        inventory = parse_lockfile(lockfile)
        check(
            "lockfile",
            True,
            f"{lockfile.name}: {len(inventory.nodes)} packages, {len(inventory.edges)} edges",
        )
    except NoLockfile as exc:
        check("lockfile", False, str(exc), hint="run deadledger from your project root")
    except Exception as exc:  # noqa: BLE001
        check("lockfile", False, f"unreadable: {exc}")

    try:
        include_user = True
        alternative_map = load_map(include_user=include_user)
        check(
            "alternatives map",
            bool(alternative_map.entries),
            alternative_map.describe(),
            hint="" if alternative_map.entries else "reinstall, the shipped map is missing",
        )
    except Exception as exc:  # noqa: BLE001
        check("alternatives map", False, f"invalid: {exc}")

    try:
        import httpx  # noqa: F401

        transport = "httpx"
    except ModuleNotFoundError:
        transport = "urllib fallback"
    check("transport", True, transport, hint="" if transport == "httpx" else "pip install httpx")

    if getattr(args, "format", "text") == "json":
        sys.stdout.write(json.dumps({"version": __version__, "checks": checks}, indent=2) + "\n")
        return EXIT_OK
    print(f"{PROG} {__version__} · rubric v{RUBRIC_VERSION}")
    for item in checks:
        mark = "ok  " if item["ok"] else "FAIL"
        print(f"  [{mark}] {item['check']:<18} {item['detail']}")
        if item["hint"] and not item["ok"]:
            print(f"         hint: {item['hint']}")
    failed = [item for item in checks if not item["ok"]]
    print("")
    if failed:
        print(f"{len(failed)} check(s) need attention; audits may degrade to 'unknown'.")
        return EXIT_FINDINGS
    print("Environment looks usable.")
    return EXIT_OK


EXIT_FAILURE = 1


def console_entry() -> None:  # pragma: no cover - packaging shim
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
