# The verdict rubric

**Version 1.0** · effective 2026-11-16 · changelog in
[`rubric-changelog.md`](rubric-changelog.md)

This document is the contract between DeadLedger and its users. Every verdict
in every report is produced by the rules below, and every rule names the
evidence it needs. If you disagree with a verdict, you are disagreeing with a
specific rule at a specific threshold — and that is a pull request, not a
footnote.

The machine-readable copy of these thresholds is `THRESHOLDS` in
[`deadledger/mortality.py`](../deadledger/mortality.py). The two are kept in
sync by tests: `tests/test_docs.py` fails if this table and the code disagree.

---

## The four verdicts

| verdict | meaning | the decision it implies |
|---|---|---|
| **thriving** | Alive, and there is current evidence of maintenance. | Keep it. Re-check in a year. |
| **coasting** | Alive but quiet. Nothing says it is dying; nothing says somebody is watching either. | Keep it, but pin it. It will not be fixed for you. |
| **dormant** | A real death signal (no release for two years, or development that stopped publishing), with no sign of a comeback. | Decide now: fork from main, pin, or schedule a migration. |
| **dead** | An explicit death signal: the repository is archived, the package is deprecated or withdrawn, or nothing has shipped in four years. | Migrate or vendor. This is an ADR, not a ticket. |
| **unknown** | Not enough evidence to say anything. | Look yourself, or re-run with network access. |

### The rule that matters most: unknown is not dead

A package with no releases and an unreadable repository is **unknown**, not
dead. It may be a mirror of a private registry, a renamed project, a rate
limit, or a typo. Absence of evidence is not evidence of mortality, and a tool
that confuses the two is worse than no tool: it trains people to ignore it.

Practically, this means:

* a source that fails is recorded as a **gap** and never contributes a zero;
* a package with no decisive evidence is never counted against you in CI;
* `unknown` is reported as its own bucket, with its own count, in every report.

---

## The thresholds

<!-- thresholds-table:begin -->
| signal | thriving | coasting | dormant | dead | where it comes from |
|---|---|---|---|---|---|
| Age of newest stable release | any age | < 730 days | ≥ 730 days | ≥ 1460 days | registry release list |
| Repository archived | — | — | — | yes (always dead) | forge API |
| Package deprecated / yanked / withdrawn | — | — | — | yes (always dead) | registry metadata |
| Package missing from registry (404) | — | — | — | yes (always dead) | registry |
| Stable releases in the last 365 days | ≥ 2 | < 2 | — | — | registry release list |
| Commits in the last 365 days | ≥ 12 | < 12 | — | — | forge commit history |
| Last commit | ≤ 90 days ago | older | — | — | forge repository |
| Commits in the last year **but** zero releases | — | yes (supporting) | only softens dead → dormant | — | both of the above |
| Distinct committers in the last 365 days | ≥ 2 (flagged "fragile" at 1) | — | — | — | forge commit history |
| Concentrated committer share | — | supporting only | — | — | forge commit history |
| Issue triage rate (closed ÷ created, last 365 days) | — | ≤ 0.35 (supporting only) | — | — | forge issue search |
| Known advisories | — | supporting only | — | — | registry / forge |
| No evidence at all | — | — | — | — | becomes `unknown` |

<!-- thresholds-table:end -->

### How a verdict is decided

Rules are evaluated in this order of precedence, and the first match wins:

1. **Explicit death signals.** An archived repository, a deprecation, or a
   404 from the registry. These are statements by the maintainers or the
   registry and cannot be outweighed by historical download volume. *Exception:*
   a package whose releases stopped but whose repository is still moving is
   **dormant**, not dead (see below).
2. **No release for four years** → dead.
3. **No release for two years** → dormant.
4. **Development without publishing.** No releases in the last year, non-bot
   commits in the last year, and a last commit materially newer than the last
   release → the verdict does **not** change, but the report says
   "development continues without publishing" and the remedy becomes *pin a
   git ref or ask for a release* instead of *migrate*. This rule is
   **supporting, not deciding**: it can soften a four-year-old release from
   `dead` to `dormant` (a consumer can still get fixes from `main`), but it can
   never on its own call a live project dormant. That distinction is
   deliberate; see `R-DEVELOP-WITHOUT-RELEASE` in the rubric changelog.
5. **Thriving.** Two or more stable releases in the last year *and* (at least
   12 commits in the last year *or* a commit within 90 days).
