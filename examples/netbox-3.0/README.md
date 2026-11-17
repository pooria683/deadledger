# Demo: a real legacy tree

`requirements.txt` here is the dependency list NetBox shipped at tag `v3.0.0`
(August 2021), reproduced from
[netbox-community/netbox@v3.0.0/requirements.txt](https://github.com/netbox-community/netbox/blob/v3.0.0/requirements.txt).

It is a deliberate choice: NetBox 3.0 is a "legacy in production" tree — the
Django 3.2 LTS era, with supporting libraries several of which have since
stopped shipping. That is the inherited-codebase situation DeadLedger is for.

The generated report is in `REPORT.md`. Regenerate it with:

```sh
cd examples/netbox-3.0
deadledger audit --format markdown --output REPORT.md
```

## What the demo is *not*

It is not a claim that NetBox is badly maintained. NetBox itself is thriving;
this snapshot is three years stale by construction, which is the point: the
report describes the tree you inherited, not the project's current state.
