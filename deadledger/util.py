"""Small, pure helpers shared by adapters and the mortality engine.

Nothing in here does I/O.  Everything is deterministic given its arguments,
which is what makes the determinism tests in ``tests/test_determinism.py``
possible.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from functools import cmp_to_key
from typing import Any, Iterable, Sequence

UTC = timezone.utc

# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------


def utcnow() -> datetime:
    """Now, in UTC, truncated to the second (stable for tests via freeze_time)."""
    return datetime.now(UTC).replace(microsecond=0)


def parse_datetime(value: Any) -> datetime | None:
    """Parse the handful of timestamp shapes registries emit.

    Accepts ISO-8601 with ``Z`` or offsets, ``YYYY-MM-DDTHH:MM:SS`` without a
    zone (assumed UTC), and ``YYYY-MM-DD``.  Returns ``None`` for junk rather
    than raising: a single unparseable date must not sink an audit.
    """
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue
            else:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def days_between(earlier: datetime, later: datetime) -> int:
    """Whole days from *earlier* to *later* (negative if *earlier* is later)."""
    return (later - earlier) // timedelta(days=1)


def iso(dt: datetime | None) -> str | None:
    """Render a UTC datetime the way the report does: ``2023-06-01T00:00:00Z``."""
    if dt is None:
        return None
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_day(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(UTC).strftime("%Y-%m-%d")


def age_in_days(when: datetime | None, now: datetime) -> int | None:
    if when is None:
        return None
    return max(0, days_between(when, now))


def human_age(days: int | None) -> str:
    """``820`` -> ``'2.2y'``.  Used in prose so verdicts read like English."""
    if days is None:
        return "unknown"
    if days < 45:
        return f"{days}d"
    if days < 730:
        return f"{days / 30.44:.1f}mo"
    return f"{days / 365.25:.1f}y"


def human_int(n: float | None) -> str:
    if n is None:
        return "unknown"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(int(n))


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+]([0-9A-Za-z.\-+]+))?$")
_PRERELEASE_WORDS = re.compile(
    r"(a|b|rc|alpha|beta|pre|preview|dev|snapshot|nightly|canary|next|insiders?)\d*$",
    re.IGNORECASE,
)


def version_sort_key(version: str) -> tuple:
    """A total ordering over version strings that is *good enough* everywhere.

    We do not try to be PEP 440 or semver-exact (PEP 440 parsing lives in
    ``packaging``, which is not a dependency).  We need a stable, deterministic
    order to (a) find "the latest" release and (b) measure gaps between it and
    a project's current pin, so a numeric-tuple-with-suffix-tiebreak order is
    the right trade-off.  Prereleases sort *before* their release.
    """
    text = str(version).strip()
    m = _SEMVER_RE.match(text)
    if m:
        major, minor, patch, suffix = m.groups()
        pre = 0 if suffix else 1
        return (1, int(major), int(minor), int(patch), pre, suffix or "")
    parts: list[tuple[int, int, str]] = []
    for chunk in re.split(r"[._\-+]", text.lstrip("vV")):
        if not chunk:
            continue
        for piece in re.findall(r"\d+|\D+", chunk):
            if piece.isdigit():
                parts.append((1, int(piece), ""))
            else:
                parts.append((0, 0, piece.lower()))
    return (0, str(text).lower(), parts)


def compare_versions(a: str, b: str) -> int:
    """Comparator form (``-1/0/1``) so we can sort with :func:`cmp_to_key`."""
    key_a, key_b = version_sort_key(a), version_sort_key(b)
    return (key_a > key_b) - (key_a < key_b)


def sort_versions(versions: Iterable[str]) -> list[str]:
    return sorted(versions, key=cmp_to_key(compare_versions))


def major_of(version: str) -> int | None:
    """Major version number, or ``None`` if the string hides it."""
    for piece in re.split(r"[._\-+]", str(version).strip().lstrip("vV")):
        if piece.isdigit():
            return int(piece)
        m = re.match(r"(\d+)", piece)
        if m:
            return int(m.group(1))
        break
    return None


def is_prerelease(version: str) -> bool:
    text = str(version).strip().lstrip("vV")
    if re.search(r"[-+](a|b|rc|alpha|beta|pre|dev|nightly|canary)", text, re.I):
        return True
    return bool(_PRERELEASE_WORDS.search(text))


# ---------------------------------------------------------------------------
# URLs and repo identity
# ---------------------------------------------------------------------------

_GITHUB_URL_RE = re.compile(
    r"(?:https?://|git\+https?://|git://|ssh://git@|git@|www\.)?"
    r"(?:www\.)?github\.com[/:](?P<owner>[A-Za-z0-9_.\-]+)/(?P<repo>[A-Za-z0-9_.\-]+)",
    re.IGNORECASE,
)


def parse_github_repo(*candidates: Any) -> str | None:
    """Extract ``owner/name`` from any of the URL-ish fields a registry offers.

    Registries store the same fact in wildly different shapes::

        https://github.com/psf/requests
        git+https://github.com/psf/requests.git
        git+ssh://git@github.com/psf/requests.git#egg=requests
        {'type': 'git', 'url': 'git://github.com/psf/requests.git'}
        'requests/requests'

    Returns ``"owner/name"`` (case preserved) or ``None``.  Only GitHub is
    parsed: it is the forge we can interrogate anonymously at scale.
    """
    for candidate in candidates:
        if not candidate:
            continue
        if isinstance(candidate, dict):
            inner = candidate.get("url") or candidate.get("browse") or ""
            found = parse_github_repo(inner)
            if found:
                return found
            continue
        text = str(candidate).strip()
        if not text:
            continue
        if re.fullmatch(r"[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+", text):
            return text
        m = _GITHUB_URL_RE.search(text)
        if m:
            owner = m.group("owner")
            repo = m.group("repo")
            if repo.endswith(".git"):
                repo = repo[:-4]
            if owner.lower() in {"github.com", "www"}:
                continue
            if owner and repo and repo not in {".", ".."}:
                return f"{owner}/{repo}"
    return None


def strip_html(value: Any) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


# ---------------------------------------------------------------------------
# Statistics used by the rubric
# ---------------------------------------------------------------------------


def median(values: Sequence[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def linear_slope(points: Sequence[tuple[float, float]]) -> float | None:
    """Least-squares slope of y on x.  ``None`` when under-determined."""
    n = len(points)
    if n < 2:
        return None
    mean_x = sum(p[0] for p in points) / n
    mean_y = sum(p[1] for p in points) / n
    denom = sum((p[0] - mean_x) ** 2 for p in points)
    if denom == 0:
        return None
    numer = sum((p[0] - mean_x) * (p[1] - mean_y) for p in points)
    return numer / denom


def round_sig(value: float | None, digits: int = 3) -> float | None:
    """Round to *digits* significant figures, keeping reports tidy.

    Determinism matters more than precision here: the same inputs must format
    to the same string forever, so we never let float repr leak into output.
    """
    if value is None:
        return None
    if value == 0:
        return 0.0
    from math import floor, log10

    exponent = floor(log10(abs(value)))
    factor = 10 ** (digits - 1 - exponent)
    return round(value * factor) / factor


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def slugify(text: str, max_length: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return (slug or "report")[:max_length].strip("-")


def json_dumps_stable(value: Any) -> str:
    """Canonical JSON: sorted keys, no insignificant whitespace.

    Used to fingerprint inputs so ``deadledger audit`` can tell you, byte for
    byte, whether anything in the underlying evidence changed.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def chunked(items: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]