6. **Otherwise: coasting.** This is the honest default for "alive, shipping
   occasionally, nobody is watching". It is always accompanied by a cited
   sentence stating what did and did not happen.

Numbers that only *support* a verdict can add a sentence and lower confidence,
but they cannot change the verdict on their own. `DECIDING_RULES` in the code
is the complete list of rules permitted to decide, and it is short on purpose.

| rule id | effect |
|---|---|
| `R-DEVELOP-WITHOUT-RELEASE` | "alive, not publishing": changes the remedy, and softens `dead` → `dormant` |
| `R-BUS-ONE` | one committer in 12 months; names them and their last commit. Never decides. |
| `R-BUS-ONE-REGISTRY` | the registry publishes exactly one owner/contributor. Never decides. |
| `R-BUS-CONCENTRATED` | one person authored most of the last year's commits. Never decides. |
| `R-TRIAGE-LOW` | triage rate at or below 0.35. Never decides. |
| `R-ADVISORIES` | known security advisories were reported. Never decides. |
| `R-QUIET-DEFAULT` | nothing decisive fired; states what was checked, so a `coasting` verdict is never reasonless. |
| `R-NO-EVIDENCE` | nothing could be retrieved → `unknown`. |

### Bus factor is a risk, not a verdict

A package with exactly one committer in the last year is **flagged**, in its
own section, with that person's last commit date and SHA. It is not moved into
a worse verdict by that fact alone.

The reason is empirical: a large share of excellent, stable packages have a
single maintainer. A rubric that calls them all dying produces a report nobody
reads, and the real deaths get lost in the noise. "Bus factor 1" tells you
where a fork would be cheap; it does not tell you the package is broken.

---

## Confidence

Every verdict carries a confidence level, and it only ever describes how much
evidence we had:

| confidence | when |
|---|---|
| **high** | Every rule that fired had all of its inputs. |
| **medium** | The verdict is supported, but a forge signal (commits, triage) was missing. |
| **low** | The verdict is a default (nothing decisive fired), or the package is `unknown`. |

Confidence is not a probability. It says "we saw what we needed to see", not
"we are 80 % sure".

---

## What each number actually measures

A mortality report is only as honest as its sources, so each figure states its
limitations in the report itself:

| figure | source | what it does **not** mean |
|---|---|---|
| Last release date | registry | That the code is unchanged — commits may continue. |
| Commits in the last year | forge | That features shipped. Bot commits are excluded and the exclusion is stated. |
| Distinct committers | forge | That those people are maintainers. It counts commit authorship. |
| Triage rate | forge issue search | That the project ignores users. Issues closed without action are still "closed". |
| Downloads | pypistats / npm | That N projects depend on it. Downloads measure use, not dependence. |
| Dependent count | crates.io only | Comparable across ecosystems. Only crates.io publishes this. |
| Import sites | GitHub code search | That the code is *used*. Matching `import x` is a text search. |

When a number is a proxy, the report says `approximate` and names the proxy. A
proxy is never presented as a census.

---

## The asymmetry that makes this safe to run in CI

`deadledger ci` fails a build on **new** critical deaths only:

* the first run is a baseline and never fails;
* a death seen in a previous run is remembered in the ledger and stays quiet;
* a transitive or dev-only death is reported but does not fail the build,
  because you cannot migrate a package you do not declare;
* a recovery is reported as good news and cannot fail anything;
* `unknown` never fails a build. Being unable to look is not a regression.

The full reasoning is in
[`ci-mode.md`](ci-mode.md).

---

## Changing the rubric

The rubric is versioned, and the version appears in every report. To change it:

1. Open a PR that changes `THRESHOLDS` (or a rule) **and** this table.
2. Add an entry to [`rubric-changelog.md`](rubric-changelog.md) saying what
   moved, why, and which real package it changes the verdict for. "It felt too
   strict" is not a reason; "it called `requests` dormant" is.
3. Bump `RUBRIC_VERSION` in [`deadledger/__init__.py`](../deadledger/__init__.py).
4. Update the golden tests in `tests/test_rubric_boundaries.py`, which are
   written to fail at exactly the boundaries you moved.

Reports quote the rubric version they were produced under, so a report from
last year stays internally consistent even after the rubric moves on. If you
want to know why a verdict changed between two runs, compare the rubric
versions first: the changelog is the answer.
