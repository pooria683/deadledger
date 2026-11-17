"""npm adapter against recorded packuments.

The legacy-npm fixture profile is a real 2021-era package-lock.json: express,
request, moment, left-pad and tslint, with their real transitive closure.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from deadledger.adapters.npm import NpmAdapter, _license
from deadledger.cache import Cache
from deadledger.http import CachingClient

UTC = timezone.utc


@pytest.fixture()
def npm_replay():
    client = CachingClient(None, Cache(":memory:"), mode="replay", profile="legacy-npm")
    yield client


def test_licence_shapes_are_handled():
    assert _license({"license": "MIT"}) == "MIT"
    assert _license({"license": {"type": "ISC"}}) == "ISC"
    assert _license({"licenses": [{"type": "Apache-2.0"}]}) == "Apache-2.0"
    assert _license({}) is None


def test_left_pad_is_deprecated_with_the_message(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "left-pad", "1.3.0")
    assert evidence.registry_ok
    assert evidence.deprecated
    assert "padStart" in (evidence.deprecation_message or "")


def test_request_is_deprecated_with_a_github_issue_link(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "request", "2.88.2")
    assert evidence.deprecated
    assert "github.com/request/request" in (evidence.deprecation_message or "")


def test_packument_gives_release_cadence_and_maintainers(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "moment", "2.29.1")
    assert evidence.releases, "a packument must yield dated releases"
    assert all(point.published_at < datetime(2030, 1, 1, tzinfo=UTC) for point in evidence.releases)
    assert evidence.last_publish_obs is not None
    assert evidence.maintainer_count_obs is not None
    if evidence.maintainer_count_obs.known:
        assert evidence.maintainer_count_obs.value == len(evidence.maintainers)


def test_repository_is_extracted_from_the_packument(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "express", "4.17.1")
    if evidence.repository:
        assert "/" in evidence.repository


def test_unpublished_package_becomes_a_gap_not_a_crash(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "this-was-never-published-xyz", "1.0.0")
    assert not evidence.registry_ok
    assert any("registry" in gap for gap in evidence.source_gaps)


def test_usage_comes_from_downloads_when_available(npm_replay):
    evidence = NpmAdapter().gather(npm_replay, "express", "4.17.1")
    if evidence.download_count_obs is not None and evidence.download_count_obs.known:
        assert evidence.usage_obs is not None
        assert evidence.usage_obs.method == "downloads"
        assert evidence.usage_obs.value == evidence.download_count_obs.value


def test_npm_never_claims_a_dependent_count(npm_replay):
    """npm publishes no reverse-dependency count; the orphan answer must say so."""
    evidence = NpmAdapter().gather(npm_replay, "express", "4.17.1")
    assert evidence.dependents_obs is None
    assert NpmAdapter().capabilities.dependents is False
