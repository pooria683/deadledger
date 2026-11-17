"""GitHub forge facts: bus factor, triage, and the ways they go wrong.

The forge module is where a mortality tool is most likely to lie: a partial
page of commits can produce a bus factor of 1 for a healthy project.  These
tests pin the "refuse to publish a partial answer" behaviour.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from deadledger.cache import Cache
from deadledger.evidence import PackageEvidence
from deadledger.forge import (
    SEARCH_BUDGET_FLOOR,
    _author_identity,
    _committers,
    _issue_counts,
    attach_repo_facts,
    fetch_repo_facts,
)
from deadledger.http import Fetched

UTC = timezone.utc
NOW = datetime(2026, 11, 16, tzinfo=UTC)


class StubClient:
    """A client whose answers a test dictates, including failures."""

    def __init__(self, handler, *, budget=None):
        self.handler = handler
        self._budget = budget
        self.asked: list[str] = []
        self.mode = "online"
        self.consumed: list[str] = []

    def get_json(self, url: str, **kwargs):
        self.asked.append(url)
        return self.handler(url, kwargs)

    def budget(self, url: str):
        return self._budget

    def consume(self, url: str) -> None:
        self.consumed.append(url)


def repo_payload(**overrides):
    payload = {
        "full_name": "psf/requests",
        "html_url": "https://github.com/psf/requests",
        "archived": False,
        "pushed_at": "2026-11-02T16:55:12Z",
        "open_issues_count": 256,
        "stargazers_count": 54714,
        "default_branch": "main",
    }
    payload.update(overrides)
    return payload


def commit(login: str, days_ago: int, sha: str = "a" * 40, name: str = "Dev", email: str = "d@x"):
    when = (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "sha": sha,
        "author": {"login": login} if login else None,
        "commit": {"author": {"name": name, "email": email, "date": when}},
    }


def make_client(commits_by_page, *, repo=None, issues=(10, 8), budget=None):
    def handler(url, kwargs):
        if "/commits" in url:
            return Fetched(url=url, payload=commits_by_page, fetched_at=NOW)
        if "/search/issues" in url:
            created, closed = issues
            is_closed = "is:closed" in url
            return Fetched(
                url=url,
                payload={"total_count": closed if is_closed else created},
                fetched_at=NOW,
            )
        return Fetched(url=url, payload=repo or repo_payload(), fetched_at=NOW)

    return StubClient(handler, budget=budget)


def test_bus_factor_counts_distinct_human_committers():
    client = make_client([commit("alice", 10), commit("alice", 20), commit("bob", 30)])
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.commits_12mo == 3
    assert {c.name for c in facts.committers} == {"alice", "bob"}
    assert facts.top_share == pytest.approx(2 / 3, abs=0.01)


def test_bots_are_excluded_and_the_exclusion_is_reported():
    client = make_client(
        [
            commit("alice", 10),
            commit("dependabot[bot]", 11),
            commit("renovate-bot", 12),
            commit("github-actions[bot]", 13),
        ]
    )
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.commits_12mo == 1
    assert {c.name for c in facts.committers} == {"alice"}
    assert any("bot account" in gap for gap in facts.gaps)


def test_committer_last_activity_is_cited_from_the_newest_commit():
    client = make_client(
        [commit("alice", 40, sha="f" * 40), commit("alice", 3, sha="e" * 40)]
    )
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    lead = facts.committers[0]
    assert lead.name == "alice"
    assert lead.commits == 2
    assert lead.last_commit_sha == "e" * 40
    assert lead.last_commit_at == NOW - timedelta(days=3)


def test_partial_history_refuses_to_publish_a_bus_factor():
    """A failed page must not become '1 committer' for a busy project."""
    calls = {"n": 0}

    def handler(url, kwargs):
        if "/commits" in url:
            calls["n"] += 1
            if calls["n"] > 1:
                from deadledger.errors import SourceUnavailable

                raise SourceUnavailable(url, "boom")
            # A full page implies there might be more history.
            return Fetched(
                url=url,
                payload=[commit("alice", 5, sha=f"{i:040d}") for i in range(100)],
                fetched_at=NOW,
                headers={"link": '<https://api.github.com/x?page=2>; rel="next"'},
            )
        return Fetched(url=url, payload=repo_payload(), fetched_at=NOW)

    client = StubClient(handler)
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.commits_12mo is None
    assert facts.committers == []
    assert any("could not be read" in gap for gap in facts.gaps)


def test_triage_rate_is_closed_over_created():
    client = make_client([commit("alice", 5)], issues=(20, 5))
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.issues_created_12mo == 20
    assert facts.issues_closed_12mo == 5
    assert facts.triage_rate == pytest.approx(0.25)


def test_triage_is_skipped_when_the_search_budget_is_exhausted():
    client = make_client([commit("alice", 5)], issues=(20, 5), budget=0)
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.triage_rate is None
    assert any("quota exhausted" in gap for gap in facts.gaps)
    # And it did not waste a request finding out.
    assert not any("/search/issues" in url for url in client.asked)


def test_archived_flag_is_carried_through():
    client = make_client([], repo=repo_payload(archived=True))
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    assert facts.archived


def test_author_identity_prefers_login_then_name_then_email():
    assert _author_identity({"author": {"login": "alice"}}, {}) == "alice"
    assert (
        _author_identity({"author": None}, {"name": "Bob", "email": "b@x"})
        == "Bob <b@x>"
    )
    assert _author_identity({"author": None}, {"name": "Cid"}) == "Cid <unknown>"
    assert _author_identity({"author": None}, {}) is None


def test_committers_are_sorted_by_volume_then_recency():
    people = [
        ("alice", NOW - timedelta(days=1), "a"),
        ("bob", NOW - timedelta(days=2), "b"),
        ("bob", NOW - timedelta(days=3), "c"),
    ]
    committers = _committers(people)
    assert [c.name for c in committers] == ["bob", "alice"]


def test_attach_records_citations_for_every_claim():
    client = make_client([commit("alice", 5)], issues=(4, 3))
    facts = fetch_repo_facts(client, "psf/requests", now=NOW)
    evidence = PackageEvidence(ecosystem="pypi", name="requests")
    attach_repo_facts(evidence, facts)

    for field in (
        "commits_12mo_obs",
        "committers_12mo_obs",
        "top_committer_share_obs",
        "triage_rate_obs",
        "last_commit_obs",
        "issue_created_12mo_obs",
    ):
        observation = getattr(evidence, field)
        assert observation is not None, field
        # Citations point at the exact endpoint the number came from: the API
        # for API facts, the repository page for pushed_at.
        assert observation.url.startswith(("https://api.github.com", "https://github.com")), field
        assert observation.retrieved_at is not None


def test_attach_without_a_repository_is_an_explicit_gap():
    evidence = PackageEvidence(ecosystem="pypi", name="pkg")
    attach_repo_facts(evidence, None)
    assert evidence.source_gaps == ["forge: no readable public repository"]
    assert not evidence.forge_ok


def test_unreadable_repository_returns_none_not_an_exception():
    from deadledger.errors import NotFound

    def handler(url, kwargs):
        raise NotFound(url, "not found")

    assert fetch_repo_facts(StubClient(handler), "nobody/nothing", now=NOW) is None


def test_issue_counts_return_none_on_failure():
    from deadledger.errors import SourceUnavailable

    def handler(url, kwargs):
        raise SourceUnavailable(url, "down")

    created, closed = _issue_counts(StubClient(handler), "a/b", NOW - timedelta(days=365))
    assert created is None and closed is None


def test_search_budget_floor_is_positive():
    assert SEARCH_BUDGET_FLOOR >= 1
