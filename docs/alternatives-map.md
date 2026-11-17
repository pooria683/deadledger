# The alternatives map

`maps/alternatives.json` answers one question: **this critical dependency is
dead — what do I move to, and how much work is that?**

It is a community asset, not a code artifact. It is versioned, reviewed, and
licensed MIT so other tools can build on it.

## The file

```json
{
  "_meta": {
    "version": "1.0.0",
    "updated_at": "2026-11-16",
    "schema": "...",
    "license": "MIT"
  },
  "entries": [
    {
      "ecosystem": "pypi",
      "package": "purl",
      "alternatives": [
        {
          "name": "yarl",
          "reason": "Actively maintained immutable URL object with a comparable path/query API.",
          "migration": "moderate",
          "notes": "purl exposes .path, .query, .add_query_param(); yarl uses .update_query().",
          "links": ["https://github.com/aio-libs/yarl"]
        }
      ]
    }
  ]
}
```

### Fields

| field | required | meaning |
|---|---|---|
| `ecosystem` | yes | `pypi`, `npm` or `crates` |
| `package` | yes | the dead package's name (normalised on load) |
| `alternatives[].name` | yes | the replacement |
| `alternatives[].reason` | yes | one plain sentence: *why* this replacement |
| `alternatives[].migration` | no | `drop-in` \| `minor` \| `moderate` \| `rewrite` |
| `alternatives[].api_diff` | no | 0–1: share of the old public API the new one covers |
| `alternatives[].basis` | **required if `api_diff` is set** | how that number was obtained |
| `alternatives[].notes` | no | the practical gotcha (renamed method, changed defaults) |
| `alternatives[].links` | no | where to read more |

## On `api_diff`

The number is a **migration-cost proxy**, and it is deliberately crude:

```
api_diff = |public names in old ∩ public names in new| / |public names in old|
```

It answers "is this a near drop-in or a rewrite?" — not "how many hours will
this cost". It is never presented as an estimate of effort.

Two rules keep it honest:

1. **Every `api_diff` states its basis**, and the basis begins with
   `measured`, `estimated` or `reported`. A number without a basis is folklore,
   and `deadledger map lint` rejects it.
2. **Unknown stays unknown.** If nobody has measured the surface, leave
   `api_diff` out. The report then prints the curator's `migration` label
   instead of a number. A fabricated 0.5 is worse than an honest "moderate".

Because the comparison is textual, it can only be as good as the surface
extracted. Today that means an explicit `api_surface` list (measured by hand)
or top-level module names; both are recorded in the entry, so a reader can see
how thin the evidence is.

## Layering: local overrides

Three layers, closest first:

1. `--map path/to/alternatives.json` (explicit — wins outright);
2. `~/.config/deadledger/alternatives.json` (your team's house rules);
3. the shipped `maps/alternatives.json` (the community file).

A package found in a closer layer wins entirely, so an organisation can pin its
own migration policy without forking the community map — and a report records
which layer it used (`alternatives map v1.0.0 (/home/you/.config/...)`).

## Validating a change

```sh
deadledger map lint
deadledger map show
```

`lint` checks structure, allowed ecosystems, duplicate entries, that every
alternative has a reason, that `api_diff` is within `[0, 1]`, and that any
`api_diff` carries a basis. CI runs it on every pull request.

The test suite additionally enforces that the shipped map has at least 50
entries across all three ecosystems (`tests/test_alternatives.py`), which is the
first-release bar in the README.

## Contributing an entry

Good entries have three qualities:

1. **They are specific.** "Use yarl, and note that `add_query_param` became
   `update_query`" is useful. "Consider alternatives" is not.
2. **They respect the maintainers.** "Abandoned" is a verdict, not a moral
   judgement. Say what the evidence is and move on.
3. **They admit uncertainty.** If you have not used the replacement, say so in
   `notes` rather than filling in an `api_diff` you cannot support.

Additions that remove a dead package from the map because it came back to life
are very welcome: note it in the pull request and bump `_meta.version`.

## Versioning

`_meta.version` follows semantic versioning from the consumer's point of view:

* **patch** — new entries for packages not yet covered, or link fixes;
* **minor** — changed recommendations for an existing entry;
* **major** — schema changes (new required field, changed semantics).

Reports quote the map version they used, so a report stays reproducible after
the map moves on.
