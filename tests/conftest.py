"""Shared fixtures.

The whole suite runs with **no network access**.  Adapters are exercised
against the recorded API responses in ``tests/fixtures/`` via the same
``CachingClient(replay)`` path production uses, so a test failure means the
adapter or the rubric changed shape relative to a real registry response --
not that an API was having a bad day.

``tests/fixtures/README.md`` explains how to re-record.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

os.environ.setdefault("DEADLEDGER_HOME", str(Path(__file__).parent / ".tmp-home"))

FIXTURES = Path(__file__).parent / "fixtures"
PROFILE = "netbox-3.0"
NOW = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def fixtures_root() -> Path:
    return FIXTURES


@pytest.fixture()
def cache(tmp_path):
    from deadledger.cache import Cache

    store = Cache(tmp_path / "cache.sqlite")
    yield store
    store.close()


@pytest.fixture()
def replay(cache):
    """A client that answers only from recorded fixtures."""
    from deadledger.http import CachingClient

    return CachingClient(None, cache, mode="replay", profile=PROFILE, fixture_root=FIXTURES)


@pytest.fixture()
def offline_client(cache):
    from deadledger.http import CachingClient

    return CachingClient(None, cache, mode="offline")


@pytest.fixture()
def now() -> datetime:
    return NOW


@pytest.fixture()
def netbox_requirements() -> Path:
    return Path(__file__).parent.parent / "examples" / "netbox-3.0" / "requirements.txt"


@pytest.fixture()
def replay_audit(replay, netbox_requirements):
    """The full NetBox audit, replayed from fixtures, computed once."""
    from deadledger.audit import Runner
    from deadledger.lockfiles import parse_lockfile

    inventory = parse_lockfile(netbox_requirements)
    return Runner(replay).run(inventory)


def make_evidence(**overrides):
    """Build a PackageEvidence with only the observations a test cares about.

    Kept in conftest (not imported from the package) so rubric tests do not
    depend on internal helpers that could be refactored away.
    """
    from deadledger.evidence import PackageEvidence, ReleasePoint, Maintainer, obs

    now = overrides.pop("now", NOW)
    evidence = PackageEvidence(
        ecosystem=overrides.pop("ecosystem", "pypi"),
        name=overrides.pop("name", "widget"),
        version=overrides.pop("version", "1.0.0"),
    )
    evidence.registry_ok = True
    evidence.registry_url = f"https://pypi.org/pypi/{evidence.name}/json"

    def stamp(value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(value, "strftime") else value

    for field, source in (
        ("last_publish_obs", "pypi"),
        ("releases_12mo_obs", "pypi"),
        ("maintainer_count_obs", "pypi"),
        ("last_commit_obs", "github"),
        ("commits_12mo_obs", "github"),
        ("committers_12mo_obs", "github"),
        ("triage_rate_obs", "github"),
        ("open_issues_obs", "github"),
        ("download_count_obs", "pypistats"),
        ("dependents_obs", "crates.io"),
        ("advisory_obs", "osv"),
    ):
        if field in overrides:
            value = overrides.pop(field)
            setattr(
                evidence,
                field,
                obs(
                    stamp(value),
                    source=source,
                    url=f"https://example.invalid/{field}",
                    retrieved_at=now,
                ),
            )

    if "releases" in overrides:
        points = overrides.pop("releases")
        evidence.releases = [
            ReleasePoint(version=str(index), published_at=when)
            for index, when in enumerate(points, start=1)
        ]
    if "committers" in overrides:
        committers = overrides.pop("committers")
        evidence.committers = [
            Maintainer(
                name=name,
                commits=count,
                last_commit_at=last,
                last_commit_sha="0" * 40,
            )
            for name, count, last in committers
        ]
    for key, value in overrides.items():
        setattr(evidence, key, value)
    return evidence
