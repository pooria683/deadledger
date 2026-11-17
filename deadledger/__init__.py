"""DeadLedger: mortality reports for dependency trees.

The public surface is deliberately small.  Everything that makes a verdict is
in :mod:`deadledger.mortality`; everything that talks to a registry is an
adapter under :mod:`deadledger.adapters`.
"""

__version__ = "0.1.0"

#: Version of the *verdict rubric*.  Bump this whenever a threshold changes.
#: It is recorded in every report and is the anchor for "why did my verdict
#: change since last week?".  See docs/verdicts.md and docs/rubric-changelog.md.
RUBRIC_VERSION = "1.0"

__all__ = ["__version__", "RUBRIC_VERSION"]
