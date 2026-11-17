# Writing an adapter

An adapter is the only part of DeadLedger that knows what a registry looks
like. Everything downstream — the rubric, the orphan simulation, the report,
the ledger — consumes `PackageEvidence` and knows nothing about PyPI, npm, or
crates.io.

Adding an ecosystem means writing one module and one fixture profile. That is
the intended cost, and the existing three adapters are the specification.

## The contract

```python
class Adapter:
    ecosystem: str                     # "pypi" | "npm" | "crates" | ...
    lockfile_names: tuple[str, ...]    # what to look for on disk
    capabilities: AdapterCapabilities  # what this ecosystem can actually tell us
    pace_seconds: float                # minimum delay between HTTP calls

    def gather(self, client, name, version) -> PackageEvidence: ...
```

Two rules:

1. **Adapters collect, they do not judge.** No adapter imports
   `deadledger.mortality`. If you find yourself writing "if last_release >
   730 days" in an adapter, it belongs in the rubric where it can be argued
   about, versioned, and tested at its boundary.
2. **Adapters degrade, they do not fail.** Every optional source is wrapped so
   that a failure becomes `evidence.add_gap(...)`. An exception escaping
   `gather` is a bug: it means one package can take down an audit.

## Registering it

```python
# deadledger/adapters/__init__.py
ADAPTERS: dict[str, Adapter] = {
    "pypi": PyPIAdapter(),
    "npm": NpmAdapter(),
    "crates": CratesAdapter(),
    "rubygems": RubyGemsAdapter(),   # yours
}
```

Then add a `Profile` in `deadledger/profiles.py` with the base URL and a TTL,
and teach `lockfiles.py` about the lockfile format if it is new.

## What to fill in, and what to leave as a gap

`PackageEvidence` has slots for each signal. Fill the ones your ecosystem
publishes; leave the rest unset and add a gap explaining why. The report renders
a gap as "we could not see this", which is always better than a zero.

| field | meaning | if your ecosystem has nothing |
|---|---|---|
| `last_publish_obs` | newest stable release date | required; without it the package is `unknown` |
| `releases_12mo_obs` | stable releases in the last year | required for a `thriving` verdict |
| `maintainer_count_obs` | accounts with publish rights | leave unset + gap |
| `download_count_obs` | downloads in a window | leave unset + gap |
| `dependents_obs` | count of packages that depend on it | leave unset; most registries do not publish this |
| `deprecated` / `deprecation_message` | registry-level deprecation | leave `False` |

Two habits that make an adapter good rather than merely working:

* **Say what a number is.** `obs(..., detail="downloads in the last month",
  method="downloads.downloads")` ends up verbatim in the report's evidence
  table. A number without a unit is a rumour.
* **Exclude what does not count.** Prereleases and fully-yanked releases must
  not enter `releases` as stable activity, or every project that tags an alpha
  looks alive forever.

## Recording fixtures

Adapter tests run against recorded responses, never the network:

```sh
deadledger record --profile my-ecosystem --lockfile path/to/lockfile
```

Recording is a two-pass process:

1. the real adapters run live and every response (and every failure) is kept in
   memory;
2. the same adapter code replays from memory, and only the URLs that pass 2
   actually asked for are written to disk.

That second pass is why the fixture directory stays small (the NetBox profile is
~3 MB for 27 packages) and why committing fixtures also proves the replay path
works. Payloads are trimmed to the fields the adapters read — see
`trim_payload()` in `deadledger/http.py` — so a 4 MB packument does not bloat
every clone.

Query parameters that change every run (`?since=<now - 365d>`) are normalised in
fixture URLs, so an unchanged registry re-records to the same file.

### Testing an adapter with fixtures

```python
def test_gather_extracts_cadence(replay):
    evidence = MyAdapter().gather(replay, "some-package", "1.2.3")
    assert evidence.registry_ok
    assert evidence.last_publish_obs.known
    for observation in evidence.observation_map().values():
        assert observation.url.startswith("http")   # every fact is cited
```

`replay` is a `CachingClient` in replay mode; see `tests/conftest.py`.

## The degradation path is part of the adapter

Test the unhappy path explicitly. For each source, assert that:

* a failure becomes a gap, not an exception;
* the resulting evidence produces an `unknown` verdict, not a `dead` one;
* the report still contains the package (silence is not an option).

`tests/test_adapters_crates.py` is the reference: crates.io is unreachable from
the environment its fixtures were recorded in, which forced the happy path to be
tested from synthetic recorded payloads and the sad path to be tested for real.

## Capabilities, honestly

`AdapterCapabilities` is printed by `deadledger sources`. It is a promise:
if `dependents=True`, the orphan simulation will quote an exact count and label
it `exact`. Do not set it for a proxy.
