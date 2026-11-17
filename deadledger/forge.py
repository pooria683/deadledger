"""Facts that live in the code forge rather than the registry.

Requirement 2 (bus factor) needs commits, and requirement 1's triage signal
needs issues.  Both live on GitHub for the overwhelming majority of packages;
the functions here are deliberately forgiving:

* they return ``None`` (and leave a note) when the forge does not answer;
* they never guess a committer count from a partial page -- if a page cannot
  be fetched the whole metric becomes unknown, because a *wrong* bus factor is
  more dangerous than a missing one;
* they record the SHA and date of the bus factor's own last commit, so the
  report can say "one person, last seen 2023-04-02" and cite the commit.

GitHub's REST API is used read-only: repository metadata, commit history,
issue search.  Nothing about the audited project is ever sent.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .errors import EvidenceUnavailable, NotFound, RateLimited, SourceUnavailable
from .evidence import Maintainer, PackageEvidence, obs
from .http import CachingClient, Fetched, github_token
from .util import iso, parse_datetime, utcnow

API = "https://api.github.com"
PER_PAGE = 100
#: Hard ceiling on commit pages we will walk for one repository.
MAX_COMMIT_PAGES = 10

_BOT_RE = re.compile(r"(\[bot\]$|-bot$|^bot-|dependabot|renovate|github-actions)", re.I)


#: Stop *starting* a new repository's fact collection when the search budget
#: drops to this.  Each repo costs up to two searches (created + closed), and a
#: run that discovers the budget at zero reports a dozen packages as "forge did
#: not answer" -- which is both noisy and untrue.  Reserving a floor means we
#: spend the budget on a few complete, trustworthy receipts instead.
SEARCH_BUDGET_FLOOR = 2


@dataclass
class RepoFacts:
    """What we learned about a repository, ready to be attached to evidence."""

    full_name: str
    html_url: str
    archived: bool = False
    pushed_at: datetime | None = None
    open_issues: int | None = None
    stars: int | None = None
    default_branch: str | None = None
    commits_12mo: int | None = None
    committers: list[Maintainer] = field(default_factory=list)
    top_share: float | None = None
    issues_created_12mo: int | None = None
    issues_closed_12mo: int | None = None
    triage_rate: float | None = None
    code_search_count: int | None = None
    gaps: list[str] = field(default_factory=list)
    fetched: Fetched | None = None


def fetch_repo_facts(
    client: CachingClient,
    repo: str,
    *,
    now: datetime | None = None,
    include_code_search: bool = False,
    include_triage: bool = True,
    pages: int = MAX_COMMIT_PAGES,
) -> RepoFacts | None:
    """Collect repository facts, or ``None`` if the repository is not readable.

    ``None`` covers both "no such repo" and "GitHub would not talk to us"; the
    caller cannot distinguish them and must not treat either as "dead".
    """
    moment = now or utcnow()
    owner, _, name = repo.partition("/")
    if not owner or not name:
        return None
    url = f"{API}/repos/{owner}/{name}"
    try:
        fetched = client.get_json(url, ttl_seconds=None)
    except (NotFound, SourceUnavailable, EvidenceUnavailable):
        return None

    data = fetched.payload or {}
    facts = RepoFacts(
        full_name=str(data.get("full_name") or repo),
        html_url=str(data.get("html_url") or f"https://github.com/{repo}"),
        archived=bool(data.get("archived")),
        pushed_at=parse_datetime(data.get("pushed_at")),
        open_issues=_as_int(data.get("open_issues_count")),
        stars=_as_int(data.get("stargazers_count")),
        default_branch=data.get("default_branch"),
        fetched=fetched,
    )

    since = moment - timedelta(days=365)
    commits_ok, commits = _commits_since(client, facts.full_name, since, pages=pages)
    if commits_ok:
        bots = {author for author, _, _ in commits if _BOT_RE.search(author)}
        humans = [c for c in commits if c[0] not in bots]
        facts.commits_12mo = len(humans)
        facts.committers = _committers(humans)
        if facts.committers and len(humans):
            counts = Counter(c[0] for c in humans)
            top = max(counts.values())
            facts.top_share = round(top / len(humans), 4)
        if bots:
            facts.gaps.append(
                f"commits: {len(bots)} bot account(s) excluded from bus-factor counting"
            )
    else:
        facts.gaps.append("commits: commit history could not be read")

    if include_triage:
        budget = client.budget(f"{API}/search/issues")
        if budget is not None and budget < SEARCH_BUDGET_FLOOR:
            facts.gaps.append(
                "triage: GitHub search quota exhausted this run; issue counts not fetched"
            )
        else:
            created, closed = _issue_counts(client, facts.full_name, since)
            facts.issues_created_12mo = created
            facts.issues_closed_12mo = closed
            if created is not None and closed is not None:
                facts.triage_rate = round(closed / created, 4) if created else None
            else:
                facts.gaps.append("triage: issue search did not answer")

    if include_code_search:
        search_url = (
            f"{API}/search/code?q={_quote(f'repo:{facts.full_name}')}&per_page=1"
        )
        try:
            search = client.get_json(search_url, ttl_seconds=None)
            facts.code_search_count = _as_int((search.payload or {}).get("total_count"))
        except (NotFound, SourceUnavailable, EvidenceUnavailable):
            facts.gaps.append("usage: code search did not answer")

    return facts


def attach_repo_facts(evidence: PackageEvidence, facts: RepoFacts | None) -> None:
    """Copy a :class:`RepoFacts` onto the evidence object, with citations."""
    if facts is None:
        evidence.add_gap("forge: no readable public repository")
        return
    cited = facts.fetched
    retrieved = cited.fetched_at if cited else utcnow()
    repo_url = facts.html_url or cited.url if cited else facts.html_url
    evidence.repo = facts.full_name
    evidence.repo_url = facts.html_url
    evidence.repo_archived = facts.archived
    evidence.forge_ok = True

    evidence.commits_12mo_obs = obs(
        facts.commits_12mo,
        source="github",
        url=f"{API}/repos/{facts.full_name}/commits",
        retrieved_at=retrieved,
        detail="non-bot commits in the 365 days before retrieval",
        method="paged commit list, bot authors excluded",
    )
    if facts.committers:
        evidence.committers = facts.committers
        evidence.committers_12mo_obs = obs(
            len(facts.committers),
            source="github",
            url=f"{API}/repos/{facts.full_name}/commits",
            retrieved_at=retrieved,
            detail="distinct non-bot commit authors in the 365 days before retrieval",
            method="distinct commit.author over the commit list",
        )
        lead = facts.committers[0]
        evidence.top_committer_share_obs = obs(
            facts.top_share,
            source="github",
            url=f"{API}/repos/{facts.full_name}/commits",
            retrieved_at=retrieved,
            detail=f"largest share of commits by one author ({lead.name})",
            method="max(commits by author) / total commits",
        )
        evidence.last_commit_by_author_obs = obs(
            lead.name,
            source="github",
            url=lead.url or f"{API}/repos/{facts.full_name}/commits",
            retrieved_at=retrieved,
            detail=(
                f"author of {lead.commits} commit(s); most recent commit {iso(lead.last_commit_at)} "
                f"(sha {lead.last_commit_sha[:12]})"
                if lead.last_commit_at and lead.last_commit_sha
                else None
            ),
        )
    else:
        evidence.committers_12mo_obs = obs(
            None,
            source="github",
            url=f"{API}/repos/{facts.full_name}/commits",
            retrieved_at=retrieved,
            detail="no non-bot commits in the last 365 days",
        )

    if facts.pushed_at is not None:
        evidence.last_commit_obs = obs(
            iso(facts.pushed_at),
            source="github",
            url=repo_url or "",
            retrieved_at=retrieved,
            detail="repository pushed_at (any branch)",
            method="repos.pushed_at",
        )
    if facts.issues_created_12mo is not None:
        evidence.issue_created_12mo_obs = obs(
            facts.issues_created_12mo,
            source="github",
            url=f"{API}/search/issues?q=repo:{facts.full_name}+type:issue",
            retrieved_at=retrieved,
            detail="issues created in the 365 days before retrieval",
            method="search/issues total_count",
        )
    if facts.issues_closed_12mo is not None:
        evidence.issue_closed_12mo_obs = obs(
            facts.issues_closed_12mo,
            source="github",
            url=f"{API}/search/issues?q=repo:{facts.full_name}+type:issue+is:closed",
            retrieved_at=retrieved,
            detail="issues created in the window that are now closed",
            method="search/issues total_count",
        )
    if facts.triage_rate is not None:
        evidence.triage_rate_obs = obs(
            facts.triage_rate,
            source="github",
            url=f"{API}/search/issues?q=repo:{facts.full_name}+type:issue",
            retrieved_at=retrieved,
            detail="share of last year's issues already closed",
            method="closed / created",
        )
    evidence.open_issues_obs = obs(
        facts.open_issues,
        source="github",
        url=repo_url or "",
        retrieved_at=retrieved,
        detail="repositories.open_issues_count (includes pull requests)",
        method="repos.open_issues_count",
    )
    for gap in facts.gaps:
        evidence.add_gap(gap)


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------


def _commits_since(
    client: CachingClient, full_name: str, since: datetime, *, pages: int
) -> tuple[bool, list[tuple[str, datetime, str]]]:
    """Walk commit pages backwards to ``since``.

    Returns ``(complete, [(author, committed_at, sha), ...])``.  ``complete`` is
    ``False`` if any page failed, which makes every derived number unknown.
    """
    collected: list[tuple[str, datetime, str]] = []
    url = (
        f"{API}/repos/{full_name}/commits?since={since.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        f"&per_page={PER_PAGE}"
    )
    seen_pages = 0
    while url and seen_pages < pages:
        try:
            fetched = client.get_json(url, ttl_seconds=None)
        except (NotFound, SourceUnavailable, EvidenceUnavailable):
            return False, collected
        seen_pages += 1
        payload = fetched.payload
        if not isinstance(payload, list):
            return False, collected
        if not payload:
            return True, collected
        oldest_on_page: datetime | None = None
        for entry in payload:
            if not isinstance(entry, dict):
                continue
            commit = entry.get("commit") or {}
            author_block = commit.get("author") or {}
            when = parse_datetime(author_block.get("date"))
            login = _author_identity(entry, author_block)
            if when is None or not login:
                continue
            collected.append((login, when, str(entry.get("sha") or "")))
            if oldest_on_page is None or when < oldest_on_page:
                oldest_on_page = when
        if len(payload) < PER_PAGE:
            return True, collected
        if oldest_on_page is not None and oldest_on_page <= since:
            return True, collected
        next_url = _next_link(fetched)
        if not next_url:
            return True, collected
        url = next_url
    if url and seen_pages >= pages:
        # Truncated history: refuse to publish a partial bus factor.
        return False, collected
    return True, collected


def _author_identity(entry: dict[str, Any], author_block: dict[str, Any]) -> str | None:
    """Prefer the GitHub login; fall back to the commit's author name."""
    user = entry.get("author") or {}
    if isinstance(user, dict) and user.get("login"):
        return str(user["login"])
    name = author_block.get("name")
    if name:
        return f"{name} <{author_block.get('email') or 'unknown'}>"
    return None


