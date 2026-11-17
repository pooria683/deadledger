# Mortality report: netbox-3.0

**Verdict as of 2026-11-16** · ecosystem `pypi` · 28 packages · rubric v1.0 · alternatives map v1.0.0 · DeadLedger 0.1.0

Audited `examples/netbox-3.0/requirements.txt`. The report describes the tree as observed on **2026-11-16**; every claim below is followed by a source marker resolved at the bottom.

## Summary

- **28 packages** audited (27 critical: direct, non-dev; 1 transitive or dev).
- **3 dead**, **2 dormant**, 9 coasting, 13 thriving, 1 unknown.
- **5 critical package(s) need a decision**: `markdown-include` (dormant), `netaddr` (dormant), `django-graphiql-debug-toolbar` (dead), `django-pglocks` (dead), `svgwrite` (dead).
- **2 package(s) have a bus factor of 1** in the last 12 months of commits.
- Ledger: no new mortality since the last run.

### The headline

- `django-graphiql-debug-toolbar` **dead** (critical) — The newest stable release is 5.2y old (2021-08-28); nothing has shipped in 4+ years. [src 1]
- `django-pglocks` **dead** (critical) — The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 2] [src 3] [src 4]
- `svgwrite` **dead** (critical) — The repository mozman/svgwrite is archived, so no further commits or releases can land without a deliberate revival. [src 5] [src 6]
- `markdown-include` **dormant** (critical) — The newest stable release is 3.8y old (2023-02-07); the project has not published for two years. [src 7]
- `netaddr` **dormant** (critical) — The newest stable release is 2.5y old (2024-05-28); the project has not published for two years. [src 8]

## What is dead or dying

### django-graphiql-debug-toolbar 0.2.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

Django Debug Toolbar for GraphiQL IDE.

**Evidence**

- The newest stable release is 5.2y old (2021-08-28); nothing has shipped in 4+ years. [src 1]
  - `last_release_age_days`=1905
- The registry lists a single owner (mongkok); the forge was not readable. [src 1]
  - `maintainers`=1
- Orphan check (approximate): About 0 files contain it (github code search); an approximate reach signal only. _(basis: files containing '"import django_graphiql_debug_toolbar" in:file')_ [src 9]

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### django-pglocks 1.0.4 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

DEPRECATED — consolidated into django-pgware. Context managers for PostgreSQL advisory locks in Django.

**Evidence**

- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 2]
  - `deprecated`=True
- Exactly one person has committed in the last year (Xof, last commit 2026-06-21 — 4.9mo ago). [src 3] [src 4]
  - `committers_12mo`=1, `lead_committer_last_activity`=2026-06-21, `lead_committer_last_activity_days`=148
- Orphan check (approximate): About 2 files contain it (github code search); an approximate reach signal only. _(basis: files containing '"import django_pglocks" in:file')_ [src 10]

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.
- Bus factor 1 — Xof is the only committer in the last 12 months (last commit 2026-06-21). If they stop, this stops. Vendoring is cheaper than waiting for a crisis if this package is critical.

### svgwrite 1.4.1 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

A Python library to create SVG drawings.

**Evidence**

- The repository mozman/svgwrite is archived, so no further commits or releases can land without a deliberate revival. [src 5]
  - `archived`=True
- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 6]
  - `deprecated`=True
- The newest stable release is 4.3y old (2022-07-14); nothing has shipped in 4+ years. [src 6]
  - `last_release_age_days`=1586
- The registry lists a single owner (mozman); the forge was not readable. [src 6]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### markdown-include 0.6.0 — 🟠 dormant

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

A Python-Markdown extension which provides an 'include' function

**Evidence**

- The newest stable release is 3.8y old (2023-02-07); the project has not published for two years. [src 7]
  - `last_release_age_days`=1378
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://pypi.org/project/markdown-include/), so commit and issue history cannot be read

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### netaddr 0.8.0 — 🟠 dormant

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

A network address manipulation library for Python

**Evidence**

