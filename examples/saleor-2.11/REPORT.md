# Mortality report: saleor

**Verdict as of 2026-11-17** · ecosystem `pypi` · 206 packages · rubric v1.0 · alternatives map v1.0.0 · DeadLedger 0.1.0

Audited `examples/saleor-2.11/poetry.lock`. The report describes the tree as observed on **2026-11-17**; every claim below is followed by a source marker resolved at the bottom.

## Summary

- **206 packages** audited (56 critical: direct, non-dev; 150 transitive or dev).
- **37 dead**, **17 dormant**, 47 coasting, 105 thriving, 0 unknown.
- **15 critical package(s) need a decision**: `django-versatileimagefield` (dormant), `google-i18n-address` (dormant), `openpyxl` (dormant), `dj-email-url` (dead), `django-measurement` (dead), `draftjs-sanitizer` (dead), `google-measurement-protocol` (dead), `html-to-draftjs` (dead), `jaeger-client` (dead), `maxminddb-geolite2` (dead), `opentracing` (dead), `prices` (dead), `purl` (dead), `python-magic-bin` (dead), `text-unidecode` (dead).
- **15 package(s) have a bus factor of 1** in the last 12 months of commits.
- Ledger: 6 new death(s), 13 worsening(s), 8 new single-maintainer flag(s).

### The headline

- `apipkg` **dormant** (dev-only) — The newest stable release is 3.2y old (2023-09-19); the project has not published for two years. [src 1] [src 2]
- `cairocffi` **dormant** (transitive, depth 1) — The newest stable release is 2.4y old (2024-06-18); the project has not published for two years. [src 3] [src 4]
- `click-didyoumean` **dormant** (transitive, depth 1) — The newest stable release is 2.6y old (2024-03-24); the project has not published for two years. [src 5]
- `colorama` **dormant** (transitive, depth 1) — The newest stable release is 4.1y old (2022-10-25); nothing has shipped in 4+ years. [src 6] [src 7]
- `defusedxml` **dormant** (transitive, depth 2) — The newest stable release is 3.1y old (2023-09-29); the project has not published for two years. [src 8]

## What is dead or dying

### dj-email-url 1.0.1 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Use an URL to configure email backend settings in your Django Application.

**Evidence**

- The newest stable release is 4.1y old (2022-09-24); nothing has shipped in 4+ years. [src 9]
  - `last_release_age_days`=1514
- The registry lists a single owner (migonzalvar); the forge was not readable. [src 9]
  - `maintainers`=1
- Only 0% of issues opened in the last year were closed (0 of 1); inbound reports are piling up. [src 10]
  - `triage_rate`=0.00, `issues_created_12mo`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### django-measurement 3.2.3 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Convenient fields and classes for handling measurements

**Evidence**

- The newest stable release is 4.7y old (2022-02-28); nothing has shipped in 4+ years. [src 11]
  - `last_release_age_days`=1722
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### draftjs-sanitizer 1.0.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Convert basic HTML into DraftJS JSON format.

**Evidence**

- The newest stable release is 7.3y old (2019-07-18); nothing has shipped in 4+ years. [src 12]
  - `last_release_age_days`=2678
- The registry lists a single owner (NyanKiyoshi); the forge was not readable. [src 12]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### google-measurement-protocol 1.1.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

A Python implementation of Google Analytics Measurement Protocol

**Evidence**

- The newest stable release is 6.2y old (2020-09-04); nothing has shipped in 4+ years. [src 13]
  - `last_release_age_days`=2264
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://pypi.org/project/google-measurement-protocol/), so commit and issue history cannot be read

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### html-to-draftjs 1.0.1 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Convert basic HTML into DraftJS JSON format.

**Evidence**

- The newest stable release is 7.3y old (2019-07-31); nothing has shipped in 4+ years. [src 14]
  - `last_release_age_days`=2665
- The registry lists a single owner (NyanKiyoshi); the forge was not readable. [src 14]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### jaeger-client 4.3.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Jaeger Python OpenTracing Tracer implementation

**Evidence**

- The repository jaegertracing/jaeger-client-python is archived, so no further commits or releases can land without a deliberate revival. [src 15]
  - `archived`=True
- The newest stable release is 5.2y old (2021-09-14); nothing has shipped in 4+ years. [src 16]
  - `last_release_age_days`=1889
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### maxminddb-geolite2 2018.703 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Provides access to the geolite2 database.  This product includes GeoLite2 data created by MaxMind, available from http://www.maxmind.com/

**Evidence**

- The newest stable release is 8.3y old (2018-07-18); nothing has shipped in 4+ years. [src 17]
  - `last_release_age_days`=3043
- The registry lists a single owner (rr2do2); the forge was not readable. [src 17]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### opentracing 2.3.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

OpenTracing API for Python. See documentation at http://opentracing.io

**Evidence**

- The repository opentracing/opentracing-python is archived, so no further commits or releases can land without a deliberate revival. [src 18]
  - `archived`=True
- The newest stable release is 6.0y old (2020-11-19); nothing has shipped in 4+ years. [src 19]
  - `last_release_age_days`=2188
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### prices 1.1.0 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

Python price handling for humans

**Evidence**

- The newest stable release is 4.1y old (2022-10-07); nothing has shipped in 4+ years. [src 20]
  - `last_release_age_days`=1501
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### purl 1.5 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

An immutable URL class for easy URL-building and manipulation

**Evidence**

- The newest stable release is 5.5y old (2021-05-15); nothing has shipped in 4+ years. [src 21]
  - `last_release_age_days`=2011
- The registry lists a single owner (codeinthehole.com); the forge was not readable. [src 21]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### python-magic-bin 0.4.14 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

File type identification using libmagic binary package

**Evidence**

- The repository julian-r/python-magic is archived, so no further commits or releases can land without a deliberate revival. [src 22]
  - `archived`=True
- The newest stable release is 9.1y old (2017-10-02); nothing has shipped in 4+ years. [src 23]
  - `last_release_age_days`=3332
- Exactly one person has committed in the last year (julian-r, last commit 2026-09-18 — 1.9mo ago). [src 24] [src 25]
  - `committers_12mo`=1, `lead_committer_last_activity`=2026-09-18, `lead_committer_last_activity_days`=59
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.
- Bus factor 1 — julian-r is the only committer in the last 12 months (last commit 2026-09-18). If they stop, this stops. Vendoring is cheaper than waiting for a crisis if this package is critical.

### text-unidecode 1.3 — 🔴 dead

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

The most basic Text::Unidecode port

**Evidence**

- The newest stable release is 7.2y old (2019-08-30); nothing has shipped in 4+ years. [src 26]
  - `last_release_age_days`=2635
- The registry lists a single owner (kmike); the forge was not readable. [src 26]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Critical: this is your decision. Fork, vendor, or migrate — the alternatives below are the starting point for that ADR.

### django-versatileimagefield 2.0 — 🟠 dormant

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

A drop-in replacement for django's ImageField that provides a flexible, intuitive and easily-extensible interface for creating new images from the one assigned to the field.

**Evidence**

- The newest stable release is 2.8y old (2024-01-21); the project has not published for two years. [src 27]
  - `last_release_age_days`=1030
- The registry lists a single owner (respondcreate); the forge was not readable. [src 27]
  - `maintainers`=1
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### google-i18n-address 2.4.0 — 🟠 dormant

*pypi · critical (direct, non-dev) · verdict confidence: high · rubric v1.0*

Address validation helpers for Google's i18n address database

**Evidence**

- The newest stable release is 2.2y old (2024-09-04); the project has not published for two years. [src 28]
  - `last_release_age_days`=803
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### openpyxl 3.0.5 — 🟠 dormant

*pypi · critical (direct, non-dev) · verdict confidence: medium · rubric v1.0*

A Python library to read/write Excel 2010 xlsx/xlsm files

**Evidence**

- The newest stable release is 2.4y old (2024-06-28); the project has not published for two years. [src 29]
  - `last_release_age_days`=871
- Orphan check: no source published a usage or dependent count.

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://foss.heptapod.net/openpyxl/openpyxl), so commit and issue history cannot be read

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### appdirs 1.4.4 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

A small Python module for determining appropriate platform-specific dirs, e.g. a "user data dir".

**Evidence**

- The newest stable release is 6.5y old (2020-05-11); nothing has shipped in 4+ years. [src 30]
  - `last_release_age_days`=2380
- The registry lists a single owner (zoofood); the forge was not readable. [src 30]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### atomicwrites 1.4.0 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

Atomic file writes.

**Evidence**

- The repository untitaker/python-atomicwrites is archived, so no further commits or releases can land without a deliberate revival. [src 31]
  - `archived`=True
- The newest stable release is 4.4y old (2022-07-09); nothing has shipped in 4+ years. [src 32]
  - `last_release_age_days`=1592
- The registry lists a single owner (untitaker); the forge was not readable. [src 32]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### beautifultable 0.7.0 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

Print text tables for terminals

**Evidence**

- The newest stable release is 4.5y old (2022-05-06); nothing has shipped in 4+ years. [src 33]
  - `last_release_age_days`=1655
- The registry lists a single owner (pri22296); the forge was not readable. [src 33]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### codecov 2.1.10 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

Hosted coverage reports for GitHub, Bitbucket and Gitlab

**Evidence**

- The repository codecov/codecov-python is archived, so no further commits or releases can land without a deliberate revival. [src 34]
  - `archived`=True
- The newest stable release is 3.6y old (2023-04-17); the project has not published for two years. [src 35]
  - `last_release_age_days`=1309

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### django-debug-toolbar-request-history 0.1.3 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

Request History Panel for Django Debug Toolbar

**Evidence**

- The newest stable release is 5.1y old (2021-10-19); nothing has shipped in 4+ years. [src 36]
  - `last_release_age_days`=1854
- The registry lists a single owner (djsutho); the forge was not readable. [src 36]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### django-graphiql-debug-toolbar 0.1.4 — 🔴 dead

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

Django Debug Toolbar for GraphiQL IDE.

**Evidence**

- The newest stable release is 5.2y old (2021-08-28); nothing has shipped in 4+ years. [src 37]
  - `last_release_age_days`=1906
- The registry lists a single owner (mongkok); the forge was not readable. [src 37]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### enmerkar 0.7.1 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

Utilities for using Babel in Django

**Evidence**

- The newest stable release is 7.0y old (2019-12-02); nothing has shipped in 4+ years. [src 38]
  - `last_release_age_days`=2541

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### gitdb 4.0.5 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

Git Object Database

**Evidence**

- The repository gitpython-developers/gitdb is archived, so no further commits or releases can land without a deliberate revival. [src 39]
  - `archived`=True

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 1 bot account(s) excluded from bus-factor counting

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### google-crc32c 1.0.0 — 🔴 dead

*pypi · transitive, depth 2 · verdict confidence: medium · rubric v1.0*

A python wrapper of the C library 'Google CRC32C'

**Evidence**

- The repository googleapis/python-crc32c is archived, so no further commits or releases can land without a deliberate revival. [src 40]
  - `archived`=True

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 1 bot account(s) excluded from bus-factor counting

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### graphql-relay 2.0.1 — 🔴 dead

*pypi · transitive, depth 2 · verdict confidence: high · rubric v1.0*

Relay library for graphql-core

**Evidence**

- The newest stable release is 4.6y old (2022-04-16); nothing has shipped in 4+ years. [src 41]
  - `last_release_age_days`=1675

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### html5lib 1.1 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

HTML parser based on the WHATWG HTML specification

**Evidence**

- The newest stable release is 6.4y old (2020-06-22); nothing has shipped in 4+ years. [src 42]
  - `last_release_age_days`=2338
- Only 0% of issues opened in the last year were closed (0 of 5); inbound reports are piling up. [src 43]
  - `triage_rate`=0.00, `issues_created_12mo`=5

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### jdcal 1.4.1 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

Julian dates from proleptic Gregorian and Julian calendars.

**Evidence**

- The newest stable release is 7.6y old (2019-04-24); nothing has shipped in 4+ years. [src 44]
  - `last_release_age_days`=2763

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### jsonfield 3.1.0 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

A reusable Django field that allows you to store validated JSON in your model.

**Evidence**

- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 45]
  - `deprecated`=True

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### promise 2.3 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Promises/A+ implementation for Python

**Evidence**

- The newest stable release is 6.9y old (2019-12-18); nothing has shipped in 4+ years. [src 46]
  - `last_release_age_days`=2525

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### py 1.9.0 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

library with cross-python path, ini-parsing, io, code, log facilities

**Evidence**

- The newest stable release is 5.0y old (2021-11-04); nothing has shipped in 4+ years. [src 47]
  - `last_release_age_days`=1838

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://py.readthedocs.io/), so commit and issue history cannot be read

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### pydocstyle 5.1.1 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

Python docstring style checker

**Evidence**

- The repository PyCQA/pydocstyle is archived, so no further commits or releases can land without a deliberate revival. [src 48]
  - `archived`=True
- The newest stable release is 3.8y old (2023-01-17); the project has not published for two years. [src 49]
  - `last_release_age_days`=1399

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### pylint-celery 0.3 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

pylint-celery is a Pylint plugin to aid Pylint in recognising and understandingerrors caused when using the Celery library

**Evidence**

- The newest stable release is 12.1y old (2014-09-25); nothing has shipped in 4+ years. [src 50]
  - `last_release_age_days`=4435
- The registry lists a single owner (carlio); the forge was not readable. [src 50]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### pytest-forked 1.3.0 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

run tests in isolated forked subprocesses

**Evidence**

- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 51]
  - `deprecated`=True

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### pytest-vcr 1.0.2 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

Plugin for managing VCR.py cassettes

**Evidence**

- The newest stable release is 7.6y old (2019-04-26); nothing has shipped in 4+ years. [src 52]
  - `last_release_age_days`=2761
- The registry lists a single owner (ktosiek); the forge was not readable. [src 52]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### rsa 4.6 — 🔴 dead

*pypi · transitive, depth 2 · verdict confidence: medium · rubric v1.0*

Pure-Python RSA implementation

**Evidence**

- The repository sybrenstuvel/python-rsa is archived, so no further commits or releases can land without a deliberate revival. [src 53]
  - `archived`=True
- The registry lists a single owner (sybrenstuvel); the forge was not readable. [src 54]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### smmap 3.0.4 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

A pure Python implementation of a sliding window memory map manager

**Evidence**

- The repository gitpython-developers/smmap is archived, so no further commits or releases can land without a deliberate revival. [src 55]
  - `archived`=True

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 2 bot account(s) excluded from bus-factor counting
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### toml 0.10.1 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

Python Library for Tom's Obvious, Minimal Language

**Evidence**

- The newest stable release is 6.0y old (2020-11-01); nothing has shipped in 4+ years. [src 56]
  - `last_release_age_days`=2207
- The registry lists a single owner (uiri); the forge was not readable. [src 56]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### transifex-client 0.14.1 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

A command line interface for Transifex

**Evidence**

- The newest stable release is 4.9y old (2021-12-24); nothing has shipped in 4+ years. [src 57]
  - `last_release_age_days`=1788
- The registry lists a single owner (transifex); the forge was not readable. [src 57]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://www.transifex.com), so commit and issue history cannot be read

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### typed-ast 1.4.1 — 🔴 dead

*pypi · dev dependency · verdict confidence: medium · rubric v1.0*

