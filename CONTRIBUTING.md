# Contributing to DeadLedger

Thanks for being here. There are two kinds of contribution this project cares
most about, and neither of them is a bug fix.

## 1. Disagree with a verdict

The verdict rubric ([`docs/verdicts.md`](docs/verdicts.md)) is a versioned
community artifact. It is *meant* to be argued with. The useful form of that
argument is:

> "Rubric 1.0 calls `<package>` dead/dormant/coasting. Here is why that is
> wrong, and here is the evidence."

Concretely:

1. Find a real package that the current rubric gets wrong.
2. Run `deadledger explain <package>` and paste the evidence table into the PR.
3. Say which rule misfired — the rule ids (`R-NO-RELEASE-DEAD`,
   `R-DEVELOP-WITHOUT-RELEASE`, …) are printed in the report and defined in the
   rubric.
4. Propose the smallest change that fixes your case without breaking the
   cases listed in [`docs/rubric-changelog.md`](docs/rubric-changelog.md).

Two examples of exactly this, both of which shaped v1.0 and are recorded in the
changelog:

* a package with commits from last week was called dead because its last
  release was four years old — that is now `dormant`, with a different remedy;
* PyYAML (releases roughly annually, commits weekly) was called dormant — that
  is now `coasting`, because "slow to release" is not "abandoned".

What a rubric PR must include:

- [ ] the change to `THRESHOLDS` or a rule in `deadledger/mortality.py`;
- [ ] the matching row change in `docs/verdicts.md` (a test enforces this);
- [ ] a `docs/rubric-changelog.md` entry naming the package whose verdict moves;
- [ ] a bump of `RUBRIC_VERSION` in `deadledger/__init__.py`;
- [ ] boundary tests in `tests/test_rubric_boundaries.py` covering one day
      either side of the new threshold.

"The threshold felt too strict" is not a PR. "It calls PyYAML dormant, and
here is why that is wrong" is.

## 2. Add an entry to the alternatives map

[`maps/alternatives.json`](maps/alternatives.json) is the community answer to
"this dead thing — what do I move to?". The schema and rules are in
[`docs/alternatives-map.md`](docs/alternatives-map.md). The short version:

- one plain sentence explaining *why* that replacement, not "consider
  alternatives";
- a `migration` label (`drop-in` / `minor` / `moderate` / `rewrite`);
- `api_diff` **only** if you can state a `basis` for it, beginning with
  `measured`, `estimated` or `reported`;
- `deadledger map lint` must pass.

Removing an entry because the package came back to life is very welcome — say
so in the PR, and bump `_meta.version` (patch for new entries, minor for
changed recommendations, major for schema changes).

## 3. Add an adapter

See [`docs/adapters.md`](docs/adapters.md). The rules that matter:

* adapters **collect**, they do not judge — no `deadledger.mortality` import in
  an adapter;
* adapters **degrade**, they do not fail — every optional source becomes a
  gap, never an exception;
* tests replay recorded fixtures, never the network. Record with
  `deadledger record --profile <name> --lockfile <path>`.

## 4. Report a bug

Include:

```sh
deadledger --version
deadledger doctor
deadledger audit --format json | head -50     # redact your package names if needed
```

If a verdict is wrong, `deadledger explain <package>` is far more useful than
a screenshot of the summary — it includes every citation.

---

## Working on the code

```sh
git clone https://github.com/pooria683/deadledger
cd deadledger
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

The suite runs with **no network access** and should stay that way. If a test
needs a new registry response, record it (`deadledger record`) and commit the
fixture — that is what makes the test suite meaningful rather than a check that
the internet is up.

### Style

* Python 3.11+, standard library first. `httpx` is the only runtime
  dependency, and even that has a `urllib` fallback.
* Type annotations on public functions.
* Comments explain *why*, not *what*. Where a rule exists because of a real
  false positive, name the package: those comments are the institutional memory
  of the rubric.
* Output is deterministic. Never call `datetime.now()` in the verdict path or
  a renderer — the clock is passed in.

### Before opening a PR

- [ ] `pytest` passes;
- [ ] `deadledger map lint` passes if you touched the map;
- [ ] new behaviour has a test, and a verdict change has a boundary test;
- [ ] docs updated if the public interface moved (`docs/verdicts.md`,
      `docs/ci-mode.md`, `docs/adapters.md`, `docs/alternatives-map.md`).

## Code of conduct

Be decent. This project takes positions on other people's work — "this package
is dead" is a statement about maintenance, not about the person who maintained
it. Keep the same standard when writing about maintainers that you would want
applied to your own projects: report the evidence, skip the contempt.

## License

Contributions are accepted under the MIT license, the same as the project.
