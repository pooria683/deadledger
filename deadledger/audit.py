"""The audit engine: inventory -> evidence -> verdicts -> report data.

This module owns two things people depend on:

* **The clock.**  Every verdict is computed against a single ``as_of``
  instant.  Online it is the moment the hardest evidence was retrieved;
  offline it is the newest retrieval recorded in the cache.  That is what
  makes a re-run from cache reproduce byte-identical verdicts (and what makes
  ``--offline`` honest: you see the world as of when you last looked).
* **The ledger.**  One JSON file per project recording the verdict history.
  CI mode diffs the new run against it, so a build fails on *new* deaths and
  stays quiet about the ones it already reported (Requirement 7).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from . import RUBRIC_VERSION, __version__
from .adapters import ADAPTERS, get_adapter
from .alternatives import AlternativeMap, load_map
from .errors import EvidenceUnavailable, NotFound, SourceUnavailable
from .evidence import PackageEvidence
from .forge import attach_repo_facts, fetch_repo_facts
from .graph import GraphAnalysis, analyse, depth_label, reachability_sentence
from .http import CachingClient
from .lockfiles import Inventory, Node, parse_lockfile
from .mortality import (
    DEAD,
    DORMANT,
    SEVERITY,
    THRESHOLDS,
    UNKNOWN,
    Verdict,
    bus_factor,
    derive_metrics,
    evaluate,
)
from .orphans import OrphanAnswer, simulate
from .util import iso, iso_day, json_dumps_stable, slugify, utcnow

LEDGER_VERSION = 1


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class PackageReport:
    node: Node
    evidence: PackageEvidence
    verdict: Verdict
    depth: int | None
    paths: int
    parents: list[str]
    critical: bool
    bus: Any = None
    orphan: OrphanAnswer | None = None
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    @property
    def key(self) -> str:
        return self.node.key

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def verdict_name(self) -> str:
        return self.verdict.verdict

    @property
    def is_dead(self) -> bool:
        return self.verdict.verdict == DEAD

    @property
    def is_dormant(self) -> bool:
        return self.verdict.verdict == DORMANT

    @property
    def needs_attention(self) -> bool:
        return self.verdict.verdict in (DEAD, DORMANT)


@dataclass
class AuditResult:
    ecosystem: str
    lockfile: Path
    as_of: datetime
    packages: list[PackageReport]
    graph: GraphAnalysis
    inventory: Inventory
    map_version: str
    warnings: list[str] = field(default_factory=list)
    client_summary: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime | None = None
    project_name: str | None = None
    rubric_version: str = RUBRIC_VERSION

    # -- derived views -----------------------------------------------------

    def by_verdict(self) -> dict[str, list[PackageReport]]:
        buckets: dict[str, list[PackageReport]] = {}
        for report in self.packages:
            buckets.setdefault(report.verdict_name, []).append(report)
        for items in buckets.values():
            items.sort(key=lambda r: (SEVERITY[r.verdict_name], r.name))
        return buckets

    def counts(self) -> dict[str, int]:
        counts = {"total": len(self.packages)}
        for name in ("thriving", "coasting", "dormant", "dead", "unknown"):
            counts[name] = 0
        for report in self.packages:
            counts[report.verdict_name] = counts.get(report.verdict_name, 0) + 1
        counts["critical"] = sum(1 for r in self.packages if r.critical)
        counts["critical_dead"] = sum(1 for r in self.packages if r.critical and r.is_dead)
        counts["critical_dormant"] = sum(
            1 for r in self.packages if r.critical and r.is_dormant
        )
        counts["single_maintainer"] = sum(
            1 for r in self.packages if getattr(r.bus, "single_maintainer", False)
        )
        return counts

    def headline_findings(self, limit: int = 5) -> list[PackageReport]:
        interesting = [
            r
            for r in self.packages
            if r.verdict_name in (DEAD, DORMANT) and r.critical
        ]
        interesting.sort(
            key=lambda r: (
                SEVERITY[r.verdict_name] * -1,
                r.verdict.as_of or self.as_of,
                r.name,
            ),
            reverse=False,
        )
        return interesting[:limit]

    def attention(self) -> list[PackageReport]:
        return [r for r in self.packages if r.needs_attention]

    def evidence_fingerprint(self) -> str:
        payload = [
            [r.key, r.verdict_name, r.verdict.rule_ids, _evidence_digest(r.evidence)]
            for r in sorted(self.packages, key=lambda r: r.key)
        ]
        return json_dumps_stable(payload)


def _evidence_digest(evidence: PackageEvidence) -> list[Any]:
    rows = []
    for name, observation in sorted(evidence.observation_map().items()):
        rows.append([name, observation.value])
    return rows


# ---------------------------------------------------------------------------
# The runner
# ---------------------------------------------------------------------------


class Runner:
    """Owns per-package orchestration so the CLI stays thin and testable."""

    def __init__(
        self,
        client: CachingClient,
        *,
        now: datetime | None = None,
        alternatives: AlternativeMap | None = None,
        include_dev: bool = True,
        forge: bool = True,
    ):
        self.client = client
        self.clock = now
        self.alternatives = alternatives or load_map()
        self.include_dev = include_dev
        self.forge = forge

    # -- entry point -------------------------------------------------------

    def run(self, inventory: Inventory, *, as_of: datetime | None = None) -> AuditResult:
        graph = analyse(inventory)
        nodes = self._select_nodes(inventory)
        if self.forge and self.client.mode in {"online", "record"}:
            # Learn GitHub's per-bucket budgets before spending any, so a big
            # audit degrades in a controlled way instead of discovering the
            # search limit 30 packages in.
            self.client.learn_rate_limits()
        evidence_by_key: dict[str, PackageEvidence] = {}
        errors: dict[str, str] = {}

        for node in nodes:
            evidence = self._gather(node)
            if self.forge and evidence.repository:
                facts = fetch_repo_facts(
                    self.client,
                    evidence.repository,
                    now=self.clock or utcnow(),
                )
                attach_repo_facts(evidence, facts)
            elif self.forge and not evidence.repository:
                # Two different facts, and conflating them is a lie a reader
                # can check in one click.
                if evidence.homepage:
                    evidence.add_gap(
                        f"forge: repository is not on GitHub ({evidence.homepage}), "
                        f"so commit and issue history cannot be read"
                    )
                else:
                    evidence.add_gap("forge: no repository URL in registry metadata")
            evidence_by_key[node.key] = evidence

        effective_now = as_of or self._clock_from(evidence_by_key) or self._cache_clock() or utcnow()
        reports: list[PackageReport] = []
        for node in nodes:
            evidence = evidence_by_key[node.key]
            verdict = evaluate(evidence, now=effective_now)
            fact = graph.facts.get(node.key)
            report = PackageReport(
                node=node,
                evidence=evidence,
                verdict=verdict,
                depth=fact.depth if fact else None,
                paths=fact.paths if fact else 1,
                parents=fact.parents if fact else [],
                critical=bool(fact.critical) if fact else False,
                bus=bus_factor(evidence, now=effective_now),
            )
            if report.critical:
                report.orphan = simulate(evidence)
            if report.needs_attention and report.critical:
                report.alternatives = self._alternatives(evidence)
            reports.append(report)

        reports.sort(key=lambda r: (SEVERITY[r.verdict_name], r.name))
        warnings = list(graph.warnings)
        skipped = len(inventory.nodes) - len(nodes)
        if skipped:
            warnings.append(
                f"{skipped} dev-only package(s) not audited (pass --include-dev to include them)"
            )
        if not self.forge:
            warnings.append("forge facts disabled (--no-forge): bus factor is unknown")

        return AuditResult(
            ecosystem=inventory.ecosystem,
            lockfile=inventory.lockfile,
            as_of=effective_now,
            packages=reports,
            graph=graph,
            inventory=inventory,
            map_version=self.alternatives.version,
            warnings=warnings,
            client_summary=self.client.summary(),
            generated_at=utcnow(),
            project_name=inventory.project_name,
        )

    # -- internals ---------------------------------------------------------

    def _select_nodes(self, inventory: Inventory) -> list[Node]:
        nodes = [
            node
            for node in inventory.nodes.values()
            if self.include_dev or not node.dev
        ]
        # Deterministic order: ecosystem name is stable, key breaks ties.
        nodes.sort(key=lambda n: (n.name, n.version or "", n.key))
        return nodes

    def _gather(self, node: Node) -> PackageEvidence:
        adapter = get_adapter(node.ecosystem)
        try:
            return adapter.gather(self.client, node.name, node.version)
        except (SourceUnavailable, EvidenceUnavailable, NotFound) as exc:
            evidence = adapter.new_evidence(node.name, node.version)
            evidence.add_gap(f"adapter: {exc}")
            return evidence
        except Exception as exc:  # noqa: BLE001 - one bad package must not sink the audit
            evidence = adapter.new_evidence(node.name, node.version)
            evidence.add_gap(f"adapter crashed: {type(exc).__name__}: {exc}")
            return evidence

    def _alternatives(self, evidence: PackageEvidence) -> list[dict[str, Any]]:
        if self.alternatives.entries:
            from .alternatives import annotate

            return annotate(self.alternatives, evidence.ecosystem, evidence.name)
        return []

    def _cache_clock(self) -> datetime | None:
        """Fallback clock: the newest retrieval the cache remembers.

        Replay mode lands here when every package failed (so there is no
        observation timestamp to take the newest of), which keeps the report's
        "as of" date meaningful instead of silently becoming today.
        """
        newest = getattr(self.client.cache, "newest_fetched_at", None)
        return newest() if callable(newest) else None

    def _clock_from(self, evidence_by_key: dict[str, PackageEvidence]) -> datetime | None:
        """The single instant all verdicts are computed against.

        We take the *newest* observation timestamp across all evidence: that is
        the moment the report's world was last observed.  Offline, every
        timestamp comes from the cache, so a re-run reproduces the same clock.
        """
        newest: datetime | None = None
        for evidence in evidence_by_key.values():
            for observation in evidence.observation_map().values():
                when = observation.retrieved_at
                if newest is None or when > newest:
                    newest = when
        return newest


# ---------------------------------------------------------------------------
# The ledger (Requirement 7)
# ---------------------------------------------------------------------------


@dataclass
class LedgerEntry:
    key: str
    name: str
    version: str | None
    verdict: str
    first_seen: str
    last_seen: str
    critical: bool
    rule_ids: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "version": self.version,
            "verdict": self.verdict,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "critical": self.critical,
            "rule_ids": self.rule_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LedgerEntry":
        return cls(
            key=str(data.get("key") or ""),
            name=str(data.get("name") or ""),
            version=data.get("version"),
            verdict=str(data.get("verdict") or UNKNOWN),
            first_seen=str(data.get("first_seen") or ""),
            last_seen=str(data.get("last_seen") or ""),
            critical=bool(data.get("critical")),
            rule_ids=list(data.get("rule_ids") or []),
        )


@dataclass
class Ledger:
    project: str
    entries: dict[str, LedgerEntry] = field(default_factory=dict)
    runs: int = 0
    last_run: str | None = None
    version: int = LEDGER_VERSION

    # -- persistence -------------------------------------------------------

    @classmethod
    def load(cls, path: Path, project: str) -> "Ledger":
        if not path.is_file():
            return cls(project=project)
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"ledger at {path} is not valid JSON: {exc}") from exc
        entries = {
            key: LedgerEntry.from_dict(value)
            for key, value in (document.get("entries") or {}).items()
        }
        return cls(
            project=str(document.get("project") or project),
            entries=entries,
            runs=int(document.get("runs") or 0),
            last_run=document.get("last_run"),
            version=int(document.get("version") or LEDGER_VERSION),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": self.version,
            "project": self.project,
            "runs": self.runs,
            "last_run": self.last_run,
            "deadledger": __version__,
            "rubric_version": RUBRIC_VERSION,
            "entries": {
                key: entry.as_dict() for key, entry in sorted(self.entries.items())
            },
        }
        path.write_text(json.dumps(document, indent=2, sort_keys=False) + "\n")

    # -- mutation ----------------------------------------------------------

    def record(self, reports: Iterable[PackageReport], *, when: datetime) -> None:
        stamp = iso_day(when) or ""
        self.runs += 1
        self.last_run = f"{iso(when)}"
        for report in reports:
            existing = self.entries.get(report.key)
            rule_ids = sorted(set(report.verdict.rule_ids))
            if existing is None:
                self.entries[report.key] = LedgerEntry(
                    key=report.key,
                    name=report.name,
                    version=report.node.version,
                    verdict=report.verdict_name,
                    first_seen=stamp,
                    last_seen=stamp,
                    critical=report.critical,
                    rule_ids=rule_ids,
                )
            else:
                existing.verdict = report.verdict_name
                existing.last_seen = stamp
                existing.critical = report.critical or existing.critical
                existing.rule_ids = rule_ids
                if report.node.version:
                    existing.version = report.node.version

    def forget_missing(self, reports: Iterable[PackageReport]) -> list[str]:
        """Drop entries for packages no longer in the tree; returns their keys."""
        present = {report.key for report in reports}
        stale = [key for key in self.entries if key not in present]
        for key in stale:
            del self.entries[key]
        return sorted(stale)


@dataclass
class LedgerDiff:
    new_deaths: list[PackageReport] = field(default_factory=list)
    recovered: list[PackageReport] = field(default_factory=list)
    worsened: list[PackageReport] = field(default_factory=list)
    newly_single_maintainer: list[PackageReport] = field(default_factory=list)
    forgot: list[str] = field(default_factory=list)
    is_first_run: bool = False
    #: When the ledger was last written, so a CI summary can say
    #: "no new mortality since <date>" instead of just "since the last run".
    previous_run: str | None = None

    @property
    def has_new_risk(self) -> bool:
        """Whether CI should fail.

        Only *critical* regressions count.  Transitive and dev-only deaths are
        reported as ``worsened`` so they show up in the summary, but they do
        not gate the build: the build has nothing actionable to point at.
        """
        return bool(
            self.new_deaths
            or [r for r in self.worsened if r.critical]
        )

    def summary_line(self) -> str:
        if self.is_first_run:
            return "First recorded run: the whole baseline is new."
        parts = []
        if self.new_deaths:
            parts.append(f"{len(self.new_deaths)} new death(s)")
        if self.worsened:
            parts.append(f"{len(self.worsened)} worsening(s)")
        if self.recovered:
            parts.append(f"{len(self.recovered)} recovery(ies)")
        if self.newly_single_maintainer:
            parts.append(f"{len(self.newly_single_maintainer)} new single-maintainer flag(s)")
        return ", ".join(parts) if parts else "no new mortality since the last run"


def diff_against(
    ledger: Ledger, reports: Iterable[PackageReport], *, previous_rubric: str | None = None
) -> LedgerDiff:
    """Compare a fresh run to the ledger.

    Deliberately conservative: a package that becomes *more* dead
    (dormant -> dead) is a new death; one that merely gains a support rule is
    not.  Recovered packages are reported but never fail a build.
    """
    diff = LedgerDiff(is_first_run=not ledger.entries, previous_run=ledger.last_run)
    if diff.is_first_run:
        # A baseline run has nothing to be new *against*.  Everything it finds
        # is reported (the caller prints it as a baseline), but none of it is a
        # regression, so a CI job adopting DeadLedger does not fail on day one
        # for deaths that predate the tool.  That first-run grace period is the
        # difference between a check people keep and a check people delete.
        return diff
    for report in reports:
        previous = ledger.entries.get(report.key)
        if previous is None:
            if report.verdict_name in (DEAD, DORMANT) and report.critical:
                diff.new_deaths.append(report)
            continue
        if report.verdict_name == DEAD and previous.verdict != DEAD:
            # Transitive deaths are recorded and reported but never gated:
            # you cannot migrate a package you do not declare, so failing the
            # build on one produces an unfixable red check.
            if report.critical:
                diff.new_deaths.append(report)
            else:
                diff.worsened.append(report)
        elif (
            report.verdict_name == DORMANT
            and previous.verdict not in (DEAD, DORMANT)
            and report.critical
        ):
            diff.worsened.append(report)
        elif previous.verdict in (DEAD, DORMANT) and report.verdict_name not in (DEAD, DORMANT):
            diff.recovered.append(report)
        single = getattr(report.bus, "single_maintainer", False)
        if single and previous and "R-SINGLE-MAINTAINER" not in previous.rule_ids:
            # Only interesting if we did not already know; rule ids carry it.
            if "R-BUS-ONE" in report.verdict.rule_ids and "R-BUS-ONE" not in previous.rule_ids:
                diff.newly_single_maintainer.append(report)
    return diff


# ---------------------------------------------------------------------------
# Convenience: whole pipeline in one call
# ---------------------------------------------------------------------------


def audit_lockfile(
    lockfile: Path | str,
    client: CachingClient,
    *,
    include_dev: bool = True,
    forge: bool = True,
    alternatives: AlternativeMap | None = None,
    now: datetime | None = None,
) -> AuditResult:
    inventory = parse_lockfile(Path(lockfile))
    runner = Runner(
        client,
        now=now,
        alternatives=alternatives,
        include_dev=include_dev,
        forge=forge,
    )
    return runner.run(inventory, as_of=now)


def default_ledger_path(project: str, ecosystem: str) -> Path:
    home = Path.cwd() / ".deadledger"
    return home / f"ledger-{slugify(ecosystem + '-' + project)}.json"


def sort_reports(reports: Iterable[PackageReport]) -> list[PackageReport]:
    return sorted(reports, key=lambda r: (SEVERITY[r.verdict_name], r.name))