a fork of Python 2 and 3 ast modules with type comment support

**Evidence**

- The repository python/typed_ast is archived, so no further commits or releases can land without a deliberate revival. [src 58]
  - `archived`=True
- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 59]
  - `deprecated`=True
- The newest stable release is 3.4y old (2023-07-04); the project has not published for two years. [src 59]
  - `last_release_age_days`=1231

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Dev-only: nothing ships to production. Remove it when convenient.

### watchgod 0.6 — 🔴 dead

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Simple, modern file watching and code reload in python.

**Evidence**

- The package is deprecated: PyPI classifier: Development Status :: 7 - Inactive. [src 60]
  - `deprecated`=True
- The newest stable release is 4.6y old (2022-04-01); nothing has shipped in 4+ years. [src 60]
  - `last_release_age_days`=1690

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 1 bot account(s) excluded from bus-factor counting
- triage: issue search did not answer

**What to do**

- Transitive: pin the version you have, then track the parent that pulls it in.

### apipkg 1.5 — 🟠 dormant

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

apipkg: namespace control and lazy-import mechanism

**Evidence**

- The newest stable release is 3.2y old (2023-09-19); the project has not published for two years. [src 1]
  - `last_release_age_days`=1154
- The repository is still moving (6 commit(s) in the last year, latest by Copilot on 2026-11-09) but the newest release is 3.2y old: development continues without publishing. [src 1] [src 2]
  - `commits_12mo`=6, `days_commits_after_release`=1147

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

### cairocffi 1.1.0 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

cffi-based cairo bindings for Python

**Evidence**

- The newest stable release is 2.4y old (2024-06-18); the project has not published for two years. [src 3]
  - `last_release_age_days`=881
- The repository is still moving (7 commit(s) in the last year, latest by liZe on 2026-08-28) but the newest release is 2.4y old: development continues without publishing. [src 3] [src 4]
  - `commits_12mo`=7, `days_commits_after_release`=801

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

### click-didyoumean 0.0.3 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

Enables git-like *did-you-mean* feature in click

**Evidence**

- The newest stable release is 2.6y old (2024-03-24); the project has not published for two years. [src 5]
  - `last_release_age_days`=967

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### colorama 0.4.4 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

Cross-platform colored terminal text.

**Evidence**

- The newest stable release is 4.1y old (2022-10-25); nothing has shipped in 4+ years. [src 6]
  - `last_release_age_days`=1484
- The repository is still moving (3 commit(s) in the last year, latest by brianwing90 on 2026-05-13) but the newest release is 4.1y old: development continues without publishing. [src 6] [src 7]
  - `commits_12mo`=3, `days_commits_after_release`=1296

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

### defusedxml 0.6.0 — 🟠 dormant

*pypi · transitive, depth 2 · verdict confidence: high · rubric v1.0*

XML bomb protection for Python stdlib modules

**Evidence**

- The newest stable release is 3.1y old (2023-09-29); the project has not published for two years. [src 8]
  - `last_release_age_days`=1144
- The registry lists a single owner (tiran); the forge was not readable. [src 8]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### et-xmlfile 1.0.1 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

An implementation of lxml.xmlfile for the standard library

**Evidence**

- The newest stable release is 2.1y old (2024-10-25); the project has not published for two years. [src 61]
  - `last_release_age_days`=752
- The registry lists a single owner (CharlieX); the forge was not readable. [src 61]
  - `maintainers`=1

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://foss.heptapod.net/openpyxl/et_xmlfile), so commit and issue history cannot be read

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### graphene 2.1.8 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: high · rubric v1.0*

GraphQL Framework for Python

**Evidence**

- The newest stable release is 2.0y old (2024-11-09); the project has not published for two years. [src 62]
  - `last_release_age_days`=737
- Only 0% of issues opened in the last year were closed (0 of 4); inbound reports are piling up. [src 63]
  - `triage_rate`=0.00, `issues_created_12mo`=4

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### mccabe 0.6.1 — 🟠 dormant

*pypi · dev dependency · verdict confidence: high · rubric v1.0*

McCabe checker, plugin for flake8

**Evidence**

- The newest stable release is 4.8y old (2022-01-24); nothing has shipped in 4+ years. [src 64]
  - `last_release_age_days`=1758
- The repository is still moving (4 commit(s) in the last year, latest by sigmavirus24 on 2026-10-12) but the newest release is 4.8y old: development continues without publishing. [src 64] [src 65]
  - `commits_12mo`=4, `days_commits_after_release`=1722

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

### measurement 3.2.0 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Easily use and manipulate unit-aware measurements in Python.

**Evidence**