def _committers(humans: list[tuple[str, datetime, str]]) -> list[Maintainer]:
    by_author: dict[str, list[tuple[datetime, str]]] = {}
    for author, when, sha in humans:
        by_author.setdefault(author, []).append((when, sha))
    out: list[Maintainer] = []
    for author, entries in by_author.items():
        entries.sort(key=lambda pair: pair[0])
        latest_at, latest_sha = entries[-1]
        out.append(
            Maintainer(
                name=author,
                role="committer",
                url=f"https://github.com/{author}" if "/" not in author and "<" not in author else None,
                last_commit_sha=latest_sha or None,
                last_commit_at=latest_at,
                commits=len(entries),
            )
        )
    out.sort(key=lambda m: (-(m.commits or 0), m.last_commit_at or utcnow(), m.name))
    return out


def _issue_counts(
    client: CachingClient, full_name: str, since: datetime
) -> tuple[int | None, int | None]:
    stamp = since.strftime("%Y-%m-%d")
    base = f"repo:{full_name}+type:issue+created:>={stamp}"
    created = _search_count(client, f"{API}/search/issues?q={base}")
    closed = _search_count(client, f"{API}/search/issues?q={base}+is:closed")
    return created, closed


def _search_count(client: CachingClient, url: str) -> int | None:
    try:
        fetched = client.get_json(url, ttl_seconds=None, accept="application/vnd.github+json")
    except (NotFound, SourceUnavailable, EvidenceUnavailable):
        return None
    if not fetched.from_cache:
        client.consume(url)
    return _as_int((fetched.payload or {}).get("total_count"))


def _next_link(fetched: Fetched) -> str | None:
    header = fetched.headers.get("link") or ""
    for part in header.split(","):
        if 'rel="next"' in part:
            match = re.search(r"<([^>]+)>", part)
            if match:
                next_url = match.group(1)
                # The Link header points at /repositories/<id>/commits; use it
                # verbatim (it is already paginated for us).
                return next_url
    return None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _quote(text: str) -> str:
    from urllib.parse import quote_plus

    return quote_plus(text)
