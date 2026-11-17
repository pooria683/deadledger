"""Exceptions.

DeadLedger distinguishes three failure modes because they demand different
behaviour from the caller (and different language in the report):

* ``SourceUnavailable`` -- a registry or forge did not answer.  The audit
  continues and the affected evidence is reported as *unknown*, never as
  *dead*.  Absence of evidence is not evidence of mortality.
* ``NotFound`` -- the source answered, and the answer is "no such package".
  That *is* evidence (a package that no longer exists in its registry).
* ``OfflineCacheMiss`` -- we were told to work offline and the cache has
  nothing for this package.  The audit continues; the package gets a
  ``known`` verdict (``unknown``), not a guess.
"""

from __future__ import annotations


class DeadLedgerError(Exception):
    """Base class for every error DeadLedger raises on purpose."""


class SourceUnavailable(DeadLedgerError):
    """A network source could not be reached or gave an unusable answer."""

    def __init__(self, source: str, detail: str = "", *, status: int | None = None):
        self.source = source
        self.detail = detail
        self.status = status
        super().__init__(f"{source}: {detail}" if detail else source)


class RateLimited(SourceUnavailable):
    """The source rate-limited us.  ``retry_after`` is in seconds, if known."""

    def __init__(self, source: str, detail: str = "", *, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(source, detail, status=429)


class NotFound(SourceUnavailable):
    """The source answered 404: the package or repository does not exist."""

    def __init__(self, source: str, detail: str = ""):
        super().__init__(source, detail, status=404)


class NoLockfile(DeadLedgerError):
    """No supported lockfile was found (or the one named is not parseable)."""


class EvidenceUnavailable(DeadLedgerError):
    """We were not allowed to ask (offline replay with no recording).

    Distinct from :class:`SourceUnavailable`, which means we asked and the
    source did not answer.  Both end up as a gap in the report, but the
    wording differs, and an audit must keep going in either case.
    """

    def __init__(self, detail: str):
        super().__init__(detail)


class OfflineCacheMiss(EvidenceUnavailable):
    """Offline mode, and this URL was never cached."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"offline: nothing cached for {url}")


class FixtureMissing(EvidenceUnavailable):
    """Recorded-response mode, and the fixtures do not cover this URL."""

    def __init__(self, profile: str, url: str):
        self.profile = profile
        self.url = url
        super().__init__(
            f"fixture profile {profile!r} has no recording for {url}\n"
            f"  re-record with: deadledger record --profile {profile} --lockfile <path>"
        )
