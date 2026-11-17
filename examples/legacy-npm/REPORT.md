# Mortality report: legacy-storefront

**Verdict as of 2026-11-16** · ecosystem `npm` · 10 packages · rubric v1.0 · alternatives map v1.0.0 · DeadLedger 0.1.0

Audited `examples/legacy-npm/package-lock.json`. The report describes the tree as observed on **2026-11-16**; every claim below is followed by a source marker resolved at the bottom.

## Summary

- **10 packages** audited (4 critical: direct, non-dev; 6 transitive or dev).
- **4 dead**, **1 dormant**, 3 coasting, 2 thriving, 0 unknown.
- **2 critical package(s) need a decision**: `left-pad` (dead), `request` (dead).
- Ledger: no new mortality since the last run.

### The headline

- `accepts` **dormant** (transitive, depth 1) — The newest stable release is 2.2y old (2024-08-31); the project has not published for two years. [src 1]
- `bytes` **dead** (transitive, depth 2) — The newest stable release is 4.8y old (2022-01-28); nothing has shipped in 4+ years. [src 2]
- `left-pad` **dead** (critical) — The repository left-pad/left-pad is archived, so no further commits or releases can land without a deliberate revival. [src 3] [src 4]
- `request` **dead** (critical) — The package is deprecated: request has been deprecated, see https://github.com/request/request/issues/3142. [src 5]
- `uuid` **dead** (transitive, depth 1) — The package is deprecated: uuid@10 and below is no longer supported.  For ESM codebases, update to uuid@latest.  For CommonJS codebases, use uuid@11 (but be aware this version will likely be deprecated in 2028).. [src 6] [src 7] [src 8]

## What is dead or dying

### left-pad 1.3.0 — 🔴 dead

*npm · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

String left pad

**Evidence**

- The repository left-pad/left-pad is archived, so no further commits or releases can land without a deliberate revival. [src 3]
  - `archived`=True
- The package is deprecated: use String.prototype.padStart(). [src 4]
  - `deprecated`=True
- The newest stable release is 8.6y old (2018-04-09); nothing has shipped in 4+ years. [src 4]
  - `last_release_age_days`=3143
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: npm download API did not answer
- usage: no download or dependent counts available
- commits: commit history could not be read
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### request 2.88.2 — 🔴 dead

*npm · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

Simplified HTTP request client.

**Evidence**

- The package is deprecated: request has been deprecated, see https://github.com/request/request/issues/3142. [src 5]
  - `deprecated`=True
- The newest stable release is 6.8y old (2020-02-11); nothing has shipped in 4+ years. [src 5]
  - `last_release_age_days`=2470
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: npm download API did not answer
- usage: no download or dependent counts available
- commits: commit history could not be read
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### bytes 3.1.0 — 🔴 dead

*npm · transitive, depth 2 · verdict confidence: medium · rubric v1.0*

Utility to parse a string bytes to bytes and vice-versa

**Evidence**

- The newest stable release is 4.8y old (2022-01-28); nothing has shipped in 4+ years. [src 2]
  - `last_release_age_days`=1753

**Gaps**

- usage: npm download API did not answer
- usage: no download or dependent counts available
- commits: commit history could not be read
- triage: issue search did not answer

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### uuid 3.4.0 — 🔴 dead

*npm · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

RFC9562 UUIDs

**Evidence**

- The package is deprecated: uuid@10 and below is no longer supported.  For ESM codebases, update to uuid@latest.  For CommonJS codebases, use uuid@11 (but be aware this version will likely be deprecated in 2028).. [src 6]
  - `deprecated`=True
- Actively maintained: 8 release(s) in 12 months, last commit 15d ago. [src 6] [src 7] [src 8]
  - `releases_12mo`=8, `last_commit_age_days`=15

**Gaps**

- usage: npm download API did not answer
- usage: no download or dependent counts available
- commits: commit history could not be read
- triage: issue search did not answer

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### accepts 1.3.7 — 🟠 dormant

*npm · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Higher-level content negotiation

**Evidence**

- The newest stable release is 2.2y old (2024-08-31); the project has not published for two years. [src 1]
  - `last_release_age_days`=807

**Gaps**

- usage: npm download API did not answer
- usage: no download or dependent counts available
- commits: commit history could not be read
- triage: issue search did not answer

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

## Bus factor: who is one person away from a fork

A package appears here when exactly one account committed to its public repository in the 12 months before retrieval. That is a fact about the repository, not a prediction.

No package in this tree had exactly one committer in the last year.

## Orphan simulation: if this dies, who else uses it?

One line per critical (direct, non-dev) dependency. `exact` means the registry publishes a dependent count; `approximate` means the number is downloads or import sites, which measure use, not dependents.

| package | if it dies | basis |
|---|---|---|
| `express` | no source published a usage or dependent count.  | unknown: usage: npm download API did not answer; usage: no download or dependent counts available |
| `left-pad` | no source published a usage or dependent count.  | unknown: usage: npm download API did not answer; usage: no download or dependent counts available |
| `moment` | no source published a usage or dependent count.  | unknown: usage: npm download API did not answer; usage: no download or dependent counts available |
| `request` | no source published a usage or dependent count.  | unknown: usage: npm download API did not answer; usage: no download or dependent counts available |

## Migration hints for dead and dormant criticals

From the community alternatives map v1.0.0 (`maps/alternatives.json`). The cost label is a migration *proxy*: `near drop-in` means the measured public API mostly overlaps, `rewrite-shaped` means it does not. Entries with no measurement say so.

### left-pad

