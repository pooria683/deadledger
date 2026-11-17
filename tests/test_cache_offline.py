"""The local-first contract (Requirement 6).

Three promises to keep:

1. registry responses are cached in SQLite with TTLs;
2. ``--offline`` never opens a socket, and says which entries went stale;
3. a cache miss offline is a *gap*, not a crash and not a zero.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from deadledger.cache import Cache
from deadledger.errors import OfflineCacheMiss
from deadledger.http import CachingClient
from deadledger.util import utcnow

URL = "https://pypi.org/pypi/widget/json"


def test_round_trip_preserves_payload_and_provenance(cache):
    entry = cache.put(
        "key", kind="pypi", url=URL, payload={"info": {"name": "widget"}}, ttl_seconds=60
    )
    again = cache.get("key")
    assert again.payload == {"info": {"name": "widget"}}
    assert again.url == URL
    assert again.fetched_at == entry.fetched_at
    assert not again.expired


def test_ttl_expiry_is_tracked(cache):
    past = utcnow() - timedelta(hours=2)
    cache.put("k", kind="pypi", url=URL, payload={}, ttl_seconds=60, fetched_at=past)
    entry = cache.get("k")
    assert entry.expired
    assert entry.ttl_seconds == 60


def test_stats_and_prune(cache):
    past = utcnow() - timedelta(days=1)
    cache.put("fresh", kind="pypi", url=URL, payload={"x": 1}, ttl_seconds=3600)
    cache.put("old", kind="npm", url="https://registry.npmjs.org/x", payload={}, ttl_seconds=60, fetched_at=past)
    stats = cache.stats()
    assert stats["entries"] == 2
    assert stats["fresh"] == 1
    assert stats["expired"] == 1
    assert cache.purge_expired() == 1
    assert cache.stats()["entries"] == 1


def test_offline_serves_stale_entries_and_marks_them(cache):
    past = utcnow() - timedelta(days=30)
    cache.put("k", kind="pypi", url=URL, payload={"info": {"name": "widget"}}, ttl_seconds=60, fetched_at=past)
    client = CachingClient(None, cache, mode="offline")
    # The client derives its cache key from the URL, so ask through a seeded key.
    from deadledger.http import cache_key

    cache.put(
        cache_key("pypi", URL),
        kind="pypi",
        url=URL,
        payload={"info": {"name": "widget"}},
        ttl_seconds=60,
        fetched_at=past,
    )
    fetched = client.get_json(URL, ttl_seconds=60)
    assert fetched.from_cache
    assert fetched.stale
    assert fetched.fetched_at == past, "offline keeps the original retrieval date"
    assert client.summary()["stale_urls"] == 1


def test_offline_cache_miss_raises_a_typed_error(cache):
    client = CachingClient(None, cache, mode="offline")
    with pytest.raises(OfflineCacheMiss):
        client.get_json("https://pypi.org/pypi/never-seen/json")
    assert client.summary()["failed_urls"] == 1


def test_cache_entry_keys_include_the_source_and_representation(cache):
    a = cache.put("k1", kind="pypi", url=URL, payload={"a": 1}, ttl_seconds=60)
    b = cache.put("k2", kind="npm", url=URL, payload={"a": 2}, ttl_seconds=60)
    assert cache.get(a.key).payload == {"a": 1}
    assert cache.get(b.key).payload == {"a": 2}


def test_cache_survives_reopening(tmp_path):
    path = tmp_path / "c.sqlite"
    with Cache(path) as first:
        first.put("k", kind="pypi", url=URL, payload={"ok": True}, ttl_seconds=600)
    with Cache(path) as second:
        assert second.get("k").payload == {"ok": True}


def test_missing_cache_file_is_reported_not_created(tmp_path):
    path = tmp_path / "absent.sqlite"
    with pytest.raises(FileNotFoundError):
        Cache(path, create=False)
    assert not path.exists()


def test_cache_stores_response_headers_so_pagination_survives(tmp_path):
    """A cached page must keep its Link header or pagination silently truncates."""
    with Cache(tmp_path / "c.sqlite") as cache:
        cache.put(
            "k",
            kind="github",
            url=URL,
            payload=[],
            ttl_seconds=600,
            headers={"link": '<https://api.github.com/x?page=2>; rel="next"'},
        )
        assert cache.get("k").headers["link"].endswith('rel="next"')


def test_newest_fetched_at_is_the_replay_clock(tmp_path):
    with Cache(tmp_path / "c.sqlite") as cache:
        assert cache.newest_fetched_at() is None
        early = utcnow() - timedelta(days=10)
        cache.put("a", kind="pypi", url=URL, payload={}, ttl_seconds=60, fetched_at=early)
        later = utcnow() - timedelta(days=1)
        cache.put("b", kind="pypi", url=URL, payload={}, ttl_seconds=60, fetched_at=later)
        assert cache.newest_fetched_at() == later


# --------------------------------------------------------------------------
# Budget accounting
#
# These exist because of a real bug that cost the demo its entire bus-factor
# column: GitHub bills /search/code, /search/* and everything else to three
# separate buckets, and spending from the wrong one made a run believe its core
# quota was gone. It then served 26 commit histories from cache, found nothing,
# and reported "no package had exactly one committer" -- a confident, cited,
# completely wrong answer.
# --------------------------------------------------------------------------


def test_budget_buckets_are_separate():
    from deadledger.http import _budget_for

    core = _budget_for("https://api.github.com/repos/pallets/click/commits?since=x")
    search = _budget_for("https://api.github.com/search/issues?q=repo:a/b+type:issue")
    code = _budget_for("https://api.github.com/search/code?q=%22import+click%22")

    assert core == "github"
    assert search == "github-search"
    assert code == "github-code-search"
    assert len({core, search, code}) == 3


def test_spending_a_search_does_not_exhaust_core(cache):
    """The regression: code-search spender must not block repo lookups."""
    from deadledger.http import PlaybackClient, CachingClient

    client = CachingClient(
        PlaybackClient(
            {
                "https://api.github.com/repos/a/b": {"default_branch": "main"},
                "https://api.github.com/search/code?q=x": {"total_count": 3},
            }
        ),
        cache,
        mode="record",
        profile="t",
    )
    client.rate_limits = {
        "github": {"remaining": 5000, "reset": 0},
        "github-code-search": {"remaining": 1, "reset": 0},
    }
    code_url = "https://api.github.com/search/code?q=x"
    client.get_json(code_url)
    client.spend(code_url)   # spends the last code-search token

    assert "github-code-search" in client.exhausted_profiles
    assert client.budget("https://api.github.com/repos/a/b") == 5000
    # Core is still usable: the repo lookup must go through.
    assert client.get_json("https://api.github.com/repos/a/b").payload == {"default_branch": "main"}


def test_rate_limit_headers_are_never_written_to_the_cache(tmp_path):
    """A cached "remaining: 0" would poison every later run."""
    from deadledger.cache import Cache
    from deadledger.http import Fetched, headers_to_cache

    kept = headers_to_cache(
        {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1800000000",
            "link": '<https://api.github.com/x?page=2>; rel="next"',
        }
    )
    assert kept == {"link": '<https://api.github.com/x?page=2>; rel="next"'}

    from deadledger.util import utcnow

    cache = Cache(tmp_path / "c.sqlite")
    cache.put(
        "https://api.github.com/repos/a/b",
        kind="github",
        url="https://api.github.com/repos/a/b",
        payload={"ok": True},
        ttl_seconds=3600,
        fetched_at=utcnow(),
        headers=kept,
    )
    stored = cache.get("https://api.github.com/repos/a/b")
    assert stored is not None
    assert "x-ratelimit-remaining" not in stored.headers


def test_playback_matches_commit_windows_across_different_clocks():
    """`since=` moves with the clock; the fixture must still be found."""
    from deadledger.http import PlaybackClient

    playback = PlaybackClient(
        {
            "https://api.github.com/repos/a/b/commits?since=2025-01-01T00:00:00Z&per_page=100": [
                {"sha": "abc"}
            ]
        }
    )
    later = playback.get_json(
        "https://api.github.com/repos/a/b/commits?since=2025-06-01T00:00:00Z&per_page=100"
    )
    assert later.payload == [{"sha": "abc"}]
