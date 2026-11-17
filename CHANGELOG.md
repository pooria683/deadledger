# Changelog

DeadLedger follows [semantic versioning](https://semver.org/). Two version
numbers matter to users:

* the **tool version** (this file) — CLI surface, report format, adapters;
* the **rubric version** ([`docs/rubric-changelog.md`](docs/rubric-changelog.md))
  — the thresholds that decide verdicts.

Every report prints both, so a report is always self-describing.

---

## 0.1.0 — 2026-11-16

First release.

### Added

**Audit**
- `deadledger audit` reads `requirements.txt`, `poetry.lock`, `uv.lock`,
  `Pipfile.lock`, `package-lock.json`, `yarn.lock` and `Cargo.lock`, walking up
  from the current directory to find them.
- Direct/transitive classification from the lockfile's own edges, with depth
  and parent chains. Where a lockfile has no edges (Pipfile.lock, yarn.lock),
  the report says so instead of inventing a tree.
- Verdicts (`thriving` / `coasting` / `dormant` / `dead` / `unknown`) from rubric
  v1.0, every claim carrying a `[src N]` marker resolved to a URL and a
  retrieval timestamp.

**Evidence**
- PyPI, npm and crates.io adapters: release cadence over the package's whole
  life, owner/maintainer identity, deprecation state, download counts.
- GitHub forge facts: last commit, distinct non-bot committers in 12 months,
  the lead committer's last activity and SHA, and an issue triage rate.
- Bus factor is reported as its own section and never decides a verdict.

**The orphan simulation**
- One line per critical dependency answering "if this dies, who else uses it?",
  labelled `exact` (crates.io reverse dependencies), `approximate` (downloads,
  code-search counts) or `unknown`.

**Migration hints**
- `maps/alternatives.json` ships 61 curated entries across the three
  ecosystems, with API-overlap cost labels and a stated basis for every number.
- Local layering: `--map`, then `~/.config/deadledger/alternatives.json`, then
  the shipped map.

**Local-first**
- SQLite cache with per-source TTLs; `--offline` replays it and keeps the
  original retrieval dates.
- `deadledger cache info|prune|clear`.

**CI**
- `deadledger ci` fails only on *new* critical mortality, using a committed
  ledger. First run baselines and never fails; transitive deaths are reported
  but do not gate; `unknown` never fails.
- SARIF 2.1.0 output for GitHub code scanning.

**Tooling**
- `deadledger record` re-records adapter fixtures in two passes (live, then
  playback), so committed fixtures contain only what an audit actually uses.
- `deadledger doctor`, `deadledger sources`, `deadledger map lint|show`,
  `deadledger explain`.

### Notes on version 1.0 of the rubric

Two false positives found while auditing real trees shaped the rubric before
release, and both are recorded in the rubric changelog: a repository with
commits from last week was called dead because its last release was old, and
PyYAML was called dormant because it ships roughly once a year. Neither is
acceptable in a tool meant to be trusted in an ADR.

### Known limitations

- Forge data comes from GitHub only. Packages hosted elsewhere report the
  absence of forge evidence as a gap.
- Python has no native dependent count; its orphan simulation is always a proxy.
- crates.io reverse dependencies are implemented and unit-tested against the
  documented schema, but the recording environment could not reach crates.io,
  so that path has not yet been exercised against the live service.
- `pnpm-lock.yaml` is detected but not parsed (YAML without a dependency).
