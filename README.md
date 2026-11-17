# DeadLedger

[![CI](https://github.com/pooria683/deadledger/actions/workflows/ci.yml/badge.svg)](https://github.com/pooria683/deadledger/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![rubric v1.0](https://img.shields.io/badge/rubric-v1.0-informational.svg)](docs/verdicts.md)

**Mortality reports for dependency trees.** For every direct *and* transitive
dependency, DeadLedger collects the evidence of its aliveness — last release,
last commit, maintainer count, bus factor, issue triage — and prints a
plain-language verdict, each backed by a citation you can check yourself.

```
● thriving 13 · ◐ coasting 9 · ○ dormant 2 · ✕ dead 3   (28 total)

Critical dependencies needing a decision
  ✕ dead      django-pglocks
    The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive.
    Bus factor 1 — Xof is the only committer in the last 12 months
    (last commit 2026-06-21). If they stop, this stops.
    → environs: drop-in (100% of measured API covered)
  ○ dormant   netaddr
    The newest stable release is 2.5y old (2024-05-28);
    the project has not published for two years.
```

Built for three questions people actually ask:

* **Where should we spend maintenance budget?** (fork vs migrate vs vendor)
* **What did we inherit?** — "we took over this project, what is already dead in here?"
* **What breaks the day this maintainer quits?**

---

## Demo: 37 dead dependencies in a production app

[`examples/saleor-2.11/REPORT.md`](examples/saleor-2.11/REPORT.md) is a full
report for [Saleor 2.11.1](https://github.com/saleor/saleor/blob/2.11.1/poetry.lock)
— a real, large Django e-commerce platform, audited at the tag as it shipped.
206 packages, 56 of them direct:

| | |
|---|---|
| **37 dead** | 18 % of the tree, including **12 direct** dependencies. |
| **17 dormant** | `openpyxl`, `google-i18n-address`, `django-versatileimagefield` … |
| **15 critical packages need a decision** | `jaeger-client` and `opentracing` are archived upstream; `draftjs-sanitizer`, `html-to-draftjs`, `prices`, `purl`, `text-unidecode` have not shipped in 4+ years; `maxminddb-geolite2` in 8 |
| **15 packages with a bus factor of 1** | e.g. `django-storages`, one committer in twelve months |
| **0 unknown** | every package resolved, so every verdict has evidence behind it |

Read the whole thing: [`REPORT.md`](examples/saleor-2.11/REPORT.md) — 2,500
lines, a citation on every claim.

There is a smaller, fully offline demo too:
[`examples/netbox-3.0/REPORT.md`](examples/netbox-3.0/REPORT.md) (28 packages,
3 dead, 2 single-maintainer), and an npm one in
[`examples/legacy-npm/REPORT.md`](examples/legacy-npm/REPORT.md) where
`left-pad` is caught by the archived-repository rule and `request` by its
deprecation.

None of this is a scandal about those projects. Every package in the Saleor
tree was a reasonable choice in 2020, most of them still work, and several were
replaced years ago by maintainers who moved on. That is exactly the point: a
dependency does not stop working when it dies, so the decay is invisible until
you look for it.

---

## Quick start

```sh
pipx install deadledger
cd your-project
deadledger audit
```

`audit` finds the lockfile in the current directory (or the nearest parent) and
writes a Markdown report to stdout. Supported out of the box:

| ecosystem | lockfiles |
|---|---|
| PyPI | `requirements.txt`, `poetry.lock`, `uv.lock`, `Pdm.lock`, `Pipfile.lock`, `constraints.txt` |
| npm | `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock` (pins only) |
| crates | `Cargo.lock` |

Other commands:

```sh
deadledger explain django-pglocks     # every fact behind one verdict, with URLs
deadledger audit --format text        # the short version for a terminal
deadledger audit --format json        # for a script; --format sarif for code scanning
deadledger --offline audit            # never open a socket; use the cache
deadledger ci --sarif out.sarif       # fail only on NEW deaths since last run
deadledger doctor                     # is this machine able to audit?
```

### Environment

| variable | effect |
|---|---|
| `GITHUB_TOKEN` (or `GH_TOKEN`) | enables bus factor, triage rate and the import-search proxy. Without it those become explicit gaps, never guesses. |
| `DEADLEDGER_HOME` | where the cache and ledgers live (default `.deadledger/`) |

Nothing about your tree is uploaded. Every request is a read for public
package metadata; the cache is SQLite on your disk.

---

## The verdict rubric

Four verdicts, exact thresholds, versioned. Full reasoning and the rule-by-rule
precedence order: [`docs/verdicts.md`](docs/verdicts.md).

| verdict | when | what it means for you |
|---|---|---|
| 🟢 **thriving** | ≥ 2 stable releases in the last year **and** (≥ 12 commits in the last year **or** a commit within 90 days) | keep it, recheck yearly |
| 🟡 **coasting** | alive, but nothing above fired; no death signal | pin it. It works; nobody is watching. |
| 🟠 **dormant** | no stable release for **730 days** | decide now: pin, fork from main, or schedule a migration |
| 🔴 **dead** | repository **archived**, package **deprecated/yanked**, missing from the registry, or no release for **1460 days** | migrate or vendor — this is an ADR |
| ⚪ **unknown** | not enough evidence | look yourself, or re-run with network access |

Four deliberate design decisions, because they are where this class of tool
usually loses its credibility:

**Unknown is not dead.** A failed source becomes a gap, never a zero. A package
nobody could look up is `unknown`, and `unknown` never fails a CI build.

**Bus factor is a risk, not a verdict.** Exactly one committer in the last year
is flagged, in its own section, with that person's last commit date — it does
not move the package into a worse verdict on its own. Many excellent packages
have one maintainer; a report that calls them all dying is a report nobody
reads.

**Slow releases are not death.** Commits-without-releases is a *different*
remedy — "pin a git ref or ask for a release" — not a death sentence. PyYAML
ships roughly once a year and is doing fine; the rubric says so.

**Dead means dead.** An archived repository or an explicit deprecation is a
statement by the maintainers and cannot be outweighed by historical download
volume.

### Arguing with a verdict

The rubric is a versioned community artifact. Every report quotes the rubric
version that produced it, and every change is recorded in
[`docs/rubric-changelog.md`](docs/rubric-changelog.md) — including the two
false positives that shaped v1.0 (`threadloop` libelled as dead, and PyYAML
libelled as dormant). If a threshold is wrong, that is a pull request with a
named package it gets wrong, not a footnote.

---

## The three analyses

### 1. Registry triage

Release history over the package's whole life, owner identity, deprecation
state, open-issue ratio and maintainer counts — cached in SQLite with TTLs
(6 h for registries, 12 h for forges, 24 h for download counts). `--offline`
replays the cache and keeps the original retrieval dates, so citations stay
honest.

### 2. Bus factor

Distinct non-bot committers in the last 12 months, from the commit history
itself. Bot accounts are excluded and the exclusion is stated in the report. A
partial page of history makes the metric *unknown* rather than wrong: a wrong
bus factor is worse than a missing one.

### 3. The orphan simulation

For each critical (direct, non-dev) dependency, one line answering *"if this
dies, who else uses it?"* — with the basis named:

| source | label | example |
|---|---|---|
| crates.io reverse dependencies | `exact` | "1,200 crates depend on tempdir (exact count from crates.io)." |
| download counts (pypistats, npm) | `approximate` | "About 250.0k downloads (widely used); a usage proxy, not a dependent count." |
| GitHub code search | `approximate` | "About 1.3k files contain it; an approximate reach signal only." |

### 4. Migration hints

For dead or dormant criticals, the report lists known alternatives from
[`maps/alternatives.json`](maps/alternatives.json) — 61 community-curated
entries across PyPI, npm and crates — each with a cost label derived from a
measured API-surface overlap (`near drop-in` → `rewrite-shaped`). Every
`api_diff` states its basis; unmeasured entries say so instead of guessing.

---

## CI mode: the ledger remembers

This is the part that makes DeadLedger usable on a schedule. A tree with 200
transitive dependencies will contain dead ones today; failing on all of them
means the check gets muted within a week.

`deadledger ci` records what it finds in a ledger and **fails only on new
critical deaths**:

* the first run is a baseline and never fails;
* a death seen before stays quiet — the ledger remembers, so humans don't have
  to re-grieve old losses every build;
* transitive and dev-only deaths are reported but do not gate the build;
* `unknown` never fails anything.

```yaml
- run: deadledger ci --sarif deadledger.sarif --report mortality.md
  env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
- uses: github/codeql-action/upload-sarif@v3
  with: { sarif_file: deadledger.sarif }
```

Full rationale, exit codes and a complete Actions workflow:
[`docs/ci-mode.md`](docs/ci-mode.md).

---

## Design notes

**Local-first.** Registry responses are cached in SQLite with per-source TTLs.
A cache miss while offline is a reported gap, not a crash and not a zero. Your
dependency tree never leaves the machine.

**Evidence is a data structure.** Every number arrives as an `Observation`
carrying its source URL and retrieval timestamp
([`deadledger/evidence.py`](deadledger/evidence.py)). That is why "no score
without its source" is enforceable rather than aspirational: the verdict
function only accepts observations, and a test fails if any claim ships without
a resolvable `[src N]` marker.

**Determinism.** The verdict clock is the newest retrieval in the evidence, not
the wall clock. Re-running an audit from cache produces the same verdicts and
the same citations, byte for byte — there are tests for exactly that
([`tests/test_determinism.py`](tests/test_determinism.py)).

**Adapters are the extension point.** One module per ecosystem, each a
collector that cannot make verdicts.
[`docs/adapters.md`](docs/adapters.md) is the guide.

## Development

```sh
git clone https://github.com/pooria683/deadledger && cd deadledger
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/pytest          # 204 tests, no network required
```

Adapter tests replay recorded registry responses from `tests/fixtures/`. Refresh
them with `deadledger record --profile netbox-3.0 --lockfile examples/netbox-3.0/requirements.txt`
(see [`tests/fixtures/README.md`](tests/fixtures/README.md)).

Contributions are welcome, especially two kinds:
[disagreements with the rubric](docs/verdicts.md) backed by a real package, and
[new entries in the alternatives map](docs/alternatives-map.md).
See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT. The rubric and the alternatives map are the community assets; fork them,
argue with them, and send back what you learn.
