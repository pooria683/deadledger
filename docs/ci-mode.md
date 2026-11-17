# CI mode: fail on new deaths, not on old ones

`deadledger ci` exists because of a specific failure mode in dependency
checking: the check that is always red.

A tree with 200 transitive dependencies will contain dead ones. That is normal.
If a pipeline fails on every dead package it finds, the pipeline is red on day
one, someone adds `|| true`, and the check is dead too — just more quietly. The
same anti-fatigue logic that makes a failing test suite useful applies here:
**a check should only be red for something new that a human can act on.**

## What `ci` does

```sh
deadledger ci --sarif deadledger.sarif --report mortality.md
```

1. runs the audit, exactly as `audit` does;
2. compares the result against the project's ledger;
3. fails **only** if a *critical* package became dead or worse since the last
   recorded run;
4. records this run into the ledger so the next run knows about it;
5. writes a SARIF file and a Markdown report if asked, whether or not it failed.

## The rules, and why each one is there

### The first run is a baseline

A project adopting DeadLedger on a legacy tree should not get a red build for
deaths that predate the tool. The first run records everything and exits 0.

```
deadledger: first run for this project; baseline recorded at .deadledger/ledger-netbox.json.
  6 package(s) are already dead or dormant. Future runs fail only on NEW mortality.
```

If you *want* to fail on the first run, use `audit --fail-on critical` — the
choice is explicit rather than a surprise.

### Only critical regressions gate the build

"Critical" means direct and not dev. Those are the dependencies you chose, can
migrate, and would have to fix yourself. A dead transitive dependency is a
decision for whoever publishes the package that pulls it in: the build has
nothing actionable to point at, so it stays green and the report says what
happened.

### `worsened` is separate from `new`

| transition | classified as | fails the build |
|---|---|---|
| thriving/coasting → dead (critical) | new death | yes |
| thriving/coasting → dormant (critical) | worsened | yes |
| dormant → dead (critical) | new death | yes |
| anything → dead (transitive/dev) | worsened | no |
| dead/dormant → thriving/coasting | recovered | no (it is good news) |
| new package that is already dead | new death (critical only) | yes, unless the run is the baseline |

### `unknown` never fails anything

Being rate-limited, offline, or blocked is not a regression in the code. It is
a gap in the report. Failing here would punish the pipeline for a network
condition and teach people to disable the check.

## The ledger

One JSON file per project, next to your code:

```json
{
  "version": 1,
  "project": "netbox",
  "runs": 7,
  "last_run": "2026-11-16T18:09:44Z",
  "rubric_version": "1.0",
  "entries": {
    "django-pglocks@1.0.4": {
      "key": "django-pglocks@1.0.4",
      "name": "django-pglocks",
      "version": "1.0.4",
      "verdict": "dead",
      "first_seen": "2026-11-16",
      "last_seen": "2026-11-16",
      "critical": true,
      "rule_ids": ["R-DEPRECATED", "R-BUS-ONE"]
    }
  }
}
```

It is plain JSON on purpose. It belongs in version control next to the lockfile,
so CI runners are stateless: check it in, and the memory of past deaths travels
with the repository.

Commit the ledger. If you would rather not, cache `.deadledger/` between CI
runs in your CI provider — but understand that the ledger is the whole
anti-fatigue mechanism, and a lost ledger means one baseline run (which exits
0, so nothing breaks).

**Which ledger file?** `.deadledger/ledger-<project>.json`, keyed by the
project name from the lockfile (or the directory name). Two projects in one
repository get two ledgers automatically.

### Resetting the ledger

```sh
deadledger ledger reset --yes
```

Deletes the ledger. The next CI run is a baseline: it reports what it finds and
does not fail. Use it after a deliberate sweep where you accept the current
state as the new normal.

## Inspecting the ledger

```sh
deadledger ledger show
```

```
Ledger: .deadledger/ledger-netbox.json
  project: netbox   runs: 7   last: 2026-11-16T18:09:44Z

  verdict    package                  first seen   last seen    rules
  dead       django-graphiql-debug-toolbar  2026-11-16   2026-11-16   R-NO-RELEASE-DEAD
  dead       django-pglocks           2026-11-16   2026-11-16   R-DEPRECATED,R-BUS-ONE
  dormant    markdown-include         2026-11-16   2026-11-16   R-NO-RELEASE-DORMANT
```

`first_seen` is how long you have known about a death. A package that has been
dead for six months and isn't failing the build is a decision somebody made,
and the report says so.

## A complete GitHub Actions example

```yaml
name: dependency mortality
on:
  schedule: [{ cron: "0 7 * * 1" }]   # Mondays, before the week starts
  pull_request:
    paths: ["**/requirements.txt", "**/poetry.lock", "**/package-lock.json"]

jobs:
  deadledger:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write        # for SARIF upload
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      - run: pipx install deadledger

      - name: Audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # bus factor + triage
        run: deadledger ci --sarif deadledger.sarif --report mortality.md

      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: deadledger.sarif }

      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: mortality-report, path: mortality.md }

      # The ledger is the memory: commit it back, or cache it.
      #
      # Do NOT put the lockfile hash in this key. A ledger keyed on the
      # lockfile becomes a fresh baseline every time someone adds a dependency,
      # and the first run on a fresh baseline cannot fail -- so "we added a
      # package that is already dead" would be silently forgiven. Key the cache
      # on the branch, and let the ledger itself decide what is new.
      - uses: actions/cache@v4
        with:
          path: .deadledger
          key: deadledger-${{ github.ref_name }}
          restore-keys: deadledger-
```

Notes on the example:

* `GITHUB_TOKEN` gives 5,000 core requests/hour and 30 search requests/minute.
  Without it, DeadLedger still runs, but bus factor and triage become gaps —
  and the report says so rather than guessing.
* The ledger is keyed by branch, not by lockfile. Changing the lockfile must
  *not* reset the memory: adopting a new dependency that is already dead is
  precisely the event this check exists to catch, and a reset baseline is
  unable to report it. The ledger stores per-package verdicts, so packages that
  disappeared from the tree do not linger as false alarms.
* `actions/cache` is not a durable store -- entries are evicted after ~7 days
  of not being touched, and a cache miss is a baseline run that cannot fail.
  For a check you intend to rely on, commit `.deadledger/` to the repository,
  or restore it from an artifact. The tool is designed for either.
* `security-events: write` is only needed for the SARIF upload.

## Exit codes

| code | meaning |
|---|---|
| 0 | no new critical mortality (or first run) |
| 1 | **new** critical death or worsening since the last run |
| 2 | usage error: no lockfile, bad flag, unreadable map |
| 3 | the audit could not be completed (offline with an empty cache) |

A 3 is worth alerting on separately from a 1: it means the check did not run,
not that the code got worse.