- **String.prototype.padStart** — The package's own deprecation message points at the language feature. *Cost: near drop-in (100% of measured API covered).*
  - Basis: measured: padStart(targetLength, padString) covers left-pad(str, len, ch)
  - <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/padStart>

### request

- **undici** — Node's own HTTP client, maintained by the Node project; fetch-compatible. *Cost: significant (50% of measured API covered).*
  - Basis: estimated: request's callback style maps to fetch/undici but the options objects share almost no names
  - <https://github.com/nodejs/undici>
- **axios** — Maintained client with interceptors, the closest conceptual successor. *Cost: moderate (70% of measured API covered).*
  - Basis: estimated: axios(config) and request(config) share method/url/headers/data, differ on streams and callbacks
  - <https://github.com/axios/axios>

## Every package

`depth 0` is declared by this project. `critical` means direct and not dev. Verdicts without enough evidence say `unknown`.

| package | version | verdict | critical | depth | last release | last commit | maintainers | bus factor |
|---|---|---|---|---|---|---|---|---|
| `body-parser` | 1.19.0 | 🟢 thriving | no | 1 | 2026-10-22 | 2026-11-15 | 4 | ? |
| `express` | 4.17.1 | 🟢 thriving | yes | 0 | 2026-10-09 | 2026-11-02 | 5 | ? |
| `mime-types` | 2.1.35 | 🟡 coasting | no | 2 | 2025-11-20 | 2026-06-02 | 5 | ? |
| `moment` | 2.29.1 | 🟡 coasting | yes | 0 | 2026-09-15 | 2026-10-08 | 6 | ? |
| `negotiator` | 0.6.2 | 🟡 coasting | no | 2 | 2026-08-20 | 2026-08-20 | 5 | ? |
| `accepts` | 1.3.7 | 🟠 dormant | no | 1 | 2024-08-31 | 2026-04-02 | 4 | ? |
| `bytes` | 3.1.0 | 🔴 dead | no | 2 | 2022-01-28 | 2024-07-05 | 2 | ? |
| `left-pad` | 1.3.0 | 🔴 dead | yes | 0 | 2018-04-09 | 2019-04-19 | 2 | ? |
| `request` | 2.88.2 | 🔴 dead | yes | 0 | 2020-02-11 | 2024-08-14 | 4 | ? |
| `uuid` | 3.4.0 | 🔴 dead | no | 1 | 2026-10-10 | 2026-11-01 | 2 | ? |

## What this report does not know

- `body-parser`: usage: npm download API did not answer
- `body-parser`: usage: no download or dependent counts available
- `body-parser`: commits: commit history could not be read
- `body-parser`: triage: issue search did not answer
- `express`: usage: npm download API did not answer
- `express`: usage: no download or dependent counts available
- `express`: commits: commit history could not be read
- `express`: triage: issue search did not answer
- `mime-types`: usage: npm download API did not answer
- `mime-types`: usage: no download or dependent counts available
- `mime-types`: commits: commit history could not be read
- `mime-types`: triage: issue search did not answer
- `moment`: usage: npm download API did not answer
- `moment`: usage: no download or dependent counts available
- `moment`: commits: commit history could not be read
- `moment`: triage: issue search did not answer
- `negotiator`: usage: npm download API did not answer
- `negotiator`: usage: no download or dependent counts available
- `negotiator`: commits: commit history could not be read
- `negotiator`: triage: issue search did not answer
- `accepts`: usage: npm download API did not answer
- `accepts`: usage: no download or dependent counts available
- `accepts`: commits: commit history could not be read
- `accepts`: triage: issue search did not answer
- `bytes`: usage: npm download API did not answer
- `bytes`: usage: no download or dependent counts available
- `bytes`: commits: commit history could not be read
- `bytes`: triage: issue search did not answer
- `left-pad`: usage: npm download API did not answer
- `left-pad`: usage: no download or dependent counts available
- `left-pad`: commits: commit history could not be read
- `left-pad`: triage: issue search did not answer
- `request`: usage: npm download API did not answer
- `request`: usage: no download or dependent counts available
- `request`: commits: commit history could not be read
- `request`: triage: issue search did not answer
- `uuid`: usage: npm download API did not answer
- `uuid`: usage: no download or dependent counts available
- `uuid`: commits: commit history could not be read
- `uuid`: triage: issue search did not answer
- 1 dev-only package(s) not audited (pass --include-dev to include them)

Verdicts follow rubric v1.0 (`docs/verdicts.md`). Dormant means no stable release for 730 days; dead means an archived repository, an explicit deprecation, or no release for 1460 days. If you think a threshold is wrong, that is a PR to the rubric, not a footnote.

## Sources

| # | Source | Retrieved |
|---|---|---|
| 1 | <https://registry.npmjs.org/accepts> | 2026-11-16T18:12:21Z |
| 2 | <https://registry.npmjs.org/bytes> | 2026-11-16T18:12:21Z |
| 3 | <https://github.com/left-pad/left-pad> | 2026-11-16T18:12:21Z |
| 4 | <https://registry.npmjs.org/left-pad> | 2026-11-16T18:12:21Z |
| 5 | <https://registry.npmjs.org/request> | 2026-11-16T18:12:21Z |
| 6 | <https://registry.npmjs.org/uuid> | 2026-11-16T18:12:21Z |
| 7 | <https://github.com/uuidjs/uuid> | 2026-11-16T18:12:21Z |
| 8 | <https://api.github.com/repos/uuidjs/uuid/commits> | 2026-11-16T18:12:21Z |

_Retrieved-at dates are when DeadLedger first stored each response. Re-running offline reuses those dates rather than pretending the world was re-observed._