- The newest stable release is 2.5y old (2024-05-28); the project has not published for two years. [src 8]
  - `last_release_age_days`=901
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

## Bus factor: who is one person away from a fork

A package appears here when exactly one account committed to its public repository in the 12 months before retrieval. That is a fact about the repository, not a prediction.

| package | critical | last commit by that person | commits |
|---|---|---|---|
| `django-pglocks` [src 3] [src 4] | yes | Xof, 2026-06-21 | 11 |
| `graphene-django` [src 11] [src 12] | yes | superlevure, 2026-06-24 | 1 |

## Orphan simulation: if this dies, who else uses it?

One line per critical (direct, non-dev) dependency. `exact` means the registry publishes a dependent count; `approximate` means the number is downloads or import sites, which measure use, not dependents.

| package | if it dies | basis |
|---|---|---|
| `django-redis` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-rq` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-tables2` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-taggit` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-timezone-field` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `djangorestframework` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `drf-yasg` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `graphene-django` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `gunicorn` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `jinja2` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `markdown` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `markdown-include` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `netaddr` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `pillow` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `psycopg2-binary` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `pycryptodome` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `pyyaml` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `svgwrite` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `tablib` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-graphiql-debug-toolbar` | About 0 files contain it (github code search); an approximate reach signal only. [src 9] | approximate: files containing '"import django_graphiql_debug_toolbar" in:file' |
| `django-cors-headers` | About 2 files contain it (github code search); an approximate reach signal only. [src 13] | approximate: files containing '"import django_cors_headers" in:file' |
| `django-debug-toolbar` | About 2 files contain it (github code search); an approximate reach signal only. [src 14] | approximate: files containing '"import django_debug_toolbar" in:file' |
| `django-pglocks` | About 2 files contain it (github code search); an approximate reach signal only. [src 10] | approximate: files containing '"import django_pglocks" in:file' |
| `django-mptt` | About 3 files contain it (github code search); an approximate reach signal only. [src 15] | approximate: files containing '"import django_mptt" in:file' |
| `django-prometheus` | About 244 files contain it (github code search); an approximate reach signal only. [src 16] | approximate: files containing '"import django_prometheus" in:file' |
| `django-filter` | About 29.9k files contain it (github code search); an approximate reach signal only. [src 17] | approximate: files containing '"import django_filter" in:file' |
| `django` | About 3.3M files contain it (github code search); an approximate reach signal only. [src 18] | approximate: files containing '"import django" in:file' |

## Migration hints for dead and dormant criticals

No dead or dormant *critical* dependency has an entry in the alternatives map yet. Adding one is a PR against `maps/alternatives.json`.

## Every package

`depth 0` is declared by this project. `critical` means direct and not dev. Verdicts without enough evidence say `unknown`.

| package | version | verdict | critical | depth | last release | last commit | maintainers | bus factor |
|---|---|---|---|---|---|---|---|---|
| `django` | 3.2.6 | 🟢 thriving | yes | 0 | 2026-11-03 | 2026-11-16 | ? | 46 |
| `django-debug-toolbar` | 3.2.2 | 🟢 thriving | yes | 0 | 2026-09-01 | 2026-11-15 | 2 | 28 |
| `django-filter` | 2.4.0 | 🟢 thriving | yes | 0 | 2026-10-03 | 2026-10-03 | 2 | 3 |
| `django-mptt` | 0.13.2 | 🟢 thriving | yes | 0 | 2026-11-03 | 2026-11-03 | 2 | 5 |
| `django-rq` | 2.4.1 | 🟢 thriving | yes | 0 | 2026-08-30 | 2026-11-16 | 1 | 7 |
| `django-tables2` | 2.4.0 | 🟢 thriving | yes | 0 | 2026-08-30 | 2026-10-27 | 2 | 10 |
| `djangorestframework` | 3.12.4 | 🟢 thriving | yes | 0 | 2026-10-06 | 2026-11-16 | 5 | 44 |
| `drf-yasg` | 1.20.0 | 🟢 thriving | yes | 0 | 2026-10-09 | 2026-10-09 | 2 | 8 |
| `gunicorn` | 20.1.0 | 🟢 thriving | yes | 0 | 2026-11-12 | 2026-11-12 | 2 | 10 |
| `markdown` | 3.3.4 | 🟢 thriving | yes | 0 | 2026-11-05 | 2026-11-16 | 3 | 21 |
| `pillow` | 8.3.1 | 🟢 thriving | yes | 0 | 2026-10-16 | 2026-11-16 | 4 | 21 |
| `psycopg2-binary` | 2.9.1 | 🟢 thriving | yes | 0 | 2026-09-10 | 2026-11-01 | 1 | 3 |
| `pycryptodome` | 3.10.1 | 🟢 thriving | yes | 0 | 2026-11-15 | 2026-11-16 | 1 | 2 |
| `django-cors-headers` | 3.8.0 | 🟡 coasting | yes | 0 | 2025-09-18 | 2026-11-04 | 1 | 2 |
| `django-prometheus` | 2.1.0 | 🟡 coasting | yes | 0 | 2026-05-26 | 2026-11-02 | 1 | 11 |
| `django-redis` | 5.0.0 | 🟡 coasting | yes | 0 | 2026-06-02 | 2026-11-16 | 3 | 9 |
| `django-taggit` | 1.5.1 | 🟡 coasting | yes | 0 | 2026-11-02 | 2026-11-11 | 6 | 5 |
| `django-timezone-field` | 4.2.1 | 🟡 coasting | yes | 0 | 2026-06-06 | 2026-06-06 | 1 | 3 |
| `graphene-django` | 2.15.0 | 🟡 coasting | yes | 0 | 2025-03-13 | 2026-06-24 | 3 | 1 |
| `jinja2` | 3.0.1 | 🟡 coasting | yes | 0 | 2025-03-05 | 2025-06-14 | ? | ? |
| `mkdocs-material` | 7.2.5 | ⚪ unknown | dev | ? | — | — | ? | ? |
| `pyyaml` | 5.4.1 | 🟡 coasting | yes | 0 | 2025-09-29 | 2026-10-07 | 3 | 2 |
| `tablib` | 3.0.0 | 🟡 coasting | yes | 0 | 2026-07-31 | 2026-11-11 | 4 | 11 |
| `markdown-include` | 0.6.0 | 🟠 dormant | yes | 0 | 2023-02-07 | — | 2 | ? |
| `netaddr` | 0.8.0 | 🟠 dormant | yes | 0 | 2024-05-28 | 2024-07-05 | 2 | ? |
| `django-graphiql-debug-toolbar` | 0.2.0 | 🔴 dead | yes | 0 | 2021-08-28 | 2024-07-14 | 1 | ? |
| `django-pglocks` | 1.0.4 | 🔴 dead | yes | 0 | 2026-06-21 | 2026-06-21 | 1 | 1 |
| `svgwrite` | 1.4.1 | 🔴 dead | yes | 0 | 2022-07-14 | 2024-02-24 | 1 | ? |

## What this report does not know

- `django`: registry: no ownership roles published
- `django`: usage: pypistats did not answer (download counts unknown)
- `django`: triage: issue search did not answer
- `django-debug-toolbar`: usage: pypistats did not answer (download counts unknown)
- `django-debug-toolbar`: commits: 2 bot account(s) excluded from bus-factor counting
- `django-debug-toolbar`: triage: issue search did not answer
- `django-filter`: usage: pypistats did not answer (download counts unknown)
- `django-filter`: triage: issue search did not answer
- `django-mptt`: usage: pypistats did not answer (download counts unknown)
- `django-mptt`: triage: issue search did not answer
- `django-rq`: usage: pypistats did not answer (download counts unknown)
- `django-rq`: usage: GitHub code search did not answer
- `django-rq`: usage: no download or dependent counts available
- `django-rq`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-rq`: triage: issue search did not answer
- `django-tables2`: usage: pypistats did not answer (download counts unknown)
- `django-tables2`: usage: GitHub code search did not answer
- `django-tables2`: usage: no download or dependent counts available
- `django-tables2`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-tables2`: triage: issue search did not answer
- `djangorestframework`: usage: pypistats did not answer (download counts unknown)
- `djangorestframework`: usage: GitHub code search did not answer
- `djangorestframework`: usage: no download or dependent counts available
- `djangorestframework`: commits: 2 bot account(s) excluded from bus-factor counting
- `djangorestframework`: triage: issue search did not answer
- `drf-yasg`: usage: pypistats did not answer (download counts unknown)
- `drf-yasg`: usage: GitHub code search did not answer
- `drf-yasg`: usage: no download or dependent counts available
- `drf-yasg`: commits: 1 bot account(s) excluded from bus-factor counting
- `drf-yasg`: triage: issue search did not answer
- `gunicorn`: usage: pypistats did not answer (download counts unknown)
- `gunicorn`: usage: GitHub code search did not answer
- `gunicorn`: usage: no download or dependent counts available
- `gunicorn`: triage: issue search did not answer
- `markdown`: usage: pypistats did not answer (download counts unknown)
- `markdown`: usage: GitHub code search did not answer
- `markdown`: usage: no download or dependent counts available
- `markdown`: triage: issue search did not answer
- `pillow`: usage: pypistats did not answer (download counts unknown)
- `pillow`: usage: GitHub code search did not answer
- `pillow`: usage: no download or dependent counts available
- `pillow`: triage: issue search did not answer
- `psycopg2-binary`: usage: pypistats did not answer (download counts unknown)
- `psycopg2-binary`: usage: GitHub code search did not answer
- `psycopg2-binary`: usage: no download or dependent counts available
- `psycopg2-binary`: commits: 1 bot account(s) excluded from bus-factor counting
- `psycopg2-binary`: triage: issue search did not answer
- `pycryptodome`: usage: pypistats did not answer (download counts unknown)
- `pycryptodome`: usage: GitHub code search did not answer
- `pycryptodome`: usage: no download or dependent counts available
- `pycryptodome`: triage: issue search did not answer
- `django-cors-headers`: usage: pypistats did not answer (download counts unknown)
- `django-cors-headers`: commits: 2 bot account(s) excluded from bus-factor counting
- `django-cors-headers`: triage: issue search did not answer
- `django-prometheus`: usage: pypistats did not answer (download counts unknown)
- `django-prometheus`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-prometheus`: triage: issue search did not answer
- `django-redis`: usage: pypistats did not answer (download counts unknown)
- `django-redis`: usage: GitHub code search did not answer
- `django-redis`: usage: no download or dependent counts available
- `django-redis`: commits: 2 bot account(s) excluded from bus-factor counting
- `django-redis`: triage: issue search did not answer
- `django-taggit`: usage: pypistats did not answer (download counts unknown)
- `django-taggit`: usage: GitHub code search did not answer
- `django-taggit`: usage: no download or dependent counts available
- `django-taggit`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-taggit`: triage: issue search did not answer
- `django-timezone-field`: usage: pypistats did not answer (download counts unknown)
- `django-timezone-field`: usage: GitHub code search did not answer
- `django-timezone-field`: usage: no download or dependent counts available
- `django-timezone-field`: triage: issue search did not answer
- `graphene-django`: usage: pypistats did not answer (download counts unknown)
- `graphene-django`: usage: GitHub code search did not answer
- `graphene-django`: usage: no download or dependent counts available
- `graphene-django`: triage: issue search did not answer
- `jinja2`: registry: no ownership roles published
- `jinja2`: usage: pypistats did not answer (download counts unknown)
- `jinja2`: usage: GitHub code search did not answer
- `jinja2`: usage: no download or dependent counts available
- `jinja2`: triage: issue search did not answer
- `mkdocs-material`: registry: PyPI did not answer
- `mkdocs-material`: forge: no repository URL in registry metadata
- `pyyaml`: usage: pypistats did not answer (download counts unknown)
- `pyyaml`: usage: GitHub code search did not answer
- `pyyaml`: usage: no download or dependent counts available
- `pyyaml`: triage: issue search did not answer
- `tablib`: usage: pypistats did not answer (download counts unknown)
- `tablib`: usage: GitHub code search did not answer
- `tablib`: usage: no download or dependent counts available
- `tablib`: commits: 1 bot account(s) excluded from bus-factor counting
- `tablib`: triage: issue search did not answer
- `markdown-include`: usage: pypistats did not answer (download counts unknown)
- `markdown-include`: usage: GitHub code search did not answer
- `markdown-include`: usage: no download or dependent counts available
- `markdown-include`: forge: repository is not on GitHub (https://pypi.org/project/markdown-include/), so commit and issue history cannot be read
- `netaddr`: usage: pypistats did not answer (download counts unknown)
- `netaddr`: usage: GitHub code search did not answer
- `netaddr`: usage: no download or dependent counts available
- `netaddr`: triage: issue search did not answer
- `django-graphiql-debug-toolbar`: usage: pypistats did not answer (download counts unknown)
- `django-graphiql-debug-toolbar`: triage: issue search did not answer
- `django-pglocks`: usage: pypistats did not answer (download counts unknown)
- `django-pglocks`: triage: issue search did not answer
- `svgwrite`: usage: pypistats did not answer (download counts unknown)
- `svgwrite`: usage: GitHub code search did not answer
- `svgwrite`: usage: no download or dependent counts available
- `svgwrite`: triage: issue search did not answer

Verdicts follow rubric v1.0 (`docs/verdicts.md`). Dormant means no stable release for 730 days; dead means an archived repository, an explicit deprecation, or no release for 1460 days. If you think a threshold is wrong, that is a PR to the rubric, not a footnote.

## Sources

| # | Source | Retrieved |
|---|---|---|
| 1 | <https://pypi.org/pypi/django-graphiql-debug-toolbar/json> | 2026-11-16T18:38:46Z |
| 2 | <https://pypi.org/pypi/django-pglocks/json> | 2026-11-16T18:38:46Z |
| 3 | <https://api.github.com/repos/Xof/django-pglocks/commits> | 2026-11-16T18:38:46Z |
| 4 | <https://github.com/Xof> | 2026-11-16T18:38:46Z |
| 5 | <https://github.com/mozman/svgwrite> | 2026-11-16T18:38:46Z |
| 6 | <https://pypi.org/pypi/svgwrite/json> | 2026-11-16T18:38:46Z |
| 7 | <https://pypi.org/pypi/markdown-include/json> | 2026-11-16T18:38:46Z |
| 8 | <https://pypi.org/pypi/netaddr/json> | 2026-11-16T18:38:46Z |
| 9 | <https://api.github.com/search/code?q=%22import+django_graphiql_debug_toolbar%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 10 | <https://api.github.com/search/code?q=%22import+django_pglocks%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 11 | <https://api.github.com/repos/graphql-python/graphene-django/commits> | 2026-11-16T18:38:46Z |
| 12 | <https://github.com/superlevure> | 2026-11-16T18:38:46Z |
| 13 | <https://api.github.com/search/code?q=%22import+django_cors_headers%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 14 | <https://api.github.com/search/code?q=%22import+django_debug_toolbar%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 15 | <https://api.github.com/search/code?q=%22import+django_mptt%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 16 | <https://api.github.com/search/code?q=%22import+django_prometheus%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 17 | <https://api.github.com/search/code?q=%22import+django_filter%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |
| 18 | <https://api.github.com/search/code?q=%22import+django%22+in%3Afile&per_page=1> | 2026-11-16T18:38:46Z |

_Retrieved-at dates are when DeadLedger first stored each response. Re-running offline reuses those dates rather than pretending the world was re-observed._