- The newest stable release is 3.8y old (2023-01-10); the project has not published for two years. [src 66]
  - `last_release_age_days`=1406

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (https://pypi.org/project/measurement/), so commit and issue history cannot be read

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### python-magic 0.4.18 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

File type identification using libmagic

**Evidence**

- The newest stable release is 4.4y old (2022-06-07); nothing has shipped in 4+ years. [src 67]
  - `last_release_age_days`=1623
- The repository is still moving (10 commit(s) in the last year, latest by ddelange on 2026-10-14) but the newest release is 4.4y old: development continues without publishing. [src 67] [src 68]
  - `commits_12mo`=10, `days_commits_after_release`=1589

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 1 bot account(s) excluded from bus-factor counting
- triage: issue search did not answer

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

### rx 1.6.1 — 🟠 dormant

*pypi · transitive, depth 2 · verdict confidence: medium · rubric v1.0*

Reactive Extensions (Rx) for Python

**Evidence**

- The newest stable release is 3.9y old (2022-12-17); the project has not published for two years. [src 69]
  - `last_release_age_days`=1430

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- forge: repository is not on GitHub (http://reactivex.io), so commit and issue history cannot be read

**What to do**

- Dormant but not dead: pin a version, watch for a successor, and if you depend on bug fixes, budget a fork.

### threadloop 1.0.2 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Tornado IOLoop Backed Concurrent Futures

**Evidence**

- The newest stable release is 10.6y old (2016-04-01); nothing has shipped in 4+ years. [src 70]
  - `last_release_age_days`=3881
- The repository is still moving (2 commit(s) in the last year, latest by Grayson Koonce <grayson.koonce@gmail.com> on 2026-09-08) but the newest release is 10.6y old: development continues without publishing. [src 70] [src 71]
  - `commits_12mo`=2, `days_commits_after_release`=3812
- Exactly one person has committed in the last year (Grayson Koonce <grayson.koonce@gmail.com>, last commit 2026-09-08 — 2.3mo ago). [src 72]
  - `committers_12mo`=1, `lead_committer_last_activity`=2026-09-08, `lead_committer_last_activity_days`=69

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.
- Bus factor 1 — Grayson Koonce <grayson.koonce@gmail.com> is the only committer in the last 12 months (last commit 2026-09-08). If they stop, this stops. Vendoring is cheaper than waiting for a crisis if this package is critical.

### typing-inspect 0.6.0 — 🟠 dormant

*pypi · transitive, depth 2 · verdict confidence: medium · rubric v1.0*

Runtime inspection utilities for typing module.

**Evidence**

- The newest stable release is 3.5y old (2023-05-24); the project has not published for two years. [src 73]
  - `last_release_age_days`=1272
- The repository is still moving (1 commit(s) in the last year, latest by leon-sony on 2026-01-18) but the newest release is 3.5y old: development continues without publishing. [src 73] [src 74]
  - `commits_12mo`=1, `days_commits_after_release`=969
- Exactly one person has committed in the last year (leon-sony, last commit 2026-01-18 — 9.9mo ago). [src 75] [src 76]
  - `committers_12mo`=1, `lead_committer_last_activity`=2026-01-18, `lead_committer_last_activity_days`=302

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- triage: issue search did not answer

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.
- Bus factor 1 — leon-sony is the only committer in the last 12 months (last commit 2026-01-18). If they stop, this stops. Vendoring is cheaper than waiting for a crisis if this package is critical.

### vine 5.0.0 — 🟠 dormant

*pypi · transitive, depth 1 · verdict confidence: medium · rubric v1.0*

Python promises.

**Evidence**

- The newest stable release is 3.0y old (2023-11-05); the project has not published for two years. [src 77]
  - `last_release_age_days`=1107
- The repository is still moving (3 commit(s) in the last year, latest by nikolas on 2026-11-16) but the newest release is 3.0y old: development continues without publishing. [src 77] [src 78]
  - `commits_12mo`=3, `days_commits_after_release`=1107

**Gaps**

- usage: pypistats did not answer (download counts unknown)
- usage: GitHub code search did not answer
- usage: no download or dependent counts available
- commits: 2 bot account(s) excluded from bus-factor counting
- triage: issue search did not answer

**What to do**

- Alive but not publishing: the fixes you want may already be on main. Pin a git ref (or ask for a release) before you fork.

## Bus factor: who is one person away from a fork

A package appears here when exactly one account committed to its public repository in the 12 months before retrieval. That is a fact about the repository, not a prediction.

| package | critical | last commit by that person | commits |
|---|---|---|---|
| `django-prices` [src 79] [src 80] | yes | filipmlynarski-mirumee, 2026-01-14 | 2 |
| `django-storages` [src 81] [src 82] | yes | jasongi, 2026-08-02 | 1 |
| `graphene-django` [src 83] [src 84] | yes | superlevure, 2026-06-24 | 1 |
| `python-magic-bin` [src 24] [src 25] | yes | julian-r, 2026-09-18 | 1 |
| `razorpay` [src 85] [src 86] | yes | ankitdas13, 2026-03-09 | 3 |
| `cfgv` [src 87] [src 88] | no | asottile, 2026-11-04 | 13 |
| `cssselect2` [src 89] [src 90] | no | liZe, 2026-10-25 | 14 |
| `django-appconf` [src 91] [src 92] | no | sparrowt, 2025-12-08 | 1 |
| `django-js-asset` [src 93] [src 94] | no | matthiask, 2026-11-15 | 89 |
| `pyflakes` [src 95] [src 88] | no | asottile, 2026-10-28 | 55 |
| `pylint-plugin-utils` [src 96] [src 97] | no | carlio, 2026-11-03 | 3 |
| `pytest-django-queries` [src 98] [src 99] | no | NyanKiyoshi, 2026-08-10 | 11 |
| `threadloop` [src 72] | no | Grayson Koonce <grayson.koonce@gmail.com>, 2026-09-08 | 2 |
| `typing-inspect` [src 75] [src 76] | no | leon-sony, 2026-01-18 | 1 |
| `webencodings` [src 100] [src 101] | no | liZe, 2026-10-25 | 10 |

## Orphan simulation: if this dies, who else uses it?

One line per critical (direct, non-dev) dependency. `exact` means the registry publishes a dependent count; `approximate` means the number is downloads or import sites, which measure use, not dependents.

| package | if it dies | basis |
|---|---|---|
| `adyen` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `babel` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `boto3` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `braintree` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `celery` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `dj-database-url` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `dj-email-url` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-cache-url` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-countries` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-filter` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-measurement` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-mptt` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-phonenumber-field` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-prices` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-prices-openexchangerates` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-prices-vatlayer` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-redis` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-storages` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-templated-email` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `django-versatileimagefield` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `draftjs-sanitizer` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `faker` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `freezegun` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `google-cloud-pubsub` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `google-cloud-storage` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `google-i18n-address` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `google-measurement-protocol` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `graphene-django` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `graphene-federation` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `gunicorn` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `html-to-draftjs` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `jaeger-client` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `markdown` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `maxminddb` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `maxminddb-geolite2` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `oauthlib` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `openpyxl` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `opentracing` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `petl` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `phonenumberslite` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `prices` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `psycopg2-binary` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `purl` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `pyjwt` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `python-json-logger` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `python-magic-bin` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `pytimeparse` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `razorpay` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `requests` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `sentry-sdk` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `stripe` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `text-unidecode` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `tqdm` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `uvicorn` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |
| `weasyprint` | no source published a usage or dependent count.  | unknown: usage: pypistats did not answer (download counts unknown); usage: GitHub code search did not answer; usage: no download or dependent counts available |

## Migration hints for dead and dormant criticals

From the community alternatives map v1.0.0 (`maps/alternatives.json`). The cost label is a migration *proxy*: `near drop-in` means the measured public API mostly overlaps, `rewrite-shaped` means it does not. Entries with no measurement say so.

### django-versatileimagefield

- **django-imagekit** — Maintained image-field processing for Django with caching pipelines. *Cost: moderate.*
  - <https://github.com/matthewwithanm/django-imagekit>
- **django-pictures** — Modern responsive-images field; smaller surface, active. *Cost: moderate.*
  - <https://github.com/codingjoe/django-pictures>

### dj-email-url

- **environs** — Actively maintained; env.dj_email_url() is the same parse function. *Cost: near drop-in (100% of measured API covered).*
  - Basis: measured: environs.dj_email_url / Env.dj_email_url provide the identical parsing helper
  - <https://github.com/sloria/environs>
- **dj-database-url's email companion** — If you already use dj-database-url, the same author's email parser moved to environs. *Cost: minor.*

### draftjs-sanitizer

- **nh3** — Rust-backed HTML sanitiser, actively maintained, the current default choice for Python. *Cost: rewrite-shaped (0% of measured API covered).*
  - Convert DraftJS JSON to HTML first, sanitise the HTML, then convert back.
  - Basis: measured: nh3 sanitises HTML strings; draftjs-sanitizer filters DraftJS block trees -- no shared surface
  - <https://github.com/messense/nh3>
- **bleach** — Widely used HTML sanitiser (itself deprecated in 2023, so prefer nh3). *Cost: rewrite.*
  - Listed for completeness; bleach is in the same mortality bucket as this package.
  - <https://github.com/mozilla/bleach>

### html-to-draftjs

- **vendor the package** — It is ~300 lines of pure-python with no dependencies; copying it into your tree beats depending on an abandoned package. *Cost: minor.*
  - Vendoring also fixes the transitive risk: nothing else in your tree pulls it in.
  - <https://github.com/NyanKiyoshi/html-to-draftjs>
- **write the converter against draftjs-js on the frontend** — If the HTML originates in your editor UI, convert there and send DraftJS JSON over the wire. *Cost: moderate.*

### jaeger-client

- **opentelemetry-sdk** — OpenTelemetry replaced the Jaeger client libraries; Jaeger ingests OTLP directly. *Cost: rewrite-shaped (10% of measured API covered).*
  - Basis: estimated: tracing concepts map 1:1 but the initialisation and span APIs are entirely different
  - <https://github.com/open-telemetry/opentelemetry-python>

### maxminddb-geolite2

- **geoip2** — Official MaxMind reader, still maintained; download the GeoLite2 database yourself. *Cost: moderate.*
  - The package's only job was bundling the database, which MaxMind now requires via account-based download.
  - <https://github.com/maxmind/GeoIP2-python>
- **ip2country** — Actively maintained offline IP-to-country lookup with a current bundled database. *Cost: minor.*
  - <https://pypi.org/project/ip2country/>

### purl

- **yarl** — Actively maintained immutable URL object with a comparable path/query API. *Cost: moderate.*
  - purl exposes .path, .query, .add_query_param(); yarl uses .path, .query, .update_query(). Method names differ, shapes are close.
  - <https://github.com/aio-libs/yarl>
- **urllib.parse** — Stdlib alternative: no dependency to maintain, but no immutable object model. *Cost: rewrite-shaped (0% of measured API covered).*
  - Zero dependency risk after migrating. Rewrite is mechanical but touches every call site.
  - Basis: estimated: stdlib functions (urlsplit/urlencode) not a class-for-class mapping; measured surface would understate rewrite work
  - <https://docs.python.org/3/library/urllib.parse.html>

### python-magic-bin

- **python-magic** — Drops the bundled libmagic wheel but keeps the maintained API; install libmagic with your system package manager. *Cost: near drop-in (100% of measured API covered).*
  - Basis: measured: python-magic-bin is a platform-wheel packaging of python-magic itself
  - <https://github.com/ahupp/python-magic>
- **filetype** — Pure-python magic-number detection; no libmagic, no C dependency. *Cost: rewrite-shaped (20% of measured API covered).*
  - Basis: estimated: filetype.guess() returns an extension, python-magic returns MIME descriptions with an incompatible call shape
  - <https://github.com/h2non/filetype.py>

### text-unidecode

- **unidecode** — Parent project, maintained again since 2022; ASCII transliteration with a larger table. *Cost: near drop-in (100% of measured API covered).*
  - Basis: measured: unidecode.unidecode() is the function text-unidecode forked; same signature
  - <https://github.com/avian2/unidecode>
- **anyascii** — Maintained pure-python transliteration with better coverage of non-Latin scripts. *Cost: near drop-in (90% of measured API covered).*
  - Basis: measured: anyascii.anyascii() mirrors unidecode.unidecode() semantics
  - <https://github.com/anyascii/anyascii>

## Every package

`depth 0` is declared by this project. `critical` means direct and not dev. Verdicts without enough evidence say `unknown`.

| package | version | verdict | critical | depth | last release | last commit | maintainers | bus factor |
|---|---|---|---|---|---|---|---|---|
| `adyen` | 3.0.0 | 🟢 thriving | yes | 0 | 2026-09-17 | 2026-11-13 | 2 | 7 |
| `amqp` | 5.0.1 | 🟢 thriving | no | 2 | 2026-11-02 | 2026-11-02 | 3 | 11 |
| `asgiref` | 3.2.10 | 🟢 thriving | no | 1 | 2026-10-23 | 2026-11-06 | 2 | 20 |
| `astroid` | 2.4.2 | 🟢 thriving | dev | ? | 2026-10-08 | 2026-11-17 | 8 | 21 |
| `billiard` | 3.6.3.0 | 🟢 thriving | no | 1 | 2026-11-02 | 2026-11-02 | 5 | 15 |
| `black` | 19.10b0 | 🟢 thriving | dev | ? | 2026-10-10 | 2026-11-16 | 5 | 44 |
| `boto3` | 1.16.7 | 🟢 thriving | yes | 0 | 2026-11-16 | 2026-11-17 | 1 | 3 |
| `botocore` | 1.19.7 | 🟢 thriving | no | 1 | 2026-11-16 | 2026-11-16 | 2 | 10 |
| `cachetools` | 4.1.1 | 🟢 thriving | no | 2 | 2026-11-14 | 2026-11-16 | 1 | 16 |
| `cairosvg` | 2.4.2 | 🟢 thriving | no | 1 | 2026-09-07 | 2026-09-07 | 2 | 4 |
| `celery` | 5.0.1 | 🟢 thriving | yes | 0 | 2026-11-05 | 2026-11-16 | 5 | 38 |
| `certifi` | 2020.6.20 | 🟢 thriving | no | 1 | 2026-10-23 | 2026-11-16 | 1 | 6 |
| `cffi` | 1.14.3 | 🟢 thriving | no | 1 | 2026-08-03 | 2026-11-13 | 8 | 19 |
| `chardet` | 3.0.4 | 🟢 thriving | no | 1 | 2026-10-18 | 2026-11-16 | 3 | 16 |
| `click` | 7.1.2 | 🟢 thriving | no | 1 | 2026-11-06 | 2026-11-16 | ? | 4 |
| `click-repl` | 0.1.6 | 🟢 thriving | no | 1 | 2026-10-05 | 2026-11-01 | 1 | 7 |
| `coverage` | 5.3 | 🟢 thriving | dev | ? | 2026-11-12 | 2026-11-16 | 1 | 18 |
| `cssselect2` | 0.3.0 | 🟢 thriving | no | 1 | 2026-08-31 | 2026-10-25 | 2 | 1 |
| `distlib` | 0.3.1 | 🟢 thriving | dev | ? | 2026-10-16 | 2026-11-05 | 1 | 21 |
| `django` | 3.1.2 | 🟢 thriving | yes | 0 | 2026-11-03 | 2026-11-16 | ? | 46 |
| `django-countries` | 6.1.3 | 🟢 thriving | yes | 0 | 2026-09-10 | 2026-10-29 | 1 | 4 |
| `django-debug-toolbar` | 3.1.1 | 🟢 thriving | dev | ? | 2026-09-01 | 2026-11-15 | 2 | 28 |
| `django-filter` | 2.4.0 | 🟢 thriving | yes | 0 | 2026-10-03 | 2026-10-03 | 2 | 3 |
| `django-js-asset` | 1.2.2 | 🟢 thriving | no | 1 | 2026-10-26 | 2026-11-16 | 2 | 1 |
| `django-mptt` | 0.11.0 | 🟢 thriving | yes | 0 | 2026-11-03 | 2026-11-03 | 2 | 5 |
| `django-phonenumber-field` | 5.0.0 | 🟢 thriving | yes | 0 | 2026-10-21 | 2026-10-30 | 5 | 6 |
| `django-stubs` | 1.2.0 | 🟢 thriving | dev | ? | 2026-10-05 | 2026-11-16 | 3 | 6 |
| `faker` | 4.14.0 | 🟢 thriving | yes | 0 | 2026-11-10 | 2026-11-10 | 2 | 23 |
| `filelock` | 3.0.12 | 🟢 thriving | dev | ? | 2026-11-09 | 2026-11-17 | 2 | 19 |
| `flake8` | 3.8.4 | 🟢 thriving | dev | ? | 2026-10-28 | 2026-11-04 | 2 | 2 |
| `gitpython` | 3.1.11 | 🟢 thriving | dev | ? | 2026-10-14 | 2026-11-16 | 2 | 8 |
| `google-api-core` | 1.23.0 | 🟢 thriving | no | 1 | 2026-11-05 | 2026-11-17 | 2 | 25 |
| `google-auth` | 1.22.1 | 🟢 thriving | no | 1 | 2026-11-10 | 2026-11-17 | 2 | 25 |
| `google-cloud-core` | 1.4.3 | 🟢 thriving | no | 1 | 2026-09-29 | 2026-11-17 | 2 | 25 |
| `google-cloud-pubsub` | 2.1.0 | 🟢 thriving | yes | 0 | 2026-11-12 | 2026-11-17 | 2 | 25 |
| `google-cloud-storage` | 1.32.0 | 🟢 thriving | yes | 0 | 2026-10-15 | 2026-11-17 | 2 | 25 |
| `google-resumable-media` | 1.1.0 | 🟢 thriving | no | 1 | 2026-09-29 | 2026-11-17 | 2 | 25 |
| `googleapis-common-protos` | 1.52.0 | 🟢 thriving | no | 2 | 2026-10-22 | 2026-11-17 | 2 | 25 |
| `graphql-core` | 2.3.2 | 🟢 thriving | no | 1 | 2026-11-06 | 2026-11-15 | 3 | 6 |
| `grpc-google-iam-v1` | 0.12.3 | 🟢 thriving | no | 1 | 2026-10-22 | 2026-11-17 | 2 | 25 |
| `grpcio` | 1.33.2 | 🟢 thriving | no | 2 | 2026-11-09 | 2026-11-17 | 2 | 36 |
| `gunicorn` | 20.0.4 | 🟢 thriving | yes | 0 | 2026-11-12 | 2026-11-12 | 2 | 10 |
| `httptools` | 0.1.1 | 🟢 thriving | no | 1 | 2026-10-09 | 2026-10-09 | 3 | 11 |
| `identify` | 1.5.6 | 🟢 thriving | dev | ? | 2026-09-26 | 2026-11-04 | 2 | 15 |
| `idna` | 2.10 | 🟢 thriving | no | 1 | 2026-09-17 | 2026-10-31 | 1 | 3 |
| `isort` | 4.3.21 | 🟢 thriving | dev | ? | 2026-11-15 | 2026-11-16 | 3 | 28 |
| `kombu` | 5.0.2 | 🟢 thriving | no | 1 | 2026-11-03 | 2026-11-16 | 5 | 28 |
| `lxml` | 4.6.1 | 🟢 thriving | no | 1 | 2026-09-03 | 2026-11-15 | 2 | 8 |
| `markdown` | 3.3.3 | 🟢 thriving | yes | 0 | 2026-11-05 | 2026-11-16 | 3 | 21 |
| `maxminddb` | 2.0.3 | 🟢 thriving | yes | 0 | 2026-09-10 | 2026-11-16 | ? | 2 |
| `mpmath` | 1.1.0 | 🟢 thriving | no | 3 | 2026-10-30 | 2026-11-16 | 1 | 14 |
| `multidict` | 5.0.0 | 🟢 thriving | dev | ? | 2026-10-24 | 2026-11-09 | 2 | 3 |
| `mypy` | 0.740 | 🟢 thriving | dev | ? | 2026-10-28 | 2026-11-16 | 12 | 10 |
| `nodeenv` | 1.5.0 | 🟢 thriving | dev | ? | 2026-10-31 | 2026-11-02 | 1 | 10 |
| `oauthlib` | 3.1.0 | 🟢 thriving | yes | 0 | 2026-10-31 | 2026-10-31 | 2 | 14 |
| `packaging` | 20.4 | 🟢 thriving | dev | ? | 2026-08-04 | 2026-11-17 | 4 | 28 |
| `pathspec` | 0.8.0 | 🟢 thriving | dev | ? | 2026-04-27 | 2026-11-11 | 1 | 19 |
| `petl` | 1.6.7 | 🟢 thriving | yes | 0 | 2026-11-10 | 2026-11-17 | 2 | 32 |
| `pillow` | 8.0.1 | 🟢 thriving | no | 1 | 2026-10-16 | 2026-11-16 | 4 | 21 |
| `pre-commit` | 2.8.1 | 🟢 thriving | dev | ? | 2026-10-12 | 2026-11-09 | 1 | 4 |
| `proto-plus` | 1.11.0 | 🟢 thriving | no | 1 | 2026-09-29 | 2026-11-17 | 2 | 25 |
| `psycopg2-binary` | 2.8.6 | 🟢 thriving | yes | 0 | 2026-09-10 | 2026-11-01 | 1 | 3 |
| `pyasn1` | 0.4.8 | 🟢 thriving | no | 3 | 2026-10-27 | 2026-10-27 | 4 | 2 |
| `pycparser` | 2.20 | 🟢 thriving | no | 2 | 2026-10-22 | 2026-11-12 | 1 | 12 |
| `pyflakes` | 2.2.0 | 🟢 thriving | dev | ? | 2026-10-28 | 2026-10-28 | 3 | 1 |
| `pyjwt` | 1.7.1 | 🟢 thriving | yes | 0 | 2026-09-28 | 2026-11-16 | 1 | 15 |
| `pylint` | 2.6.0 | 🟢 thriving | dev | ? | 2026-11-14 | 2026-11-17 | 8 | 28 |
| `pylint-django` | 2.3.0 | 🟢 thriving | dev | ? | 2026-07-11 | 2026-11-16 | 2 | 4 |
| `pyparsing` | 2.4.7 | 🟢 thriving | dev | ? | 2026-09-20 | 2026-10-18 | 1 | 15 |
| `pyphen` | 0.9.5 | 🟢 thriving | no | 1 | 2026-08-14 | 2026-11-09 | 2 | 5 |
| `pytest` | 6.1.2 | 🟢 thriving | dev | ? | 2026-10-27 | 2026-11-17 | 7 | 18 |
| `pytest-django` | 3.10.0 | 🟢 thriving | dev | ? | 2026-08-10 | 2026-11-01 | 4 | 12 |
| `pytest-django-queries` | 1.1.0 | 🟢 thriving | dev | ? | 2026-03-01 | 2026-10-29 | 1 | 1 |
| `pytest-mock` | 3.3.1 | 🟢 thriving | dev | ? | 2026-10-17 | 2026-11-17 | 6 | 15 |
| `python-dateutil` | 2.8.1 | 🟢 thriving | no | 1 | 2026-11-01 | 2026-11-01 | 4 | 7 |
| `python-dotenv` | 0.15.0 | 🟢 thriving | no | 1 | 2026-10-01 | 2026-11-09 | 2 | 21 |
| `python-json-logger` | 2.0.1 | 🟢 thriving | yes | 0 | 2026-08-15 | 2026-10-31 | 1 | 13 |
| `python-slugify` | 4.0.1 | 🟢 thriving | dev | ? | 2026-11-16 | 2026-11-16 | 1 | 13 |
| `pytimeparse` | 1.1.8 | 🟢 thriving | yes | 0 | 2026-10-17 | 2026-10-17 | 1 | 9 |
| `pytz` | 2020.1 | 🟢 thriving | no | 1 | 2026-10-29 | 2026-10-29 | 1 | 7 |
| `redis` | 3.5.3 | 🟢 thriving | no | 1 | 2026-11-04 | 2026-11-16 | 3 | 40 |
| `regex` | 2020.10.28 | 🟢 thriving | dev | ? | 2026-11-15 | 2026-11-15 | 1 | 4 |
| `requests` | 2.24.0 | 🟢 thriving | yes | 0 | 2026-05-14 | 2026-11-02 | 3 | 23 |
| `s3transfer` | 0.3.3 | 🟢 thriving | no | 1 | 2026-10-19 | 2026-11-05 | 1 | 12 |
| `sentry-sdk` | 0.19.1 | 🟢 thriving | yes | 0 | 2026-11-12 | 2026-11-17 | 1 | 14 |
| `snowballstemmer` | 2.0.0 | 🟢 thriving | dev | ? | 2026-06-03 | 2026-11-10 | 2 | 2 |
| `soupsieve` | 2.0.1 | 🟢 thriving | no | 2 | 2026-11-14 | 2026-11-15 | 1 | 11 |
| `sqlparse` | 0.4.1 | 🟢 thriving | no | 1 | 2026-11-01 | 2026-11-01 | 1 | 15 |
| `stripe` | 2.55.0 | 🟢 thriving | yes | 0 | 2026-11-11 | 2026-11-16 | 1 | 9 |
| `sympy` | 1.6.2 | 🟢 thriving | no | 2 | 2026-11-15 | 2026-11-17 | 3 | 15 |
| `tinycss2` | 1.0.2 | 🟢 thriving | no | 1 | 2025-11-23 | 2026-10-25 | 2 | 5 |
| `tornado` | 6.0.4 | 🟢 thriving | no | 1 | 2026-11-09 | 2026-11-17 | 2 | 9 |
| `tox` | 3.20.1 | 🟢 thriving | dev | ? | 2026-11-06 | 2026-11-16 | ? | 18 |
| `tqdm` | 4.51.0 | 🟢 thriving | yes | 0 | 2026-09-11 | 2026-11-02 | 2 | 23 |
| `typing-extensions` | 3.7.4.3 | 🟢 thriving | no | 2 | 2026-07-02 | 2026-11-16 | 6 | 17 |
| `urllib3` | 1.25.11 | 🟢 thriving | no | 1 | 2026-09-15 | 2026-11-14 | 3 | 38 |
| `uvicorn` | 0.12.2 | 🟢 thriving | yes | 0 | 2026-09-25 | 2026-11-01 | 1 | 16 |
| `vcrpy` | 4.1.1 | 🟢 thriving | dev | ? | 2026-11-02 | 2026-11-10 | 6 | 5 |
| `virtualenv` | 20.1.0 | 🟢 thriving | dev | ? | 2026-11-17 | 2026-11-17 | 2 | 17 |
| `wcwidth` | 0.2.5 | 🟢 thriving | no | 3 | 2026-10-24 | 2026-11-13 | 1 | 3 |
| `weasyprint` | 51 | 🟢 thriving | yes | 0 | 2026-09-08 | 2026-11-13 | 2 | 7 |
| `webencodings` | 0.5.1 | 🟢 thriving | no | 2 | 2026-08-15 | 2026-10-25 | 2 | 1 |
| `websockets` | 8.1 | 🟢 thriving | no | 1 | 2026-10-30 | 2026-11-14 | 1 | 5 |
| `wrapt` | 1.12.1 | 🟢 thriving | dev | ? | 2026-10-29 | 2026-11-08 | 1 | 6 |
| `yarl` | 1.6.2 | 🟢 thriving | dev | ? | 2026-09-15 | 2026-11-16 | 2 | 6 |
| `aniso8601` | 7.0.0 | 🟡 coasting | no | 2 | 2025-04-18 | — | 1 | ? |
| `attrs` | 20.2.0 | 🟡 coasting | dev | ? | 2026-03-19 | 2026-11-14 | ? | 17 |
| `babel` | 2.8.0 | 🟡 coasting | yes | 0 | 2026-02-01 | 2026-11-16 | 5 | 33 |
| `beautifulsoup4` | 4.7.1 | 🟡 coasting | no | 1 | 2026-06-07 | — | 1 | ? |
| `braintree` | 4.4.0 | 🟡 coasting | yes | 0 | 2026-10-19 | — | 1 | ? |
| `cfgv` | 3.2.0 | 🟡 coasting | dev | ? | 2025-11-19 | 2026-11-04 | 1 | 1 |
| `dj-database-url` | 0.5.0 | 🟡 coasting | yes | 0 | 2026-02-19 | — | 2 | ? |
| `django-appconf` | 1.0.4 | 🟡 coasting | no | 1 | 2025-11-08 | 2026-01-01 | 3 | 1 |
| `django-cache-url` | 3.1.2 | 🟡 coasting | yes | 0 | 2026-01-24 | 2026-01-24 | 1 | 2 |
| `django-extensions` | 3.0.9 | 🟡 coasting | dev | ? | 2025-04-11 | 2026-08-31 | 1 | 9 |
| `django-prices` | 2.2.0 | 🟡 coasting | yes | 0 | 2025-10-29 | 2026-01-14 | 4 | 1 |
| `django-prices-openexchangerates` | 1.1.0 | 🟡 coasting | yes | 0 | 2025-10-30 | 2025-10-30 | 4 | ? |
| `django-prices-vatlayer` | 1.1.0 | 🟡 coasting | yes | 0 | 2025-10-30 | 2025-10-29 | 1 | ? |
| `django-redis` | 4.12.1 | 🟡 coasting | yes | 0 | 2026-06-02 | 2026-11-16 | 3 | 9 |
| `django-render-block` | 0.8.1 | 🟡 coasting | no | 1 | 2025-05-13 | 2025-06-10 | 1 | ? |
| `django-storages` | 1.10.1 | 🟡 coasting | yes | 0 | 2025-04-02 | 2026-08-02 | 1 | 1 |
| `django-templated-email` | 2.3.0 | 🟡 coasting | yes | 0 | 2025-08-21 | 2025-09-29 | 3 | ? |
| `execnet` | 1.7.1 | 🟡 coasting | dev | ? | 2025-11-12 | — | 3 | ? |
| `freezegun` | 0.3.15 | 🟡 coasting | yes | 0 | 2025-08-09 | 2025-08-19 | 2 | ? |
| `graphene-django` | 2.13.0 | 🟡 coasting | yes | 0 | 2025-03-13 | 2026-06-24 | 3 | 1 |
| `graphene-federation` | 0.1.0 | 🟡 coasting | yes | 0 | 2025-10-09 | 2025-10-09 | 4 | ? |
| `h11` | 0.11.0 | 🟡 coasting | no | 1 | 2025-04-24 | 2025-04-24 | 2 | ? |
| `iniconfig` | 1.1.1 | 🟡 coasting | dev | ? | 2026-10-06 | 2026-11-16 | 2 | 6 |
| `jinja2` | 2.11.2 | 🟡 coasting | dev | ? | 2025-03-05 | 2025-06-14 | ? | ? |
| `jmespath` | 0.10.0 | 🟡 coasting | no | 1 | 2026-01-22 | 2026-04-20 | 2 | 3 |
| `lazy-object-proxy` | 1.4.3 | 🟡 coasting | dev | ? | 2026-10-20 | 2026-10-17 | 1 | 6 |
| `libcst` | 0.3.13 | 🟡 coasting | no | 1 | 2026-08-11 | 2026-08-11 | 4 | 8 |
| `markupsafe` | 1.1.1 | 🟡 coasting | dev | ? | 2026-10-02 | 2026-10-03 | ? | 5 |
| `mypy-extensions` | 0.4.3 | 🟡 coasting | no | 3 | 2026-11-03 | 2026-11-03 | 5 | 2 |
| `phonenumberslite` | 8.12.11 | 🟡 coasting | yes | 0 | 2026-11-06 | — | 1 | ? |
| `pluggy` | 0.13.1 | 🟡 coasting | dev | ? | 2026-10-15 | 2026-11-17 | 6 | 11 |
| `prompt-toolkit` | 3.0.8 | 🟡 coasting | no | 2 | 2026-07-26 | 2026-10-20 | 1 | 13 |
| `protobuf` | 3.13.0 | 🟡 coasting | no | 2 | 2026-11-13 | — | 1 | ? |
| `pyasn1-modules` | 0.2.8 | 🟡 coasting | no | 2 | 2025-03-28 | 2025-05-09 | 4 | ? |
| `pycodestyle` | 2.6.0 | 🟡 coasting | dev | ? | 2026-09-22 | — | 2 | ? |
| `pylint-plugin-utils` | 0.6 | 🟡 coasting | dev | ? | 2025-06-24 | 2026-11-16 | 1 | 1 |
| `pytest-celery` | 0.0.0a1 | 🟡 coasting | dev | ? | 2026-03-02 | 2026-11-16 | 3 | 3 |
| `pytest-cov` | 2.10.1 | 🟡 coasting | dev | ? | 2026-03-21 | 2026-10-18 | 1 | 10 |
| `pytest-xdist` | 1.34.0 | 🟡 coasting | dev | ? | 2025-07-01 | 2026-11-17 | 6 | 11 |
| `pywatchman` | 1.4.1 | 🟡 coasting | dev | ? | 2026-06-12 | 2026-11-17 | 1 | 22 |
| `pyyaml` | 5.3.1 | 🟡 coasting | no | 1 | 2025-09-29 | 2026-10-07 | 3 | 2 |
| `razorpay` | 1.2.0 | 🟡 coasting | yes | 0 | 2026-03-09 | 2026-10-30 | 2 | 1 |
| `singledispatch` | 3.4.0.3 | 🟡 coasting | no | 1 | 2025-05-14 | 2026-10-17 | 2 | 4 |
| `six` | 1.15.0 | 🟡 coasting | no | 1 | 2024-12-04 | 2026-02-23 | 1 | 2 |
| `thrift` | 0.13.0 | 🟡 coasting | no | 1 | 2026-09-30 | — | 3 | ? |
| `unidecode` | 1.1.1 | 🟡 coasting | no | 1 | 2025-04-24 | — | 2 | ? |
| `uvloop` | 0.14.0 | 🟡 coasting | no | 1 | 2026-10-01 | 2026-10-19 | 4 | 13 |
| `apipkg` | 1.5 | 🟠 dormant | dev | ? | 2023-09-19 | 2026-11-09 | 2 | 3 |
| `cairocffi` | 1.1.0 | 🟠 dormant | no | 1 | 2024-06-18 | 2026-08-28 | 2 | 2 |
| `click-didyoumean` | 0.0.3 | 🟠 dormant | no | 1 | 2024-03-24 | 2024-03-27 | 2 | ? |
| `colorama` | 0.4.4 | 🟠 dormant | no | 1 | 2022-10-25 | 2026-05-13 | 2 | 2 |
| `defusedxml` | 0.6.0 | 🟠 dormant | no | 2 | 2023-09-29 | 2024-09-03 | 1 | ? |
| `django-versatileimagefield` | 2.0 | 🟠 dormant | yes | 0 | 2024-01-21 | 2024-01-21 | 1 | ? |
| `et-xmlfile` | 1.0.1 | 🟠 dormant | no | 1 | 2024-10-25 | — | 1 | ? |
| `google-i18n-address` | 2.4.0 | 🟠 dormant | yes | 0 | 2024-09-04 | 2026-04-16 | 4 | ? |
| `graphene` | 2.1.8 | 🟠 dormant | no | 1 | 2024-11-09 | 2025-09-04 | 3 | ? |
| `mccabe` | 0.6.1 | 🟠 dormant | dev | ? | 2022-01-24 | 2026-10-12 | 1 | 3 |
| `measurement` | 3.2.0 | 🟠 dormant | no | 1 | 2023-01-10 | — | 3 | ? |
| `openpyxl` | 3.0.5 | 🟠 dormant | yes | 0 | 2024-06-28 | — | 2 | ? |
| `python-magic` | 0.4.18 | 🟠 dormant | no | 1 | 2022-06-07 | 2026-10-14 | 1 | 5 |
| `rx` | 1.6.1 | 🟠 dormant | no | 2 | 2022-12-17 | — | 2 | ? |
| `threadloop` | 1.0.2 | 🟠 dormant | no | 1 | 2016-04-01 | 2026-09-08 | 7 | 1 |
| `typing-inspect` | 0.6.0 | 🟠 dormant | no | 2 | 2023-05-24 | 2026-01-18 | 1 | 1 |
| `vine` | 5.0.0 | 🟠 dormant | no | 1 | 2023-11-05 | 2026-11-16 | 3 | 2 |
| `appdirs` | 1.4.4 | 🔴 dead | dev | ? | 2020-05-11 | 2023-02-10 | 1 | ? |
| `atomicwrites` | 1.4.0 | 🔴 dead | dev | ? | 2022-07-09 | 2022-07-08 | 1 | ? |
| `beautifultable` | 0.7.0 | 🔴 dead | dev | ? | 2022-05-06 | 2022-05-13 | 1 | ? |
| `codecov` | 2.1.10 | 🔴 dead | dev | ? | 2023-04-17 | 2025-05-21 | 3 | ? |
| `dj-email-url` | 1.0.1 | 🔴 dead | yes | 0 | 2022-09-24 | 2024-06-10 | 1 | ? |
| `django-debug-toolbar-request-history` | 0.1.3 | 🔴 dead | dev | ? | 2021-10-19 | 2022-09-23 | 1 | ? |
| `django-graphiql-debug-toolbar` | 0.1.4 | 🔴 dead | dev | ? | 2021-08-28 | 2024-07-14 | 1 | ? |
| `django-measurement` | 3.2.3 | 🔴 dead | yes | 0 | 2022-02-28 | 2023-05-10 | 3 | ? |
| `draftjs-sanitizer` | 1.0.0 | 🔴 dead | yes | 0 | 2019-07-18 | 2019-07-18 | 1 | ? |
| `enmerkar` | 0.7.1 | 🔴 dead | no | 1 | 2019-12-02 | 2023-08-16 | 2 | ? |
| `gitdb` | 4.0.5 | 🔴 dead | dev | ? | 2025-01-02 | 2026-07-26 | 2 | 3 |
| `google-crc32c` | 1.0.0 | 🔴 dead | no | 2 | 2026-09-24 | 2026-04-01 | 2 | 3 |
| `google-measurement-protocol` | 1.1.0 | 🔴 dead | yes | 0 | 2020-09-04 | — | 3 | ? |
| `graphql-relay` | 2.0.1 | 🔴 dead | no | 2 | 2022-04-16 | 2023-02-27 | 3 | ? |
| `html-to-draftjs` | 1.0.1 | 🔴 dead | yes | 0 | 2019-07-31 | 2020-10-27 | 1 | ? |
| `html5lib` | 1.1 | 🔴 dead | no | 1 | 2020-06-22 | 2026-04-21 | 2 | ? |
| `jaeger-client` | 4.3.0 | 🔴 dead | yes | 0 | 2021-09-14 | 2022-07-10 | 2 | ? |
| `jdcal` | 1.4.1 | 🔴 dead | no | 1 | 2019-04-24 | 2022-02-26 | 2 | ? |
| `jsonfield` | 3.1.0 | 🔴 dead | no | 1 | 2025-07-04 | 2025-07-04 | 2 | ? |
| `maxminddb-geolite2` | 2018.703 | 🔴 dead | yes | 0 | 2018-07-18 | 2018-07-30 | 1 | ? |
| `opentracing` | 2.3.0 | 🔴 dead | yes | 0 | 2020-11-19 | 2022-07-01 | 3 | ? |
| `prices` | 1.1.0 | 🔴 dead | yes | 0 | 2022-10-07 | 2025-10-30 | 4 | ? |
| `promise` | 2.3 | 🔴 dead | no | 1 | 2019-12-18 | 2024-07-09 | 2 | ? |
| `purl` | 1.5 | 🔴 dead | yes | 0 | 2021-05-15 | 2023-08-04 | 1 | ? |
| `py` | 1.9.0 | 🔴 dead | dev | ? | 2021-11-04 | — | 6 | ? |
| `pydocstyle` | 5.1.1 | 🔴 dead | dev | ? | 2023-01-17 | 2023-11-03 | 2 | ? |
| `pylint-celery` | 0.3 | 🔴 dead | dev | ? | 2014-09-25 | 2022-11-12 | 1 | ? |
| `pytest-forked` | 1.3.0 | 🔴 dead | dev | ? | 2026-08-08 | 2026-08-08 | 2 | 6 |
| `pytest-vcr` | 1.0.2 | 🔴 dead | dev | ? | 2019-04-26 | 2022-05-07 | 1 | ? |
| `python-magic-bin` | 0.4.14 | 🔴 dead | yes | 0 | 2017-10-02 | 2026-09-18 | 1 | 1 |
| `rsa` | 4.6 | 🔴 dead | no | 2 | 2025-04-16 | 2025-04-16 | 1 | ? |
| `smmap` | 3.0.4 | 🔴 dead | dev | ? | 2026-03-09 | 2026-07-26 | 1 | 3 |
| `text-unidecode` | 1.3 | 🔴 dead | yes | 0 | 2019-08-30 | 2023-03-16 | 1 | ? |
| `toml` | 0.10.1 | 🔴 dead | dev | ? | 2020-11-01 | 2024-06-26 | 1 | ? |
| `transifex-client` | 0.14.1 | 🔴 dead | dev | ? | 2021-12-24 | — | 1 | ? |
| `typed-ast` | 1.4.1 | 🔴 dead | dev | ? | 2023-07-04 | 2023-07-03 | 6 | ? |
| `watchgod` | 0.6 | 🔴 dead | no | 1 | 2022-04-01 | 2026-11-01 | 1 | 8 |

## What this report does not know

- `adyen`: usage: pypistats did not answer (download counts unknown)
- `adyen`: usage: GitHub code search did not answer
- `adyen`: usage: no download or dependent counts available
- `adyen`: commits: 1 bot account(s) excluded from bus-factor counting
- `amqp`: usage: pypistats did not answer (download counts unknown)
- `amqp`: usage: GitHub code search did not answer
- `amqp`: usage: no download or dependent counts available
- `amqp`: commits: 1 bot account(s) excluded from bus-factor counting
- `asgiref`: usage: pypistats did not answer (download counts unknown)
- `asgiref`: usage: GitHub code search did not answer
- `asgiref`: usage: no download or dependent counts available
- `astroid`: usage: pypistats did not answer (download counts unknown)
- `astroid`: usage: GitHub code search did not answer
- `astroid`: usage: no download or dependent counts available
- `astroid`: commits: 3 bot account(s) excluded from bus-factor counting
- `billiard`: usage: pypistats did not answer (download counts unknown)
- `billiard`: usage: GitHub code search did not answer
- `billiard`: usage: no download or dependent counts available
- `billiard`: commits: 2 bot account(s) excluded from bus-factor counting
- `black`: usage: pypistats did not answer (download counts unknown)
- `black`: usage: GitHub code search did not answer
- `black`: usage: no download or dependent counts available
- `black`: commits: 1 bot account(s) excluded from bus-factor counting
- `boto3`: usage: pypistats did not answer (download counts unknown)
- `boto3`: usage: GitHub code search did not answer
- `boto3`: usage: no download or dependent counts available
- `boto3`: commits: 1 bot account(s) excluded from bus-factor counting
- `botocore`: usage: pypistats did not answer (download counts unknown)
- `botocore`: usage: GitHub code search did not answer
- `botocore`: usage: no download or dependent counts available
- `botocore`: commits: 1 bot account(s) excluded from bus-factor counting
- `cachetools`: usage: pypistats did not answer (download counts unknown)
- `cachetools`: usage: GitHub code search did not answer
- `cachetools`: usage: no download or dependent counts available
- `cachetools`: commits: 1 bot account(s) excluded from bus-factor counting
- `cairosvg`: usage: pypistats did not answer (download counts unknown)
- `cairosvg`: usage: GitHub code search did not answer
- `cairosvg`: usage: no download or dependent counts available
- `celery`: usage: pypistats did not answer (download counts unknown)
- `celery`: usage: GitHub code search did not answer
- `celery`: usage: no download or dependent counts available
- `celery`: commits: 1 bot account(s) excluded from bus-factor counting
- `certifi`: usage: pypistats did not answer (download counts unknown)
- `certifi`: usage: GitHub code search did not answer
- `certifi`: usage: no download or dependent counts available
- `certifi`: commits: 2 bot account(s) excluded from bus-factor counting
- `cffi`: usage: pypistats did not answer (download counts unknown)
- `cffi`: usage: GitHub code search did not answer
- `cffi`: usage: no download or dependent counts available
- `cffi`: commits: 1 bot account(s) excluded from bus-factor counting
- `chardet`: usage: pypistats did not answer (download counts unknown)
- `chardet`: usage: GitHub code search did not answer
- `chardet`: usage: no download or dependent counts available
- `click`: registry: no ownership roles published
- `click`: usage: pypistats did not answer (download counts unknown)
- `click`: usage: GitHub code search did not answer
- `click`: usage: no download or dependent counts available
- `click-repl`: usage: pypistats did not answer (download counts unknown)
- `click-repl`: usage: GitHub code search did not answer
- `click-repl`: usage: no download or dependent counts available
- `coverage`: usage: pypistats did not answer (download counts unknown)
- `coverage`: usage: GitHub code search did not answer
- `coverage`: usage: no download or dependent counts available
- `coverage`: commits: 1 bot account(s) excluded from bus-factor counting
- `cssselect2`: usage: pypistats did not answer (download counts unknown)
- `cssselect2`: usage: GitHub code search did not answer
- `cssselect2`: usage: no download or dependent counts available
- `distlib`: usage: pypistats did not answer (download counts unknown)
- `distlib`: usage: GitHub code search did not answer
- `distlib`: usage: no download or dependent counts available
- `django`: registry: no ownership roles published
- `django`: usage: pypistats did not answer (download counts unknown)
- `django`: usage: GitHub code search did not answer
- `django`: usage: no download or dependent counts available
- `django-countries`: usage: pypistats did not answer (download counts unknown)
- `django-countries`: usage: GitHub code search did not answer
- `django-countries`: usage: no download or dependent counts available
- `django-debug-toolbar`: usage: pypistats did not answer (download counts unknown)
- `django-debug-toolbar`: usage: GitHub code search did not answer
- `django-debug-toolbar`: usage: no download or dependent counts available
- `django-debug-toolbar`: commits: 2 bot account(s) excluded from bus-factor counting
- `django-filter`: usage: pypistats did not answer (download counts unknown)
- `django-filter`: usage: GitHub code search did not answer
- `django-filter`: usage: no download or dependent counts available
- `django-js-asset`: usage: pypistats did not answer (download counts unknown)
- `django-js-asset`: usage: GitHub code search did not answer
- `django-js-asset`: usage: no download or dependent counts available
- `django-js-asset`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-mptt`: usage: pypistats did not answer (download counts unknown)
- `django-mptt`: usage: GitHub code search did not answer
- `django-mptt`: usage: no download or dependent counts available
- `django-phonenumber-field`: usage: pypistats did not answer (download counts unknown)
- `django-phonenumber-field`: usage: GitHub code search did not answer
- `django-phonenumber-field`: usage: no download or dependent counts available
- `django-phonenumber-field`: commits: 1 bot account(s) excluded from bus-factor counting
- `django-stubs`: usage: pypistats did not answer (download counts unknown)
- `django-stubs`: usage: GitHub code search did not answer
- `django-stubs`: usage: no download or dependent counts available
- `django-stubs`: commits: 2 bot account(s) excluded from bus-factor counting
- `faker`: usage: pypistats did not answer (download counts unknown)
- `faker`: usage: GitHub code search did not answer
- `faker`: usage: no download or dependent counts available
- `faker`: commits: 1 bot account(s) excluded from bus-factor counting
- `filelock`: usage: pypistats did not answer (download counts unknown)
- `filelock`: usage: GitHub code search did not answer
- `filelock`: usage: no download or dependent counts available
- `filelock`: commits: 3 bot account(s) excluded from bus-factor counting
- `flake8`: usage: pypistats did not answer (download counts unknown)
- `flake8`: usage: GitHub code search did not answer
- `flake8`: usage: no download or dependent counts available
- `flake8`: commits: 1 bot account(s) excluded from bus-factor counting
- `gitpython`: usage: pypistats did not answer (download counts unknown)
- `gitpython`: usage: GitHub code search did not answer
- `gitpython`: usage: no download or dependent counts available
- `gitpython`: commits: 1 bot account(s) excluded from bus-factor counting
- `google-api-core`: usage: pypistats did not answer (download counts unknown)
- `google-api-core`: usage: GitHub code search did not answer
- `google-api-core`: usage: no download or dependent counts available
- `google-api-core`: commits: 3 bot account(s) excluded from bus-factor counting
- `google-auth`: usage: pypistats did not answer (download counts unknown)
- `google-auth`: usage: GitHub code search did not answer
- `google-auth`: usage: no download or dependent counts available
- `google-auth`: commits: 3 bot account(s) excluded from bus-factor counting
- `google-cloud-core`: usage: pypistats did not answer (download counts unknown)
- `google-cloud-core`: usage: GitHub code search did not answer
- `google-cloud-core`: usage: no download or dependent counts available
- `google-cloud-core`: commits: 3 bot account(s) excluded from bus-factor counting
- `google-cloud-pubsub`: usage: pypistats did not answer (download counts unknown)
- `google-cloud-pubsub`: usage: GitHub code search did not answer
- `google-cloud-pubsub`: usage: no download or dependent counts available
- `google-cloud-pubsub`: commits: 3 bot account(s) excluded from bus-factor counting
- `google-cloud-storage`: usage: pypistats did not answer (download counts unknown)
- `google-cloud-storage`: usage: GitHub code search did not answer
- `google-cloud-storage`: usage: no download or dependent counts available
- `google-cloud-storage`: commits: 3 bot account(s) excluded from bus-factor counting
- `google-resumable-media`: usage: pypistats did not answer (download counts unknown)
- `google-resumable-media`: usage: GitHub code search did not answer
- `google-resumable-media`: usage: no download or dependent counts available
- `google-resumable-media`: commits: 3 bot account(s) excluded from bus-factor counting
- `googleapis-common-protos`: usage: pypistats did not answer (download counts unknown)
- `googleapis-common-protos`: usage: GitHub code search did not answer
- `googleapis-common-protos`: usage: no download or dependent counts available
- `googleapis-common-protos`: commits: 3 bot account(s) excluded from bus-factor counting
- `graphql-core`: usage: pypistats did not answer (download counts unknown)
- `graphql-core`: usage: GitHub code search did not answer
- `graphql-core`: usage: no download or dependent counts available
- `grpc-google-iam-v1`: usage: pypistats did not answer (download counts unknown)
- `grpc-google-iam-v1`: usage: GitHub code search did not answer
- `grpc-google-iam-v1`: usage: no download or dependent counts available
- `grpc-google-iam-v1`: commits: 3 bot account(s) excluded from bus-factor counting
- `grpcio`: usage: pypistats did not answer (download counts unknown)
- `grpcio`: usage: GitHub code search did not answer
- `grpcio`: usage: no download or dependent counts available
- `grpcio`: commits: 1 bot account(s) excluded from bus-factor counting
- `gunicorn`: usage: pypistats did not answer (download counts unknown)
- `gunicorn`: usage: GitHub code search did not answer
- `gunicorn`: usage: no download or dependent counts available
- `httptools`: usage: pypistats did not answer (download counts unknown)
- `httptools`: usage: GitHub code search did not answer
- `httptools`: usage: no download or dependent counts available
- `identify`: usage: pypistats did not answer (download counts unknown)
- `identify`: usage: GitHub code search did not answer
- `identify`: usage: no download or dependent counts available
- `identify`: commits: 1 bot account(s) excluded from bus-factor counting
- `idna`: usage: pypistats did not answer (download counts unknown)
- `idna`: usage: GitHub code search did not answer
- `idna`: usage: no download or dependent counts available
- `idna`: commits: 1 bot account(s) excluded from bus-factor counting
- `isort`: usage: pypistats did not answer (download counts unknown)
- `isort`: usage: GitHub code search did not answer
- `isort`: usage: no download or dependent counts available
- `isort`: commits: 1 bot account(s) excluded from bus-factor counting
- `kombu`: usage: pypistats did not answer (download counts unknown)
- `kombu`: usage: GitHub code search did not answer
- `kombu`: usage: no download or dependent counts available
- `kombu`: commits: 2 bot account(s) excluded from bus-factor counting
- `lxml`: usage: pypistats did not answer (download counts unknown)
- `lxml`: usage: GitHub code search did not answer
- `lxml`: usage: no download or dependent counts available
- `lxml`: commits: 1 bot account(s) excluded from bus-factor counting
- `markdown`: usage: pypistats did not answer (download counts unknown)
- `markdown`: usage: GitHub code search did not answer
- `markdown`: usage: no download or dependent counts available
- `maxminddb`: registry: no ownership roles published
- `maxminddb`: usage: pypistats did not answer (download counts unknown)
- `maxminddb`: usage: GitHub code search did not answer
- `maxminddb`: usage: no download or dependent counts available
- `maxminddb`: commits: 1 bot account(s) excluded from bus-factor counting
- `mpmath`: usage: pypistats did not answer (download counts unknown)
- `mpmath`: usage: GitHub code search did not answer
- `mpmath`: usage: no download or dependent counts available
- `mpmath`: commits: 1 bot account(s) excluded from bus-factor counting
- `multidict`: usage: pypistats did not answer (download counts unknown)
- `multidict`: usage: GitHub code search did not answer
- `multidict`: usage: no download or dependent counts available
- `multidict`: commits: 1 bot account(s) excluded from bus-factor counting
- `mypy`: usage: pypistats did not answer (download counts unknown)
- `mypy`: usage: GitHub code search did not answer
- `mypy`: usage: no download or dependent counts available
- `nodeenv`: usage: pypistats did not answer (download counts unknown)
- `nodeenv`: usage: GitHub code search did not answer
- `nodeenv`: usage: no download or dependent counts available
- `nodeenv`: commits: 1 bot account(s) excluded from bus-factor counting
- `oauthlib`: usage: pypistats did not answer (download counts unknown)
- `oauthlib`: usage: GitHub code search did not answer
- `oauthlib`: usage: no download or dependent counts available
- `packaging`: usage: pypistats did not answer (download counts unknown)
- `packaging`: usage: GitHub code search did not answer
- `packaging`: usage: no download or dependent counts available
- `packaging`: commits: 1 bot account(s) excluded from bus-factor counting
- `pathspec`: usage: pypistats did not answer (download counts unknown)
- `pathspec`: usage: GitHub code search did not answer
- `pathspec`: usage: no download or dependent counts available
- `petl`: usage: pypistats did not answer (download counts unknown)
- `petl`: usage: GitHub code search did not answer
- `petl`: usage: no download or dependent counts available
- `petl`: triage: issue search did not answer
- `pillow`: usage: pypistats did not answer (download counts unknown)
- `pillow`: usage: GitHub code search did not answer
- `pillow`: usage: no download or dependent counts available
- `pre-commit`: usage: pypistats did not answer (download counts unknown)
- `pre-commit`: usage: GitHub code search did not answer
- `pre-commit`: usage: no download or dependent counts available
- `pre-commit`: commits: 1 bot account(s) excluded from bus-factor counting
- `pre-commit`: triage: issue search did not answer
- `proto-plus`: usage: pypistats did not answer (download counts unknown)
- `proto-plus`: usage: GitHub code search did not answer
- `proto-plus`: usage: no download or dependent counts available
- `proto-plus`: commits: 3 bot account(s) excluded from bus-factor counting
- `psycopg2-binary`: usage: pypistats did not answer (download counts unknown)
- `psycopg2-binary`: usage: GitHub code search did not answer
- `psycopg2-binary`: usage: no download or dependent counts available
- `psycopg2-binary`: commits: 1 bot account(s) excluded from bus-factor counting
- `pyasn1`: usage: pypistats did not answer (download counts unknown)
- `pyasn1`: usage: GitHub code search did not answer
- `pyasn1`: usage: no download or dependent counts available
- `pyasn1`: triage: issue search did not answer
- `pycparser`: usage: pypistats did not answer (download counts unknown)
- `pycparser`: usage: GitHub code search did not answer
- `pycparser`: usage: no download or dependent counts available
- `pycparser`: triage: issue search did not answer
- `pyflakes`: usage: pypistats did not answer (download counts unknown)
- `pyflakes`: usage: GitHub code search did not answer
- `pyflakes`: usage: no download or dependent counts available
- `pyflakes`: triage: issue search did not answer
- `pyjwt`: usage: pypistats did not answer (download counts unknown)
- `pyjwt`: usage: GitHub code search did not answer
- `pyjwt`: usage: no download or dependent counts available
- `pyjwt`: commits: 2 bot account(s) excluded from bus-factor counting
- `pyjwt`: triage: issue search did not answer
- `pylint`: usage: pypistats did not answer (download counts unknown)
- `pylint`: usage: GitHub code search did not answer
- `pylint`: usage: no download or dependent counts available
- `pylint`: commits: 3 bot account(s) excluded from bus-factor counting
- `pylint`: triage: issue search did not answer
- `pylint-django`: usage: pypistats did not answer (download counts unknown)
- `pylint-django`: usage: GitHub code search did not answer
- `pylint-django`: usage: no download or dependent counts available
- `pylint-django`: commits: 1 bot account(s) excluded from bus-factor counting
- `pylint-django`: triage: issue search did not answer
- `pyparsing`: usage: pypistats did not answer (download counts unknown)
- `pyparsing`: usage: GitHub code search did not answer
- `pyparsing`: usage: no download or dependent counts available
- `pyparsing`: triage: issue search did not answer
- `pyphen`: usage: pypistats did not answer (download counts unknown)
- `pyphen`: usage: GitHub code search did not answer
- `pyphen`: usage: no download or dependent counts available
- `pyphen`: triage: issue search did not answer
- `pytest`: usage: pypistats did not answer (download counts unknown)
- `pytest`: usage: GitHub code search did not answer
- `pytest`: usage: no download or dependent counts available
- `pytest`: commits: 3 bot account(s) excluded from bus-factor counting
- `pytest`: triage: issue search did not answer
- `pytest-django`: usage: pypistats did not answer (download counts unknown)
- `pytest-django`: usage: GitHub code search did not answer
- `pytest-django`: usage: no download or dependent counts available
- `pytest-django`: commits: 1 bot account(s) excluded from bus-factor counting
- `pytest-django`: triage: issue search did not answer
- `pytest-django-queries`: usage: pypistats did not answer (download counts unknown)
- `pytest-django-queries`: usage: GitHub code search did not answer
- `pytest-django-queries`: usage: no download or dependent counts available
- `pytest-django-queries`: commits: 1 bot account(s) excluded from bus-factor counting
- `pytest-django-queries`: triage: issue search did not answer
- `pytest-mock`: usage: pypistats did not answer (download counts unknown)
- `pytest-mock`: usage: GitHub code search did not answer
- `pytest-mock`: usage: no download or dependent counts available
- `pytest-mock`: commits: 3 bot account(s) excluded from bus-factor counting
- `pytest-mock`: triage: issue search did not answer
- `python-dateutil`: usage: pypistats did not answer (download counts unknown)
- `python-dateutil`: usage: GitHub code search did not answer
- `python-dateutil`: usage: no download or dependent counts available
- `python-dateutil`: triage: issue search did not answer
- `python-dotenv`: usage: pypistats did not answer (download counts unknown)
- `python-dotenv`: usage: GitHub code search did not answer
- `python-dotenv`: usage: no download or dependent counts available
- `python-dotenv`: commits: 1 bot account(s) excluded from bus-factor counting
- `python-dotenv`: triage: issue search did not answer
- `python-json-logger`: usage: pypistats did not answer (download counts unknown)
- `python-json-logger`: usage: GitHub code search did not answer
- `python-json-logger`: usage: no download or dependent counts available
- `python-json-logger`: commits: 1 bot account(s) excluded from bus-factor counting
- `python-json-logger`: triage: issue search did not answer
- `python-slugify`: usage: pypistats did not answer (download counts unknown)
- `python-slugify`: usage: GitHub code search did not answer
- `python-slugify`: usage: no download or dependent counts available
- `python-slugify`: triage: issue search did not answer
- `pytimeparse`: usage: pypistats did not answer (download counts unknown)
- `pytimeparse`: usage: GitHub code search did not answer
- `pytimeparse`: usage: no download or dependent counts available
- `pytimeparse`: triage: issue search did not answer
- `pytz`: usage: pypistats did not answer (download counts unknown)
- `pytz`: usage: GitHub code search did not answer
- `pytz`: usage: no download or dependent counts available
- `pytz`: triage: issue search did not answer
- `redis`: usage: pypistats did not answer (download counts unknown)
- `redis`: usage: GitHub code search did not answer
- `redis`: usage: no download or dependent counts available
- `redis`: commits: 1 bot account(s) excluded from bus-factor counting
- `redis`: triage: issue search did not answer
- `regex`: usage: pypistats did not answer (download counts unknown)
- `regex`: usage: GitHub code search did not answer
- `regex`: usage: no download or dependent counts available
- `regex`: triage: issue search did not answer
- `requests`: usage: pypistats did not answer (download counts unknown)
- `requests`: usage: GitHub code search did not answer
- `requests`: usage: no download or dependent counts available
- `requests`: commits: 1 bot account(s) excluded from bus-factor counting
- `requests`: triage: issue search did not answer
- `s3transfer`: usage: pypistats did not answer (download counts unknown)
- `s3transfer`: usage: GitHub code search did not answer
- `s3transfer`: usage: no download or dependent counts available
- `s3transfer`: commits: 1 bot account(s) excluded from bus-factor counting
- `s3transfer`: triage: issue search did not answer
- `sentry-sdk`: usage: pypistats did not answer (download counts unknown)
- `sentry-sdk`: usage: GitHub code search did not answer
- `sentry-sdk`: usage: no download or dependent counts available
- `sentry-sdk`: commits: 5 bot account(s) excluded from bus-factor counting
- `sentry-sdk`: triage: issue search did not answer
- `snowballstemmer`: usage: pypistats did not answer (download counts unknown)
- `snowballstemmer`: usage: GitHub code search did not answer
- `snowballstemmer`: usage: no download or dependent counts available
- `snowballstemmer`: triage: issue search did not answer
- `soupsieve`: usage: pypistats did not answer (download counts unknown)
- `soupsieve`: usage: GitHub code search did not answer
- `soupsieve`: usage: no download or dependent counts available
- `soupsieve`: triage: issue search did not answer
- `sqlparse`: usage: pypistats did not answer (download counts unknown)
- `sqlparse`: usage: GitHub code search did not answer
- `sqlparse`: usage: no download or dependent counts available
- `sqlparse`: triage: issue search did not answer
- `stripe`: usage: pypistats did not answer (download counts unknown)
- `stripe`: usage: GitHub code search did not answer
- `stripe`: usage: no download or dependent counts available
- `stripe`: commits: 1 bot account(s) excluded from bus-factor counting
- `stripe`: triage: issue search did not answer
- `sympy`: usage: pypistats did not answer (download counts unknown)
- `sympy`: usage: GitHub code search did not answer
- `sympy`: usage: no download or dependent counts available
- `sympy`: triage: issue search did not answer
- `tinycss2`: usage: pypistats did not answer (download counts unknown)
- `tinycss2`: usage: GitHub code search did not answer
- `tinycss2`: usage: no download or dependent counts available
- `tinycss2`: triage: issue search did not answer
- `tornado`: usage: pypistats did not answer (download counts unknown)
- `tornado`: usage: GitHub code search did not answer
- `tornado`: usage: no download or dependent counts available
- `tornado`: commits: 1 bot account(s) excluded from bus-factor counting
- `tornado`: triage: issue search did not answer
- `tox`: registry: no ownership roles published
- `tox`: usage: pypistats did not answer (download counts unknown)
- `tox`: usage: GitHub code search did not answer
- `tox`: usage: no download or dependent counts available
- `tox`: commits: 2 bot account(s) excluded from bus-factor counting
- `tox`: triage: issue search did not answer
- `tqdm`: usage: pypistats did not answer (download counts unknown)
- `tqdm`: usage: GitHub code search did not answer
- `tqdm`: usage: no download or dependent counts available
- `tqdm`: triage: issue search did not answer
- `typing-extensions`: usage: pypistats did not answer (download counts unknown)
- `typing-extensions`: usage: GitHub code search did not answer
- `typing-extensions`: usage: no download or dependent counts available
- `typing-extensions`: commits: 3 bot account(s) excluded from bus-factor counting
- `urllib3`: usage: pypistats did not answer (download counts unknown)
- `urllib3`: usage: GitHub code search did not answer
- `urllib3`: usage: no download or dependent counts available
- `urllib3`: commits: 1 bot account(s) excluded from bus-factor counting
- `urllib3`: triage: issue search did not answer
- `uvicorn`: usage: pypistats did not answer (download counts unknown)
- `uvicorn`: usage: GitHub code search did not answer
- `uvicorn`: usage: no download or dependent counts available
- `uvicorn`: commits: 1 bot account(s) excluded from bus-factor counting
- `uvicorn`: triage: issue search did not answer
- `vcrpy`: usage: pypistats did not answer (download counts unknown)
- `vcrpy`: usage: GitHub code search did not answer
- `vcrpy`: usage: no download or dependent counts available
- `vcrpy`: commits: 1 bot account(s) excluded from bus-factor counting
- `vcrpy`: triage: issue search did not answer
- `virtualenv`: usage: pypistats did not answer (download counts unknown)
- `virtualenv`: usage: GitHub code search did not answer
- `virtualenv`: usage: no download or dependent counts available
- `virtualenv`: commits: 2 bot account(s) excluded from bus-factor counting
- `virtualenv`: triage: issue search did not answer
- `wcwidth`: usage: pypistats did not answer (download counts unknown)
- `wcwidth`: usage: GitHub code search did not answer
- `wcwidth`: usage: no download or dependent counts available
- `wcwidth`: commits: 1 bot account(s) excluded from bus-factor counting
- `wcwidth`: triage: issue search did not answer
- `weasyprint`: usage: pypistats did not answer (download counts unknown)
- `weasyprint`: usage: GitHub code search did not answer
- `weasyprint`: usage: no download or dependent counts available
- `weasyprint`: triage: issue search did not answer
- `webencodings`: usage: pypistats did not answer (download counts unknown)
- `webencodings`: usage: GitHub code search did not answer
- `webencodings`: usage: no download or dependent counts available
- `webencodings`: triage: issue search did not answer
- `websockets`: usage: pypistats did not answer (download counts unknown)
- `websockets`: usage: GitHub code search did not answer
- `websockets`: usage: no download or dependent counts available
- `websockets`: commits: 1 bot account(s) excluded from bus-factor counting
- `websockets`: triage: issue search did not answer
- `wrapt`: usage: pypistats did not answer (download counts unknown)
- `wrapt`: usage: GitHub code search did not answer
- `wrapt`: usage: no download or dependent counts available
- `wrapt`: triage: issue search did not answer
- `yarl`: usage: pypistats did not answer (download counts unknown)
- `yarl`: usage: GitHub code search did not answer
- `yarl`: usage: no download or dependent counts available
- `yarl`: commits: 2 bot account(s) excluded from bus-factor counting
- `yarl`: triage: issue search did not answer
- `aniso8601`: usage: pypistats did not answer (download counts unknown)
- `aniso8601`: usage: GitHub code search did not answer
- `aniso8601`: usage: no download or dependent counts available
- `aniso8601`: forge: repository is not on GitHub (https://codeberg.org/nielsenb-jf/aniso8601), so commit and issue history cannot be read
- `attrs`: registry: no ownership roles published
- `attrs`: usage: pypistats did not answer (download counts unknown)
- `attrs`: usage: GitHub code search did not answer
- `attrs`: usage: no download or dependent counts available
- `attrs`: commits: 2 bot account(s) excluded from bus-factor counting
- `babel`: usage: pypistats did not answer (download counts unknown)
- `babel`: usage: GitHub code search did not answer
- `babel`: usage: no download or dependent counts available
- `beautifulsoup4`: usage: pypistats did not answer (download counts unknown)
- `beautifulsoup4`: usage: GitHub code search did not answer
- `beautifulsoup4`: usage: no download or dependent counts available
- `beautifulsoup4`: forge: repository is not on GitHub (https://www.crummy.com/software/BeautifulSoup/bs4/), so commit and issue history cannot be read
- `braintree`: usage: pypistats did not answer (download counts unknown)
- `braintree`: usage: GitHub code search did not answer
- `braintree`: usage: no download or dependent counts available
- `braintree`: forge: repository is not on GitHub (https://developer.paypal.com/braintree/docs/reference/overview), so commit and issue history cannot be read
- `cfgv`: usage: pypistats did not answer (download counts unknown)
- `cfgv`: usage: GitHub code search did not answer
- `cfgv`: usage: no download or dependent counts available
- `cfgv`: commits: 1 bot account(s) excluded from bus-factor counting
- `dj-database-url`: usage: pypistats did not answer (download counts unknown)
- `dj-database-url`: usage: GitHub code search did not answer
- `dj-database-url`: usage: no download or dependent counts available
- `dj-database-url`: forge: repository is not on GitHub (https://jazzband.co/projects/dj-database-url), so commit and issue history cannot be read
- `django-appconf`: usage: pypistats did not answer (download counts unknown)
- `django-appconf`: usage: GitHub code search did not answer
- `django-appconf`: usage: no download or dependent counts available
- `django-cache-url`: usage: pypistats did not answer (download counts unknown)
- `django-cache-url`: usage: GitHub code search did not answer
- `django-cache-url`: usage: no download or dependent counts available
- `django-extensions`: usage: pypistats did not answer (download counts unknown)
- `django-extensions`: usage: GitHub code search did not answer
- `django-extensions`: usage: no download or dependent counts available
- `django-prices`: usage: pypistats did not answer (download counts unknown)
- `django-prices`: usage: GitHub code search did not answer
- `django-prices`: usage: no download or dependent counts available
- `django-prices-openexchangerates`: usage: pypistats did not answer (download counts unknown)
- `django-prices-openexchangerates`: usage: GitHub code search did not answer
- `django-prices-openexchangerates`: usage: no download or dependent counts available
- `django-prices-vatlayer`: usage: pypistats did not answer (download counts unknown)
- `django-prices-vatlayer`: usage: GitHub code search did not answer
- `django-prices-vatlayer`: usage: no download or dependent counts available
- `django-redis`: usage: pypistats did not answer (download counts unknown)
- `django-redis`: usage: GitHub code search did not answer
- `django-redis`: usage: no download or dependent counts available
- `django-redis`: commits: 2 bot account(s) excluded from bus-factor counting
- `django-render-block`: usage: pypistats did not answer (download counts unknown)
- `django-render-block`: usage: GitHub code search did not answer
- `django-render-block`: usage: no download or dependent counts available
- `django-storages`: usage: pypistats did not answer (download counts unknown)
- `django-storages`: usage: GitHub code search did not answer
- `django-storages`: usage: no download or dependent counts available
- `django-templated-email`: usage: pypistats did not answer (download counts unknown)
- `django-templated-email`: usage: GitHub code search did not answer
- `django-templated-email`: usage: no download or dependent counts available
- `execnet`: usage: pypistats did not answer (download counts unknown)
- `execnet`: usage: GitHub code search did not answer
- `execnet`: usage: no download or dependent counts available
- `execnet`: forge: repository is not on GitHub (https://execnet.readthedocs.io/en/latest/), so commit and issue history cannot be read
- `freezegun`: usage: pypistats did not answer (download counts unknown)
- `freezegun`: usage: GitHub code search did not answer
- `freezegun`: usage: no download or dependent counts available
- `graphene-django`: usage: pypistats did not answer (download counts unknown)
- `graphene-django`: usage: GitHub code search did not answer
- `graphene-django`: usage: no download or dependent counts available
- `graphene-federation`: usage: pypistats did not answer (download counts unknown)
- `graphene-federation`: usage: GitHub code search did not answer
- `graphene-federation`: usage: no download or dependent counts available
- `h11`: usage: pypistats did not answer (download counts unknown)
- `h11`: usage: GitHub code search did not answer
- `h11`: usage: no download or dependent counts available
- `iniconfig`: usage: pypistats did not answer (download counts unknown)
- `iniconfig`: usage: GitHub code search did not answer
- `iniconfig`: usage: no download or dependent counts available
- `iniconfig`: commits: 1 bot account(s) excluded from bus-factor counting
- `jinja2`: registry: no ownership roles published
- `jinja2`: usage: pypistats did not answer (download counts unknown)
- `jinja2`: usage: GitHub code search did not answer
- `jinja2`: usage: no download or dependent counts available
- `jmespath`: usage: pypistats did not answer (download counts unknown)
- `jmespath`: usage: GitHub code search did not answer
- `jmespath`: usage: no download or dependent counts available
- `lazy-object-proxy`: usage: pypistats did not answer (download counts unknown)
- `lazy-object-proxy`: usage: GitHub code search did not answer
- `lazy-object-proxy`: usage: no download or dependent counts available
- `libcst`: usage: pypistats did not answer (download counts unknown)
- `libcst`: usage: GitHub code search did not answer
- `libcst`: usage: no download or dependent counts available
- `markupsafe`: registry: no ownership roles published
- `markupsafe`: usage: pypistats did not answer (download counts unknown)
- `markupsafe`: usage: GitHub code search did not answer
- `markupsafe`: usage: no download or dependent counts available
- `mypy-extensions`: usage: pypistats did not answer (download counts unknown)
- `mypy-extensions`: usage: GitHub code search did not answer
- `mypy-extensions`: usage: no download or dependent counts available
- `phonenumberslite`: usage: pypistats did not answer (download counts unknown)
- `phonenumberslite`: usage: GitHub code search did not answer
- `phonenumberslite`: usage: no download or dependent counts available
- `phonenumberslite`: forge: repository is not on GitHub (https://github.com/daviddrysdale/python-phonenumbers), so commit and issue history cannot be read
- `pluggy`: usage: pypistats did not answer (download counts unknown)
- `pluggy`: usage: GitHub code search did not answer
- `pluggy`: usage: no download or dependent counts available
- `pluggy`: commits: 2 bot account(s) excluded from bus-factor counting
- `prompt-toolkit`: usage: pypistats did not answer (download counts unknown)
- `prompt-toolkit`: usage: GitHub code search did not answer
- `prompt-toolkit`: usage: no download or dependent counts available
- `prompt-toolkit`: triage: issue search did not answer
- `protobuf`: usage: pypistats did not answer (download counts unknown)
- `protobuf`: usage: GitHub code search did not answer
- `protobuf`: usage: no download or dependent counts available
- `protobuf`: forge: repository is not on GitHub (https://developers.google.com/protocol-buffers/), so commit and issue history cannot be read
- `pyasn1-modules`: usage: pypistats did not answer (download counts unknown)
- `pyasn1-modules`: usage: GitHub code search did not answer
- `pyasn1-modules`: usage: no download or dependent counts available
- `pyasn1-modules`: triage: issue search did not answer
- `pycodestyle`: usage: pypistats did not answer (download counts unknown)
- `pycodestyle`: usage: GitHub code search did not answer
- `pycodestyle`: usage: no download or dependent counts available
- `pycodestyle`: forge: repository is not on GitHub (https://pycodestyle.pycqa.org/), so commit and issue history cannot be read
- `pylint-plugin-utils`: usage: pypistats did not answer (download counts unknown)
- `pylint-plugin-utils`: usage: GitHub code search did not answer
- `pylint-plugin-utils`: usage: no download or dependent counts available
- `pylint-plugin-utils`: commits: 1 bot account(s) excluded from bus-factor counting
- `pylint-plugin-utils`: triage: issue search did not answer
- `pytest-celery`: usage: pypistats did not answer (download counts unknown)
- `pytest-celery`: usage: GitHub code search did not answer
- `pytest-celery`: usage: no download or dependent counts available
- `pytest-celery`: commits: 2 bot account(s) excluded from bus-factor counting
- `pytest-celery`: triage: issue search did not answer
- `pytest-cov`: usage: pypistats did not answer (download counts unknown)
- `pytest-cov`: usage: GitHub code search did not answer
- `pytest-cov`: usage: no download or dependent counts available
- `pytest-cov`: triage: issue search did not answer
- `pytest-xdist`: usage: pypistats did not answer (download counts unknown)
- `pytest-xdist`: usage: GitHub code search did not answer
- `pytest-xdist`: usage: no download or dependent counts available
- `pytest-xdist`: commits: 2 bot account(s) excluded from bus-factor counting
- `pytest-xdist`: triage: issue search did not answer
- `pywatchman`: usage: pypistats did not answer (download counts unknown)
- `pywatchman`: usage: GitHub code search did not answer
- `pywatchman`: usage: no download or dependent counts available
- `pywatchman`: triage: issue search did not answer
- `pyyaml`: usage: pypistats did not answer (download counts unknown)
- `pyyaml`: usage: GitHub code search did not answer
- `pyyaml`: usage: no download or dependent counts available
- `razorpay`: usage: pypistats did not answer (download counts unknown)
- `razorpay`: usage: GitHub code search did not answer
- `razorpay`: usage: no download or dependent counts available
- `razorpay`: triage: issue search did not answer
- `singledispatch`: usage: pypistats did not answer (download counts unknown)
- `singledispatch`: usage: GitHub code search did not answer
- `singledispatch`: usage: no download or dependent counts available
- `singledispatch`: triage: issue search did not answer
- `six`: usage: pypistats did not answer (download counts unknown)
- `six`: usage: GitHub code search did not answer
- `six`: usage: no download or dependent counts available
- `six`: triage: issue search did not answer
- `thrift`: usage: pypistats did not answer (download counts unknown)
- `thrift`: usage: GitHub code search did not answer
- `thrift`: usage: no download or dependent counts available
- `thrift`: forge: repository is not on GitHub (http://thrift.apache.org), so commit and issue history cannot be read
- `unidecode`: usage: pypistats did not answer (download counts unknown)
- `unidecode`: usage: GitHub code search did not answer
- `unidecode`: usage: no download or dependent counts available
- `unidecode`: forge: repository is not on GitHub (https://pypi.org/project/Unidecode/), so commit and issue history cannot be read
- `uvloop`: usage: pypistats did not answer (download counts unknown)
- `uvloop`: usage: GitHub code search did not answer
- `uvloop`: usage: no download or dependent counts available
- `uvloop`: triage: issue search did not answer
- `apipkg`: usage: pypistats did not answer (download counts unknown)
- `apipkg`: usage: GitHub code search did not answer
- `apipkg`: usage: no download or dependent counts available
- `cairocffi`: usage: pypistats did not answer (download counts unknown)
- `cairocffi`: usage: GitHub code search did not answer
- `cairocffi`: usage: no download or dependent counts available
- `click-didyoumean`: usage: pypistats did not answer (download counts unknown)
- `click-didyoumean`: usage: GitHub code search did not answer
- `click-didyoumean`: usage: no download or dependent counts available
- `colorama`: usage: pypistats did not answer (download counts unknown)
- `colorama`: usage: GitHub code search did not answer
- `colorama`: usage: no download or dependent counts available
- `defusedxml`: usage: pypistats did not answer (download counts unknown)
- `defusedxml`: usage: GitHub code search did not answer
- `defusedxml`: usage: no download or dependent counts available
- `django-versatileimagefield`: usage: pypistats did not answer (download counts unknown)
- `django-versatileimagefield`: usage: GitHub code search did not answer
- `django-versatileimagefield`: usage: no download or dependent counts available
- `et-xmlfile`: usage: pypistats did not answer (download counts unknown)
- `et-xmlfile`: usage: GitHub code search did not answer
- `et-xmlfile`: usage: no download or dependent counts available
- `et-xmlfile`: forge: repository is not on GitHub (https://foss.heptapod.net/openpyxl/et_xmlfile), so commit and issue history cannot be read
- `google-i18n-address`: usage: pypistats did not answer (download counts unknown)
- `google-i18n-address`: usage: GitHub code search did not answer
- `google-i18n-address`: usage: no download or dependent counts available
- `graphene`: usage: pypistats did not answer (download counts unknown)
- `graphene`: usage: GitHub code search did not answer
- `graphene`: usage: no download or dependent counts available
- `mccabe`: usage: pypistats did not answer (download counts unknown)
- `mccabe`: usage: GitHub code search did not answer
- `mccabe`: usage: no download or dependent counts available
- `measurement`: usage: pypistats did not answer (download counts unknown)
- `measurement`: usage: GitHub code search did not answer
- `measurement`: usage: no download or dependent counts available
- `measurement`: forge: repository is not on GitHub (https://pypi.org/project/measurement/), so commit and issue history cannot be read
- `openpyxl`: usage: pypistats did not answer (download counts unknown)
- `openpyxl`: usage: GitHub code search did not answer
- `openpyxl`: usage: no download or dependent counts available
- `openpyxl`: forge: repository is not on GitHub (https://foss.heptapod.net/openpyxl/openpyxl), so commit and issue history cannot be read
- `python-magic`: usage: pypistats did not answer (download counts unknown)
- `python-magic`: usage: GitHub code search did not answer
- `python-magic`: usage: no download or dependent counts available
- `python-magic`: commits: 1 bot account(s) excluded from bus-factor counting
- `python-magic`: triage: issue search did not answer
- `rx`: usage: pypistats did not answer (download counts unknown)
- `rx`: usage: GitHub code search did not answer
- `rx`: usage: no download or dependent counts available
- `rx`: forge: repository is not on GitHub (http://reactivex.io), so commit and issue history cannot be read
- `threadloop`: usage: pypistats did not answer (download counts unknown)
- `threadloop`: usage: GitHub code search did not answer
- `threadloop`: usage: no download or dependent counts available
- `threadloop`: triage: issue search did not answer
- `typing-inspect`: usage: pypistats did not answer (download counts unknown)
- `typing-inspect`: usage: GitHub code search did not answer
- `typing-inspect`: usage: no download or dependent counts available
- `typing-inspect`: triage: issue search did not answer
- `vine`: usage: pypistats did not answer (download counts unknown)
- `vine`: usage: GitHub code search did not answer
- `vine`: usage: no download or dependent counts available
- `vine`: commits: 2 bot account(s) excluded from bus-factor counting
- `vine`: triage: issue search did not answer
- `appdirs`: usage: pypistats did not answer (download counts unknown)
- `appdirs`: usage: GitHub code search did not answer
- `appdirs`: usage: no download or dependent counts available
- `atomicwrites`: usage: pypistats did not answer (download counts unknown)
- `atomicwrites`: usage: GitHub code search did not answer
- `atomicwrites`: usage: no download or dependent counts available
- `beautifultable`: usage: pypistats did not answer (download counts unknown)
- `beautifultable`: usage: GitHub code search did not answer
- `beautifultable`: usage: no download or dependent counts available
- `codecov`: usage: pypistats did not answer (download counts unknown)
- `codecov`: usage: GitHub code search did not answer
- `codecov`: usage: no download or dependent counts available
- `dj-email-url`: usage: pypistats did not answer (download counts unknown)
- `dj-email-url`: usage: GitHub code search did not answer
- `dj-email-url`: usage: no download or dependent counts available
- `django-debug-toolbar-request-history`: usage: pypistats did not answer (download counts unknown)
- `django-debug-toolbar-request-history`: usage: GitHub code search did not answer
- `django-debug-toolbar-request-history`: usage: no download or dependent counts available
- `django-graphiql-debug-toolbar`: usage: pypistats did not answer (download counts unknown)
- `django-graphiql-debug-toolbar`: usage: GitHub code search did not answer
- `django-graphiql-debug-toolbar`: usage: no download or dependent counts available
- `django-measurement`: usage: pypistats did not answer (download counts unknown)
- `django-measurement`: usage: GitHub code search did not answer
- `django-measurement`: usage: no download or dependent counts available
- `draftjs-sanitizer`: usage: pypistats did not answer (download counts unknown)
- `draftjs-sanitizer`: usage: GitHub code search did not answer
- `draftjs-sanitizer`: usage: no download or dependent counts available
- `enmerkar`: usage: pypistats did not answer (download counts unknown)
- `enmerkar`: usage: GitHub code search did not answer
- `enmerkar`: usage: no download or dependent counts available
- `gitdb`: usage: pypistats did not answer (download counts unknown)
- `gitdb`: usage: GitHub code search did not answer
- `gitdb`: usage: no download or dependent counts available
- `gitdb`: commits: 1 bot account(s) excluded from bus-factor counting
- `google-crc32c`: usage: pypistats did not answer (download counts unknown)
- `google-crc32c`: usage: GitHub code search did not answer
- `google-crc32c`: usage: no download or dependent counts available
- `google-crc32c`: commits: 1 bot account(s) excluded from bus-factor counting
- `google-measurement-protocol`: usage: pypistats did not answer (download counts unknown)
- `google-measurement-protocol`: usage: GitHub code search did not answer
- `google-measurement-protocol`: usage: no download or dependent counts available
- `google-measurement-protocol`: forge: repository is not on GitHub (https://pypi.org/project/google-measurement-protocol/), so commit and issue history cannot be read
- `graphql-relay`: usage: pypistats did not answer (download counts unknown)
- `graphql-relay`: usage: GitHub code search did not answer
- `graphql-relay`: usage: no download or dependent counts available
- `html-to-draftjs`: usage: pypistats did not answer (download counts unknown)
- `html-to-draftjs`: usage: GitHub code search did not answer
- `html-to-draftjs`: usage: no download or dependent counts available
- `html5lib`: usage: pypistats did not answer (download counts unknown)
- `html5lib`: usage: GitHub code search did not answer
- `html5lib`: usage: no download or dependent counts available
- `jaeger-client`: usage: pypistats did not answer (download counts unknown)
- `jaeger-client`: usage: GitHub code search did not answer
- `jaeger-client`: usage: no download or dependent counts available
- `jdcal`: usage: pypistats did not answer (download counts unknown)
- `jdcal`: usage: GitHub code search did not answer
- `jdcal`: usage: no download or dependent counts available
- `jsonfield`: usage: pypistats did not answer (download counts unknown)
- `jsonfield`: usage: GitHub code search did not answer
- `jsonfield`: usage: no download or dependent counts available
- `maxminddb-geolite2`: usage: pypistats did not answer (download counts unknown)
- `maxminddb-geolite2`: usage: GitHub code search did not answer
- `maxminddb-geolite2`: usage: no download or dependent counts available
- `opentracing`: usage: pypistats did not answer (download counts unknown)
- `opentracing`: usage: GitHub code search did not answer
- `opentracing`: usage: no download or dependent counts available
- `prices`: usage: pypistats did not answer (download counts unknown)
- `prices`: usage: GitHub code search did not answer
- `prices`: usage: no download or dependent counts available
- `prices`: triage: issue search did not answer
- `promise`: usage: pypistats did not answer (download counts unknown)
- `promise`: usage: GitHub code search did not answer
- `promise`: usage: no download or dependent counts available
- `promise`: triage: issue search did not answer
- `purl`: usage: pypistats did not answer (download counts unknown)
- `purl`: usage: GitHub code search did not answer
- `purl`: usage: no download or dependent counts available
- `purl`: triage: issue search did not answer
- `py`: usage: pypistats did not answer (download counts unknown)
- `py`: usage: GitHub code search did not answer
- `py`: usage: no download or dependent counts available
- `py`: forge: repository is not on GitHub (https://py.readthedocs.io/), so commit and issue history cannot be read
- `pydocstyle`: usage: pypistats did not answer (download counts unknown)
- `pydocstyle`: usage: GitHub code search did not answer
- `pydocstyle`: usage: no download or dependent counts available
- `pydocstyle`: triage: issue search did not answer
- `pylint-celery`: usage: pypistats did not answer (download counts unknown)
- `pylint-celery`: usage: GitHub code search did not answer
- `pylint-celery`: usage: no download or dependent counts available
- `pylint-celery`: triage: issue search did not answer
- `pytest-forked`: usage: pypistats did not answer (download counts unknown)
- `pytest-forked`: usage: GitHub code search did not answer
- `pytest-forked`: usage: no download or dependent counts available
- `pytest-forked`: triage: issue search did not answer
- `pytest-vcr`: usage: pypistats did not answer (download counts unknown)
- `pytest-vcr`: usage: GitHub code search did not answer
- `pytest-vcr`: usage: no download or dependent counts available
- `pytest-vcr`: triage: issue search did not answer
- `python-magic-bin`: usage: pypistats did not answer (download counts unknown)
- `python-magic-bin`: usage: GitHub code search did not answer
- `python-magic-bin`: usage: no download or dependent counts available
- `python-magic-bin`: triage: issue search did not answer
- `rsa`: usage: pypistats did not answer (download counts unknown)
- `rsa`: usage: GitHub code search did not answer
- `rsa`: usage: no download or dependent counts available
- `rsa`: triage: issue search did not answer
- `smmap`: usage: pypistats did not answer (download counts unknown)
- `smmap`: usage: GitHub code search did not answer
- `smmap`: usage: no download or dependent counts available
- `smmap`: commits: 2 bot account(s) excluded from bus-factor counting
- `smmap`: triage: issue search did not answer
- `text-unidecode`: usage: pypistats did not answer (download counts unknown)
- `text-unidecode`: usage: GitHub code search did not answer
- `text-unidecode`: usage: no download or dependent counts available
- `text-unidecode`: triage: issue search did not answer
- `toml`: usage: pypistats did not answer (download counts unknown)
- `toml`: usage: GitHub code search did not answer
- `toml`: usage: no download or dependent counts available
- `toml`: triage: issue search did not answer
- `transifex-client`: usage: pypistats did not answer (download counts unknown)
- `transifex-client`: usage: GitHub code search did not answer
- `transifex-client`: usage: no download or dependent counts available
- `transifex-client`: forge: repository is not on GitHub (https://www.transifex.com), so commit and issue history cannot be read
- `typed-ast`: usage: pypistats did not answer (download counts unknown)
- `typed-ast`: usage: GitHub code search did not answer
- `typed-ast`: usage: no download or dependent counts available
- `typed-ast`: triage: issue search did not answer
- `watchgod`: usage: pypistats did not answer (download counts unknown)
- `watchgod`: usage: GitHub code search did not answer
- `watchgod`: usage: no download or dependent counts available
- `watchgod`: commits: 1 bot account(s) excluded from bus-factor counting
- `watchgod`: triage: issue search did not answer
- direct dependencies taken from pyproject.toml

Verdicts follow rubric v1.0 (`docs/verdicts.md`). Dormant means no stable release for 730 days; dead means an archived repository, an explicit deprecation, or no release for 1460 days. If you think a threshold is wrong, that is a PR to the rubric, not a footnote.

## Sources

| # | Source | Retrieved |
|---|---|---|
| 1 | <https://pypi.org/pypi/apipkg/json> | 2026-11-17T04:13:40Z |
| 2 | <https://github.com/pytest-dev/apipkg> | 2026-11-17T04:13:40Z |
| 3 | <https://pypi.org/pypi/cairocffi/json> | 2026-11-17T04:13:40Z |
| 4 | <https://github.com/Kozea/cairocffi> | 2026-11-17T04:13:40Z |
| 5 | <https://pypi.org/pypi/click-didyoumean/json> | 2026-11-17T04:13:41Z |
| 6 | <https://pypi.org/pypi/colorama/json> | 2026-11-17T04:13:41Z |
| 7 | <https://github.com/tartley/colorama> | 2026-11-17T04:13:41Z |
| 8 | <https://pypi.org/pypi/defusedxml/json> | 2026-11-17T04:13:41Z |
| 9 | <https://pypi.org/pypi/dj-email-url/json> | 2026-11-17T04:13:41Z |
| 10 | <https://api.github.com/search/issues?q=repo:migonzalvar/dj-email-url+type:issue> | 2026-11-17T04:13:41Z |
| 11 | <https://pypi.org/pypi/django-measurement/json> | 2026-11-17T04:13:41Z |
| 12 | <https://pypi.org/pypi/draftjs-sanitizer/json> | 2026-11-17T04:13:41Z |
| 13 | <https://pypi.org/pypi/google-measurement-protocol/json> | 2026-11-17T04:13:41Z |
| 14 | <https://pypi.org/pypi/html-to-draftjs/json> | 2026-11-17T04:13:41Z |
| 15 | <https://github.com/jaegertracing/jaeger-client-python> | 2026-11-17T04:13:41Z |
| 16 | <https://pypi.org/pypi/jaeger-client/json> | 2026-11-17T04:13:41Z |
| 17 | <https://pypi.org/pypi/maxminddb-geolite2/json> | 2026-11-17T04:13:41Z |
| 18 | <https://github.com/opentracing/opentracing-python> | 2026-11-17T04:13:41Z |
| 19 | <https://pypi.org/pypi/opentracing/json> | 2026-11-17T04:13:41Z |
| 20 | <https://pypi.org/pypi/prices/json> | 2026-11-17T04:13:41Z |
| 21 | <https://pypi.org/pypi/purl/json> | 2026-11-17T04:13:41Z |
| 22 | <https://github.com/julian-r/python-magic> | 2026-11-17T04:13:42Z |
| 23 | <https://pypi.org/pypi/python-magic-bin/json> | 2026-11-17T04:13:42Z |
| 24 | <https://api.github.com/repos/julian-r/python-magic/commits> | 2026-11-17T04:13:42Z |
| 25 | <https://github.com/julian-r> | 2026-11-17T04:13:42Z |
| 26 | <https://pypi.org/pypi/text-unidecode/json> | 2026-11-17T04:13:42Z |
| 27 | <https://pypi.org/pypi/django-versatileimagefield/json> | 2026-11-17T04:13:41Z |
| 28 | <https://pypi.org/pypi/google-i18n-address/json> | 2026-11-17T04:13:41Z |
| 29 | <https://pypi.org/pypi/openpyxl/json> | 2026-11-17T04:13:41Z |
| 30 | <https://pypi.org/pypi/appdirs/json> | 2026-11-17T04:13:40Z |
| 31 | <https://github.com/untitaker/python-atomicwrites> | 2026-11-17T04:13:40Z |
| 32 | <https://pypi.org/pypi/atomicwrites/json> | 2026-11-17T04:13:40Z |
| 33 | <https://pypi.org/pypi/beautifultable/json> | 2026-11-17T04:13:40Z |
| 34 | <https://github.com/codecov/codecov-python> | 2026-11-17T04:13:41Z |
| 35 | <https://pypi.org/pypi/codecov/json> | 2026-11-17T04:13:41Z |
| 36 | <https://pypi.org/pypi/django-debug-toolbar-request-history/json> | 2026-11-17T04:13:41Z |
| 37 | <https://pypi.org/pypi/django-graphiql-debug-toolbar/json> | 2026-11-17T04:13:41Z |
| 38 | <https://pypi.org/pypi/enmerkar/json> | 2026-11-17T04:13:41Z |
| 39 | <https://github.com/gitpython-developers/gitdb> | 2026-11-17T04:13:41Z |
| 40 | <https://github.com/googleapis/python-crc32c> | 2026-11-17T04:13:41Z |
| 41 | <https://pypi.org/pypi/graphql-relay/json> | 2026-11-17T04:13:41Z |
| 42 | <https://pypi.org/pypi/html5lib/json> | 2026-11-17T04:13:41Z |
| 43 | <https://api.github.com/search/issues?q=repo:html5lib/html5lib-python+type:issue> | 2026-11-17T04:13:41Z |
| 44 | <https://pypi.org/pypi/jdcal/json> | 2026-11-17T04:13:41Z |
| 45 | <https://pypi.org/pypi/jsonfield/json> | 2026-11-17T04:13:41Z |
| 46 | <https://pypi.org/pypi/promise/json> | 2026-11-17T04:13:41Z |
| 47 | <https://pypi.org/pypi/py/json> | 2026-11-17T04:13:41Z |
| 48 | <https://github.com/PyCQA/pydocstyle> | 2026-11-17T04:13:41Z |
| 49 | <https://pypi.org/pypi/pydocstyle/json> | 2026-11-17T04:13:41Z |
| 50 | <https://pypi.org/pypi/pylint-celery/json> | 2026-11-17T04:13:42Z |
| 51 | <https://pypi.org/pypi/pytest-forked/json> | 2026-11-17T04:13:42Z |
| 52 | <https://pypi.org/pypi/pytest-vcr/json> | 2026-11-17T04:13:42Z |
| 53 | <https://github.com/sybrenstuvel/python-rsa> | 2026-11-17T04:13:42Z |
| 54 | <https://pypi.org/pypi/rsa/json> | 2026-11-17T04:13:42Z |
| 55 | <https://github.com/gitpython-developers/smmap> | 2026-11-17T04:13:42Z |
| 56 | <https://pypi.org/pypi/toml/json> | 2026-11-17T04:13:42Z |
| 57 | <https://pypi.org/pypi/transifex-client/json> | 2026-11-17T04:13:42Z |
| 58 | <https://github.com/python/typed_ast> | 2026-11-17T04:13:42Z |
| 59 | <https://pypi.org/pypi/typed-ast/json> | 2026-11-17T04:13:42Z |
| 60 | <https://pypi.org/pypi/watchgod/json> | 2026-11-17T04:13:42Z |
| 61 | <https://pypi.org/pypi/et-xmlfile/json> | 2026-11-17T04:13:41Z |
| 62 | <https://pypi.org/pypi/graphene/json> | 2026-11-17T04:13:41Z |
| 63 | <https://api.github.com/search/issues?q=repo:graphql-python/graphene+type:issue> | 2026-11-17T04:13:41Z |
| 64 | <https://pypi.org/pypi/mccabe/json> | 2026-11-17T04:13:41Z |
| 65 | <https://github.com/PyCQA/mccabe> | 2026-11-17T04:13:41Z |
| 66 | <https://pypi.org/pypi/measurement/json> | 2026-11-17T04:13:41Z |
| 67 | <https://pypi.org/pypi/python-magic/json> | 2026-11-17T04:13:42Z |
| 68 | <https://github.com/ahupp/python-magic> | 2026-11-17T04:13:42Z |
| 69 | <https://pypi.org/pypi/rx/json> | 2026-11-17T04:13:42Z |
| 70 | <https://pypi.org/pypi/threadloop/json> | 2026-11-17T04:13:42Z |
| 71 | <https://github.com/breerly/threadloop> | 2026-11-17T04:13:42Z |
| 72 | <https://api.github.com/repos/breerly/threadloop/commits> | 2026-11-17T04:13:42Z |
| 73 | <https://pypi.org/pypi/typing-inspect/json> | 2026-11-17T04:13:42Z |
| 74 | <https://github.com/ilevkivskyi/typing_inspect> | 2026-11-17T04:13:42Z |
| 75 | <https://api.github.com/repos/ilevkivskyi/typing_inspect/commits> | 2026-11-17T04:13:42Z |
| 76 | <https://github.com/leon-sony> | 2026-11-17T04:13:42Z |
| 77 | <https://pypi.org/pypi/vine/json> | 2026-11-17T04:13:42Z |
| 78 | <https://github.com/celery/vine> | 2026-11-17T04:13:42Z |
| 79 | <https://api.github.com/repos/mirumee/django-prices/commits> | 2026-11-17T04:13:41Z |
| 80 | <https://github.com/filipmlynarski-mirumee> | 2026-11-17T04:13:41Z |
| 81 | <https://api.github.com/repos/jschneier/django-storages/commits> | 2026-11-17T04:13:41Z |
| 82 | <https://github.com/jasongi> | 2026-11-17T04:13:41Z |
| 83 | <https://api.github.com/repos/graphql-python/graphene-django/commits> | 2026-11-17T04:13:41Z |
| 84 | <https://github.com/superlevure> | 2026-11-17T04:13:41Z |
| 85 | <https://api.github.com/repos/razorpay/razorpay-python/commits> | 2026-11-17T04:13:42Z |
| 86 | <https://github.com/ankitdas13> | 2026-11-17T04:13:42Z |
| 87 | <https://api.github.com/repos/asottile/cfgv/commits> | 2026-11-17T04:13:41Z |
| 88 | <https://github.com/asottile> | 2026-11-17T04:13:41Z |
| 89 | <https://api.github.com/repos/Kozea/cssselect2/commits> | 2026-11-17T04:13:41Z |
| 90 | <https://github.com/liZe> | 2026-11-17T04:13:41Z |
| 91 | <https://api.github.com/repos/django-compressor/django-appconf/commits> | 2026-11-17T04:13:41Z |
| 92 | <https://github.com/sparrowt> | 2026-11-17T04:13:41Z |
| 93 | <https://api.github.com/repos/feincms/django-js-asset/commits> | 2026-11-17T04:13:41Z |
| 94 | <https://github.com/matthiask> | 2026-11-17T04:13:41Z |
| 95 | <https://api.github.com/repos/PyCQA/pyflakes/commits> | 2026-11-17T04:13:41Z |
| 96 | <https://api.github.com/repos/pylint-dev/pylint-plugin-utils/commits> | 2026-11-17T04:13:42Z |
| 97 | <https://github.com/carlio> | 2026-11-17T04:13:42Z |
| 98 | <https://api.github.com/repos/NyanKiyoshi/pytest-django-queries/commits> | 2026-11-17T04:13:42Z |
| 99 | <https://github.com/NyanKiyoshi> | 2026-11-17T04:13:42Z |
| 100 | <https://api.github.com/repos/CourtBouillon/webencodings/commits> | 2026-11-17T04:13:42Z |
| 101 | <https://github.com/liZe> | 2026-11-17T04:13:42Z |

_Retrieved-at dates are when DeadLedger first stored each response. Re-running offline reuses those dates rather than pretending the world was re-observed._
