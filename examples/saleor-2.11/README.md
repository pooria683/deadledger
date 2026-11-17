# Saleor 2.11.1 — the launch demo

This is the report the project leads with: a real, large, formerly
production-grade Python application, audited as it was tagged.

* **`poetry.lock`** — the actual lockfile from `saleor/saleor` at tag `2.11.1`
  (206 packages), fetched from the GitHub contents API.
* **`pyproject.toml`** — the same tag's project file, needed because
  `poetry.lock` v1 does not record which packages are direct dependencies.
* **`REPORT.md`** — the generated mortality report.

## What it found

| | |
|---|---|
| 206 packages | 56 critical (direct, non-dev), 150 transitive or dev |
| **37 dead** | 18 % of the tree |
| **17 dormant** | |
| 15 critical packages need a decision | 12 dead, 3 dormant |
| 15 packages with a bus factor of 1 | |

The tree is not obviously rotten — it is a normal Django application from
2020, and every package in it was a reasonable choice at the time. That is the
point: mortality accumulates quietly in trees that work.

## Regenerating

The report is deterministic. Two ways to reproduce it:

```sh
# From the network (needs GITHUB_TOKEN for bus factor and triage rate):
deadledger audit --lockfile examples/saleor-2.11/poetry.lock --include-dev

# Regenerate the committed file exactly:
deadledger audit --lockfile examples/saleor-2.11/poetry.lock --include-dev \
    -o examples/saleor-2.11/REPORT.md
```

## Why there are no committed fixtures for this profile

The recorded responses for 206 packages came to **79 MB**. That is a fine size
for a local cache and a poor size for a git repository, and unlike the NetBox
and npm profiles it is not needed to keep the test suite meaningful — those two
already cover every adapter and every rubric branch offline.

If you want to run this profile offline, record it yourself; it takes about
eight minutes:

```sh
deadledger record --profile saleor-2.11 --include-dev \
    --lockfile examples/saleor-2.11/poetry.lock
```

Recording `--include-dev` matters here. Without it the dev half of the tree is
missing from the fixtures, and the audit then reports ~100 packages as
`unknown` — which is technically honest but useless as a demo, and it looks
like a tool failure rather than a recording choice.
