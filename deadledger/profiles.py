"""Where facts come from, and how long they stay true.

Every remote endpoint DeadLedger knows about belongs to a *profile*.  A
profile carries the base URL (so it can be pointed at a mirror) and the TTL
for responses from it.  The four operating modes are properties of the
client, not of the profiles:

===========  =============================================================
online       cache-first with TTL; on a source failure fall back to the
             stale copy and say so in the report
offline      cache-only, stale data allowed, citations keep their
             original retrieved-at dates
record       fetch live, write every response into a fixture profile
replay       serve only from a fixture profile; the socket is never opened
===========  =============================================================

TTLs are short where "is it alive *today*" matters (commits, publish
dates) and long where the answer is historical and therefore immutable
(release history never changes; only the newest entry does).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR


@dataclass(frozen=True)
class Profile:
    name: str
    base_url: str
    ttl_seconds: int
    description: str
    auth_header: str | None = None
    auth_env: tuple[str, ...] = ()
    #: Some APIs demand a descriptive UA and will 403 without it.
    user_agent: str | None = None
    accepts: str | None = None


# The order matters for `deadledger doctor` output and docs.
PROFILES: dict[str, Profile] = {
    "pypi": Profile(
        name="pypi",
        base_url="https://pypi.org",
        ttl_seconds=6 * HOUR,
        description="PyPI JSON API (releases, owners, OSV advisories)",
    ),
    "pypistats": Profile(
        name="pypistats",
        base_url="https://pypistats.org",
        ttl_seconds=DAY,
        description="PyPI download counts (third-party mirror of BigQuery data)",
    ),
    "npm": Profile(
        name="npm",
        base_url="https://registry.npmjs.org",
        ttl_seconds=6 * HOUR,
        description="npm registry packument (releases, maintainers, deprecation)",
    ),
    "npm-downloads": Profile(
        name="npm-downloads",
        base_url="https://api.npmjs.org",
        ttl_seconds=DAY,
        description="npm download counts",
    ),
    "crates": Profile(
        name="crates",
        base_url="https://crates.io",
        ttl_seconds=6 * HOUR,
        description="crates.io API (releases, owners, reverse dependencies)",
        user_agent=(
            "deadledger/{version} (https://github.com/pooria683/deadledger; "
            "mortality audits)"
        ),
    ),
    "github": Profile(
        name="github",
        base_url="https://api.github.com",
        ttl_seconds=12 * HOUR,
        description="GitHub REST API (commits, issue triage, usage proxy)",
        auth_header="Authorization",
        auth_env=("DEADLEDGER_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"),
        user_agent="deadledger (https://github.com/pooria683/deadledger)",
    ),
}

FIXTURE_ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


def get_profile(name: str) -> Profile:
    try:
        return PROFILES[name]
    except KeyError:  # pragma: no cover - programming error
        raise KeyError(f"unknown profile {name!r}; known: {', '.join(PROFILES)}") from None


def profile_for_url(url: str) -> Profile | None:
    """Best-effort reverse lookup so recorded fixtures group sanely."""
    for profile in PROFILES.values():
        if url.startswith(profile.base_url):
            return profile
    return None
