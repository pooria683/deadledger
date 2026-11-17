"""crates.io adapter.

crates.io is not reachable from every environment (and is unreachable from the
one these fixtures were recorded in), which makes it the ideal adapter to test
both paths:

* the **happy path**, driven from a synthetic recorded payload in the crates.io
  schema, so the field mapping is pinned independently of network access;
* the **degradation path**, where the registry does not answer and the package
  must become ``unknown`` -- never ``dead``.
"""

from __future__ import annotations

import pytest

from deadledger.adapters.crates import CratesAdapter
from deadledger.cache import Cache
from deadledger.http import CachingClient, Fetched
from deadledger.orphans import simulate
from deadledger.util import utcnow

CRATE = {
    "crate": {
        "id": "rustc-serialize",
        "name": "rustc-serialize",
        "description": "Serialization and deserialization support for Rust",
        "downloads": 12_345_678,
        "recent_downloads": 234_567,
        "max_stable_version": "0.3.24",
        "newest_version": "0.3.24",
        "repository": "https://github.com/rust-lang-deprecated/rustc-serialize",
        "homepage": None,
    },
    "versions": [
        {"num": "0.3.24", "created_at": "2017-03-01T00:00:00Z", "yanked": False},
        {"num": "0.3.23", "created_at": "2016-12-01T00:00:00Z", "yanked": False},
        {"num": "0.4.0-alpha.1", "created_at": "2017-06-01T00:00:00Z", "yanked": False},
    ],
}


class StubPlayback:
    """Serves canned crates.io documents; used instead of a network client."""

    def __init__(self, documents: dict[str, object]):
        self.documents = documents
        self.asked: list[str] = []
        self.mode = "replay"

    def get_json(self, url: str, **_):
        self.asked.append(url)
        for prefix, payload in self.documents.items():
            if url.startswith(prefix):
                return Fetched(url=url, payload=payload, fetched_at=utcnow())
        from deadledger.errors import NotFound

        raise NotFound(url, "not found")

    def budget(self, url: str):
        return None

    def consume(self, url: str) -> None:
        return None


def test_happy_path_maps_the_crates_schema():
    stub = StubPlayback(
        {
            "https://crates.io/api/v1/crates/rustc-serialize/reverse_dependencies": {
                "dependencies": [],
                "meta": {"total": 42},
            },
            "https://crates.io/api/v1/crates/rustc-serialize/owners": {
                "users": [{"login": "alexcrichton", "url": "https://crates.io/users/alexcrichton"}]
            },
            "https://crates.io/api/v1/crates/rustc-serialize": CRATE,
        }
    )
    client = CachingClient(None, Cache(":memory:"), mode="replay", profile="x")
    client.inner = stub  # not used in replay mode; set for completeness
    # Replay mode has no fixtures, so drive the adapter through a live-shaped path.
    client.mode = "online"
    client.inner = stub
    adapter = CratesAdapter()
    adapter.pace_seconds = 0
    evidence = adapter.gather(client, "rustc-serialize", "0.3.24")

    assert evidence.registry_ok
    assert evidence.repository == "rust-lang-deprecated/rustc-serialize"
    assert evidence.latest_version == "0.3.24"
    assert evidence.download_count_obs.value == 12_345_678
    assert evidence.maintainer_count_obs.value == 1
    assert evidence.dependents_obs.value == 42
    assert evidence.usage_obs.method == "dependents", "crates publishes an exact count"

    # Prereleases are excluded from the stable cadence, so the newest stable is
    # 0.3.24, not 0.4.0-alpha.1.
    assert [p.version for p in evidence.stable_releases()][-1] == "0.3.24"


def test_orphan_answer_is_labelled_exact_for_crates():
    stub = StubPlayback(
        {
            "https://crates.io/api/v1/crates/tempdir/reverse_dependencies": {
                "dependencies": [],
                "meta": {"total": 1200},
            },
            "https://crates.io/api/v1/crates/tempdir/owners": {"users": [{"login": "steb"}]},
            "https://crates.io/api/v1/crates/tempdir": {
                **CRATE,
                "crate": {**CRATE["crate"], "name": "tempdir", "repository": None},
            },
        }
    )
    client = CachingClient(None, Cache(":memory:"), mode="online")
    client.inner = stub
    adapter = CratesAdapter()
    adapter.pace_seconds = 0
    evidence = adapter.gather(client, "tempdir", "0.3.7")
    answer = simulate(evidence)
    assert answer.reach_label == "exact"
    assert "1,200 crates depend on" in answer.answer


def test_yanked_version_is_recorded_as_deprecation():
    crate = {
        "crate": {**CRATE["crate"], "name": "yanked-crate"},
        "versions": [{"num": "1.0.0", "created_at": "2020-01-01T00:00:00Z", "yanked": True}],
    }
    stub = StubPlayback(
        {
            "https://crates.io/api/v1/crates/yanked-crate/reverse_dependencies": {"meta": {"total": 0}},
            "https://crates.io/api/v1/crates/yanked-crate/owners": {"users": []},
            "https://crates.io/api/v1/crates/yanked-crate": crate,
        }
    )
    client = CachingClient(None, Cache(":memory:"), mode="online")
    client.inner = stub
    adapter = CratesAdapter()
    adapter.pace_seconds = 0
    evidence = adapter.gather(client, "yanked-crate", "1.0.0")
    assert evidence.deprecated
    assert "yanked" in (evidence.deprecation_message or "")


def test_unreachable_registry_becomes_unknown_never_dead():
    """The most important crates.io behaviour in a sandboxed CI."""
    cache = Cache(":memory:")
    client = CachingClient(None, cache, mode="offline")
    evidence = CratesAdapter().gather(client, "serde", "1.0.130")
    assert not evidence.registry_ok
    assert evidence.source_gaps

    from deadledger.mortality import UNKNOWN, evaluate

    assert evaluate(evidence, now=utcnow()).verdict == UNKNOWN


def test_crates_rate_limit_is_polite():
    """crates.io asks for ~1 req/s; the adapter must pace itself."""
    assert CratesAdapter.pace_seconds >= 0.5
