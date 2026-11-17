"""The local-first store: a single SQLite file holding HTTP responses (with
TTLs) and DeadLedger's own ledger state.

Two design rules, both load-bearing:

1. **The cache is the archive.**  A report must cite *when* a fact was
   retrieved, so the cache stores the retrieval timestamp with the body and
   the report quotes that, not "now".  Re-running an audit offline reproduces
   the same retrieved-at dates and therefore the same citations.
2. **Your tree never leaves your machine.**  Nothing stored here is keyed by
   the project being audited; the only keys are public URLs and the ledger's
   own bookkeeping.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .util import json_dumps_stable, parse_datetime, utcnow

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS http_cache (
    key          TEXT PRIMARY KEY,
    kind         TEXT NOT NULL,
    url          TEXT NOT NULL,
    query        TEXT NOT NULL DEFAULT '',
    status       INTEGER NOT NULL DEFAULT 200,
    fetched_at   TEXT NOT NULL,
    ttl_seconds  INTEGER NOT NULL,
    expires_at   TEXT NOT NULL,
    payload      TEXT NOT NULL,
    etag         TEXT,
    headers      TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS http_cache_expires ON http_cache(expires_at);

CREATE TABLE IF NOT EXISTS kv (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

DEFAULT_DIR = ".deadledger"
DEFAULT_DB_NAME = "cache.sqlite"


def _json_dict(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:  # pragma: no cover
        return {}
    return {str(k): str(v) for k, v in value.items()} if isinstance(value, dict) else {}


def default_db_path() -> Path:
    """Where the cache lives when the user does not say otherwise.

    ``DEADLEDGER_HOME`` wins, then the XDG data dir, then ``.deadledger/`` in
    the current directory.  A local directory keeps the "works offline from
    the cache you already have" story obvious.
    """
    env = os.environ.get("DEADLEDGER_HOME")
    if env:
        return Path(env).expanduser() / DEFAULT_DB_NAME
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg and Path(xdg).is_dir():
        return Path(xdg) / "deadledger" / DEFAULT_DB_NAME
    return Path.cwd() / DEFAULT_DIR / DEFAULT_DB_NAME


@dataclass(frozen=True)
class CacheEntry:
    key: str
    kind: str
    url: str
    status: int
    fetched_at: datetime
    ttl_seconds: int
    expires_at: datetime
    payload: Any
    etag: str | None = None
    query: str = ""
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def expired(self) -> bool:
        return self.expires_at <= utcnow()

    @property
    def age_seconds(self) -> int:
        return max(0, int((utcnow() - self.fetched_at).total_seconds()))


class Cache:
    """Thin, boring wrapper over SQLite.  No ORM, no magic, no threads."""

    def __init__(self, path: str | Path | None = None, *, create: bool = True):
        self.path = Path(path) if path is not None else default_db_path()
        if str(self.path) != ":memory:":
            if not create and not self.path.exists():
                raise FileNotFoundError(
                    f"no cache at {self.path}; run deadledger online first "
                    f"(or drop --offline) to build it"
                )
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), timeout=30)
        self._conn.row_factory = sqlite3.Row
        if str(self.path) != ":memory:":
            try:
                self._conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.DatabaseError:  # pragma: no cover - exotic FS
                pass
        self._conn.execute("PRAGMA busy_timeout=15000")
        self._conn.executescript(_SCHEMA)
        self._migrate()
        self._conn.execute(
            "INSERT OR IGNORE INTO schema_meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        self._conn.commit()

    def _migrate(self) -> None:
        """Add columns introduced after a cache file was first created."""
        columns = {
            row["name"]
            for row in self._conn.execute("PRAGMA table_info(http_cache)").fetchall()
        }
        if "headers" not in columns:
            self._conn.execute(
                "ALTER TABLE http_cache ADD COLUMN headers TEXT NOT NULL DEFAULT '{}'"
            )
            self._conn.commit()
        # Rate-limit headers describe the moment of retrieval, not the present.
        # Replaying them ("remaining: 0") would make a later run believe the
        # quota is still spent, so any cache written before this fix is scrubbed.
        self._conn.execute(
            "UPDATE http_cache SET headers = json_remove(headers, "
            "'$.x-ratelimit-remaining', '$.x-ratelimit-reset') "
            "WHERE headers LIKE '%x-ratelimit%'"
        )
        self._conn.commit()

    # -- HTTP response cache ------------------------------------------------

    def get(self, key: str) -> CacheEntry | None:
        row = self._conn.execute("SELECT * FROM http_cache WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        fetched_at = parse_datetime(row["fetched_at"]) or utcnow()
        expires_at = parse_datetime(row["expires_at"]) or fetched_at
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:  # pragma: no cover - corrupt row
            return None
        return CacheEntry(
            key=row["key"],
            kind=row["kind"],
            url=row["url"],
            status=row["status"],
            fetched_at=fetched_at,
            ttl_seconds=row["ttl_seconds"],
            expires_at=expires_at,
            payload=payload,
            etag=row["etag"],
            query=row["query"],
            headers=_json_dict(row["headers"]),
        )

    def put(
        self,
        key: str,
        *,
        kind: str,
        url: str,
        payload: Any,
        ttl_seconds: int,
        status: int = 200,
        etag: str | None = None,
        query: str = "",
        fetched_at: datetime | None = None,
        headers: dict[str, str] | None = None,
    ) -> CacheEntry:
        when = fetched_at or utcnow()
        expires = when + timedelta(seconds=max(0, ttl_seconds))
        body = json_dumps_stable(payload)
        self._conn.execute(
            """
            INSERT INTO http_cache (key, kind, url, query, status, fetched_at,
                                    ttl_seconds, expires_at, payload, etag, headers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                kind=excluded.kind, url=excluded.url, query=excluded.query,
                status=excluded.status, fetched_at=excluded.fetched_at,
                ttl_seconds=excluded.ttl_seconds, expires_at=excluded.expires_at,
                payload=excluded.payload, etag=excluded.etag,
                headers=excluded.headers
            """,
            (
                key,
                kind,
                url,
                query,
                status,
                when.strftime("%Y-%m-%dT%H:%M:%SZ"),
                int(ttl_seconds),
                expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
                body,
                etag,
                json_dumps_stable(headers or {}),
            ),
        )
        self._conn.commit()
        return CacheEntry(
            key=key,
            kind=kind,
            url=url,
            status=status,
            fetched_at=when,
            ttl_seconds=int(ttl_seconds),
            expires_at=expires,
            payload=payload,
            etag=etag,
            query=query,
            headers=dict(headers or {}),
        )

    def delete(self, key: str) -> None:
        self._conn.execute("DELETE FROM http_cache WHERE key = ?", (key,))
        self._conn.commit()

    def purge_expired(self) -> int:
        now = utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        cur = self._conn.execute("DELETE FROM http_cache WHERE expires_at <= ?", (now,))
        self._conn.commit()
        return cur.rowcount

    def newest_fetched_at(self) -> datetime | None:
        """The most recent retrieval stored, or ``None`` for an empty cache.

        Replay mode uses this as its clock: the fixtures' own ``recorded_at``
        values are replayed into the in-memory cache, so the audit runs against
        the instant the world was recorded rather than the instant the test
        happens to run.
        """
        row = self._conn.execute("SELECT MAX(fetched_at) AS newest FROM http_cache").fetchone()
        return parse_datetime(row["newest"]) if row and row["newest"] else None

    def stats(self) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT COUNT(*) AS n, MIN(fetched_at) AS oldest, MAX(fetched_at) AS newest, "
            "SUM(LENGTH(payload)) AS bytes FROM http_cache"
        ).fetchone()
        by_kind = {
            r["kind"]: r["n"]
            for r in self._conn.execute(
                "SELECT kind, COUNT(*) AS n FROM http_cache GROUP BY kind ORDER BY kind"
            )
        }
        now = utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        fresh = self._conn.execute(
            "SELECT COUNT(*) AS n FROM http_cache WHERE expires_at > ?", (now,)
        ).fetchone()["n"]
        return {
            "path": str(self.path),
            "entries": row["n"] or 0,
            "fresh": fresh,
            "expired": (row["n"] or 0) - fresh,
            "bytes": row["bytes"] or 0,
            "oldest": row["oldest"],
            "newest": row["newest"],
            "by_kind": by_kind,
        }

    # -- Ledger bookkeeping -------------------------------------------------

    def kv_get(self, key: str) -> Any | None:
        row = self._conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:  # pragma: no cover
            return None

    def kv_put(self, key: str, value: Any) -> None:
        self._conn.execute(
            """INSERT INTO kv (key, value, updated_at) VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                                              updated_at=excluded.updated_at""",
            (key, json_dumps_stable(value), utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")),
        )
        self._conn.commit()

    # -- housekeeping -------------------------------------------------------

    def close(self) -> None:
        try:
            self._conn.close()
        except sqlite3.Error:  # pragma: no cover
            pass

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
