# Rubric changelog

The verdict rubric is a versioned artifact. This file is its history, and it
exists so that a verdict change can always be traced to a decision rather than
to a Tuesday.

Rules for entries:

* one section per version, newest first;
* say **what** moved, **why**, and — wherever possible — **which real package's
  verdict changed** as a result;
* if a change was made to stop a false positive, name the false positive.

---

## 1.0 — 2026-11-16

First published rubric.

Boundaries as published:

* dormant at **730 days** without a stable release; dead at **1460 days**;
* thriving requires **≥ 2 releases** *and* (**≥ 12 commits** or a commit within
  **90 days**);
* single maintainer = exactly **1** distinct committer in 365 days;
* low triage = **≤ 35 %** of last year's issues closed.

### Decisions worth recording

**Slow releases are not death, and this rule does not decide verdicts.**
The first draft of `R-DEVELOP-WITHOUT-RELEASE` *was* a deciding rule: no release
in a year, with commits in the last year, produced `dormant`. Recording the demo
tree caught it immediately: it marked **PyYAML dormant** (releases roughly once
a year, commits weekly) and **django-cors-headers dormant** (a release eight
months before the audit, commits that month). Those are two of the most widely
deployed Python packages in existence. The rule is now *supporting*: it changes
the remedy sentence, and its only verdict-level effect is to soften a
four-year-old release from `dead` to `dormant` when the repository is still
moving. Only the 730/1460-day release-age rules may reach `dormant` or `dead`.
There is a boundary test named after the PyYAML shape.

**`R-DEVELOP-WITHOUT-RELEASE` exists because of a false positive.**
An early draft of this rubric called a package "dead" whenever the newest
release was more than four years old. Run against a real tree, it libelled
`threadloop`, whose repository had received commits in the months before the
audit. The rubric now distinguishes "nobody is maintaining this" from "the
maintainer is committing but not publishing", because those have different
remedies (migrate vs. pin a git ref or ask for a release). A package with an
old release *and* a live repository is **dormant**, never dead.

**Bus factor does not decide verdicts.** The first draft elevated
single-maintainer packages to `dormant`. Against the NetBox 3.0 tree that
turned a dozen healthy packages orange, including ones that had shipped that
month. Concentration risk is now its own section (`## Bus factor`) with its own
sentence and its own citation. It can lower confidence in a thriving verdict —
it cannot create a death.

**Unknown is a first-class outcome.** The first draft defaulted a package to
`coasting` when every source failed. That reads as reassurance on a page where
the truth is "we could not look". `unknown` is now a bucket, a count, and a
colour, and it never fails CI.

**Transitive deaths do not fail builds.** Recorded here because it is a
rubric-level decision, not just a CLI one: a failure you cannot act on is a
failure people learn to ignore. Transitive and dev-only deaths are reported and
counted, but only critical (direct, non-dev) regressions gate a build.

### Known limits at 1.0

* Python has no native dependent count, so its orphan simulation is always a
  proxy (downloads, or a code-search count).
* The forge module only interrogates GitHub. Packages hosted elsewhere report
  the absence of forge evidence as a gap rather than guessing.
* "Last commit" is `pushed_at` from the repository record: it covers any
  branch, including push force-updates.
* Triage rate counts issues *created* in the window that are now closed. An
  issue closed as "won't fix" counts as closed, because the registry does not
  expose the reason.
