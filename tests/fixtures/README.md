# Recorded fixtures

Every test in this suite runs **offline**. These directories are the responses
that make that possible: real API payloads, trimmed to the fields the adapters
read, replayed through the normal HTTP client.

```
tests/fixtures/<profile>/
    <host>_<path>_<query>.<hash>.json     a recorded response
    ...
```

## What a fixture contains

```json
{
  "url": "https://pypi.org/pypi/django/json",
  "status": 200,
  "fetched_at": "2026-11-16T18:31:44Z",
  "headers": {"link": "<https://api.github.com/...>; rel=\"next\""},
  "body": { "...": "the trimmed payload" }
}
```

Two things about the format are deliberate:

* **`fetched_at` is real.** It becomes the citation's retrieval timestamp, and
  it is what makes the report's clock (`as_of`) reproducible. Fixtures are
  never re-stamped on replay.
* **Failures are recorded too**, as `{"status": 0, "error": "..."}`. A source
  that did not answer during recording must stay "did not answer" in the test,
  because "unknown is not dead" is a product rule and it needs a fixture that
  proves the degradation path actually runs. A profile with no failures in it
  has not tested anything.

Rate-limit headers are deliberately **not** stored: they describe the moment of
retrieval, and a replayed `x-ratelimit-remaining: 0` would make a later run
believe its quota was spent. `link` is kept, because pagination has to survive a
cache hit.

## The profiles

| profile | lockfile | captured | used by |
|---|---|---|---|
| `netbox-3.0` | `examples/netbox-3.0/requirements.txt` | 139 responses, 27 gaps | adapter, rubric, determinism, report, orphan and CLI tests |
| `legacy-npm` | `examples/legacy-npm/package-lock.json` | 40 responses, 20 gaps | npm adapter and deprecation tests |

The gaps are the point as much as the responses: pypistats and `api.npmjs.org`
were unreachable from the recording environment, and crates.io was blocked
entirely, so the downloaded-count and dependent-count code paths are exercised
as *missing data* rather than as fabricated numbers.

## Re-recording

```sh
export GITHUB_TOKEN=$(gh auth token)
deadledger record --profile netbox-3.0 \
    --lockfile examples/netbox-3.0/requirements.txt
```

Re-record when an upstream API changes shape or a package in the demo tree
publishes something new. The command is two-pass:

1. **live** — run every adapter against the real APIs, keeping each response in
   memory;
2. **playback** — run the same audit again from those responses, and write only
   the URLs an audit actually asks for.

Pass 2 exists because pass 1 asks for more than an audit needs, and because the
set of URLs an audit touches depends on what the earlier calls returned (no
repository URL means no commit history). Both passes must go through
`canonical_fixture_url()`, because commit windows contain a `since=` timestamp
derived from the clock: without canonicalisation, pass 1 and pass 2 ask for
different URLs and every commit history silently becomes a gap. That bug
shipped once; `tests/test_cache_offline.py` now guards it.

## Rules for contributors

* **Never hand-edit a fixture body** to make a test pass. Re-record it. A
  hand-edited fixture tests your imagination, not the registry.
* Keep payloads trimmed. `write_fixture` keeps only the fields the adapters
  read; a raw npm packument is ~15 MB and would bloat the repository.
* A new adapter needs a profile with at least one recorded *failure*, or it has
  not proven that it degrades.
