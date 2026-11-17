"""The alternatives map (Requirement 5).

For a dead or dormant critical dependency, the report answers "what do I move
to, and how much work is that?"  Two halves:

1. **Where the data lives.**  ``maps/alternatives.json`` in the repository is
   the community-curated asset (versioned, reviewed, forkable).  At runtime we
   layer three sources, closest first: an explicit ``--map`` path, the user's
   ``~/.config/deadledger/alternatives.json``, then the shipped default.  A
   package found in a closer layer wins entirely, so a team can override the
   community answer locally without forking it.
2. **How the cost is estimated.**  ``api_diff`` is a rough, explainable
   proxy: symbol-level overlap between the old and new package's public API,
   measured from the runtimes' own metadata (``__all__`` when a source
   distribution ships one, otherwise exported top-level names).  We do *not*
   pretend it is a real refactoring estimate; it is a pointer that says
   "these are near drop-ins" versus "this is a rewrite".  Every entry states
   its basis, and unmeasured entries say ``unknown`` rather than guessing.

The map ships with a ``_meta`` block carrying a version string.  Reports quote
that version so a reader can see exactly which map produced the advice.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

MAP_VERSION = "1.0.0"
MAP_FILENAME = "alternatives.json"


@dataclass
class Alternative:
    name: str
    ecosystem: str
    reason: str
    migration: str = "moderate"     # 'drop-in' | 'minor' | 'moderate' | 'rewrite'
    api_diff: float | None = None   # 0..1, share of the old API the new one covers
    basis: str = ""                 # how api_diff was obtained
    notes: str = ""
    links: list[str] = field(default_factory=list)
    deprecated_original: bool = False

    @property
    def cost_label(self) -> str:
        if self.api_diff is None:
            return self.migration
        covered = round(self.api_diff * 100)
        if covered >= 90:
            return f"near drop-in ({covered}% of measured API covered)"
        if covered >= 60:
            return f"moderate ({covered}% of measured API covered)"
        if covered >= 30:
            return f"significant ({covered}% of measured API covered)"
        return f"rewrite-shaped ({covered}% of measured API covered)"

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ecosystem": self.ecosystem,
            "reason": self.reason,
            "migration": self.migration,
            "cost": self.cost_label,
            "api_diff": self.api_diff,
            "basis": self.basis,
            "notes": self.notes,
            "links": self.links,
        }


@dataclass
class AlternativeMap:
    version: str
    updated_at: str | None
    entries: dict[tuple[str, str], list[Alternative]]
    source: str
    warnings: list[str] = field(default_factory=list)

    def lookup(self, ecosystem: str, name: str) -> list[Alternative]:
        return self.entries.get((ecosystem, normalise(name)), [])

    def describe(self) -> str:
        return f"alternatives map v{self.version} ({self.source})"


def normalise(name: str) -> str:
    import re

    return re.sub(r"[-_.]+", "-", str(name).strip().lower())


class _NotFound(Exception):
    pass


def default_map_path() -> Path | None:
    """Locate the shipped map in both layouts: source checkout and wheel."""
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / "maps" / MAP_FILENAME,
        here / "data" / MAP_FILENAME,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def user_map_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "deadledger" / MAP_FILENAME


def load_map(
    *, explicit: str | Path | None = None, include_user: bool = True
) -> AlternativeMap:
    """Load the closest map that exists, reporting which one was used."""
    layers: list[tuple[str, Path]] = []
    if include_user:
        layers.append(("user", user_map_path()))
    if explicit:
        layers.append(("explicit", Path(explicit).expanduser()))
    else:
        shipped = default_map_path()
        if shipped:
            layers.append(("shipped", shipped))

    chosen: tuple[str, Path, dict[str, Any]] | None = None
    for label, path in layers:
        if not path.is_file():
            if label in {"explicit"}:
                raise FileNotFoundError(f"alternatives map not found: {path}")
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        chosen = (label, path, document)
        if label == "user" or label == "explicit":
            break
    if chosen is None:
        return AlternativeMap(version="none", updated_at=None, entries={}, source="none")

    label, path, document = chosen
    entries: dict[tuple[str, str], list[Alternative]] = {}
    warnings: list[str] = []
    for raw in document.get("entries") or []:
        ecosystem = str(raw.get("ecosystem") or "").lower()
        package = normalise(str(raw.get("package") or ""))
        if not ecosystem or not package:
            warnings.append(f"map entry without ecosystem/package skipped: {raw!r}")
            continue
        alternatives = [
            Alternative(
                name=str(item.get("name") or ""),
                ecosystem=ecosystem,
                reason=str(item.get("reason") or ""),
                migration=str(item.get("migration") or "moderate"),
                api_diff=_float_or_none(item.get("api_diff")),
                basis=str(item.get("basis") or ""),
                notes=str(item.get("notes") or ""),
                links=[str(link) for link in item.get("links") or []],
            )
            for item in raw.get("alternatives") or []
            if item.get("name")
        ]
        entries[(ecosystem, package)] = alternatives

    meta = document.get("_meta") or {}
    return AlternativeMap(
        version=str(meta.get("version") or MAP_VERSION),
        updated_at=meta.get("updated_at"),
        entries=entries,
        source=str(path),
        warnings=warnings,
    )


def _float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, number))


def estimate_api_diff(
    old: dict[str, Any], new: dict[str, Any]
) -> tuple[float | None, str]:
    """How much of *old*'s measured API does *new* appear to cover?

    ``old`` and ``new`` are ``{'names': set[str]}`` blobs extracted from package
    metadata by :func:`api_surface`.  Returns ``(fraction, basis)`` and is
    intentionally conservative: with nothing to compare we return ``None`` and
    say why, because a fabricated 0.5 would be worse than an honest "unknown".
    """
    old_names = {str(n) for n in old.get("names") or ()}
    new_names = {str(n) for n in new.get("names") or ()}
    if not old_names or not new_names:
        return None, "no comparable API surface extracted"
    overlap = old_names & new_names
    return round(len(overlap) / len(old_names), 3), (
        f"{len(overlap)} of {len(old_names)} public names in {old.get('package') or 'old'} "
        f"also appear in {new.get('package') or 'new'}"
    )


def api_surface(metadata: dict[str, Any]) -> dict[str, Any]:
    """Extract a comparable "public API surface" from registry metadata.

    Priority order, because each is a weaker signal than the last:

    1. an explicit ``api_surface`` list recorded by whoever measured it;
    2. ``__all__`` shipped in ``*.dist-info/top_level.txt``-adjacent metadata
       (rare on registries, which is why the map stores measured surfaces);
    3. the set of top-level modules (``top_level``), which at least tells you
       whether the *shape* of the import is preserved.

    Anything we cannot see is simply absent from the set; the caller decides
    whether the comparison is meaningful.
    """
    if isinstance(metadata.get("api_surface"), (list, tuple, set)):
        return {"package": metadata.get("package"), "names": set(metadata["api_surface"])}
    if isinstance(metadata.get("top_level"), (list, tuple, set)):
        return {"package": metadata.get("package"), "names": set(metadata["top_level"])}
    return {"package": metadata.get("package"), "names": set()}


def annotate(
    map_object: AlternativeMap,
    ecosystem: str,
    name: str,
    *,
    measured_surfaces: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Look up alternatives and attach computed costs where possible."""
    rows = []
    for alternative in map_object.lookup(ecosystem, name):
        if alternative.api_diff is None and measured_surfaces:
            old = measured_surfaces.get(normalise(name)) or {}
            new = measured_surfaces.get(normalise(alternative.name)) or {}
            fraction, basis = estimate_api_diff(old, new)
            if fraction is not None:
                alternative.api_diff = fraction
                alternative.basis = basis
        rows.append(alternative.as_dict())
    return rows


def validate(document: dict[str, Any]) -> list[str]:
    """Lint a map file.  Used by ``deadledger map lint`` and the test suite."""
    problems: list[str] = []
    if not isinstance(document, dict):
        return ["map must be a JSON object"]
    meta = document.get("_meta")
    if not isinstance(meta, dict) or not meta.get("version"):
        problems.append("missing _meta.version")
    if not meta.get("updated_at"):
        problems.append("missing _meta.updated_at")
    entries = document.get("entries")
    if not isinstance(entries, list) or not entries:
        return problems + ["entries must be a non-empty list"]
    allowed_ecosystems = {"pypi", "npm", "crates"}
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        where = f"entries[{index}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: not an object")
            continue
        ecosystem = str(entry.get("ecosystem") or "").lower()
        package = entry.get("package")
        if ecosystem not in allowed_ecosystems:
            problems.append(f"{where}: ecosystem {ecosystem!r} not in {sorted(allowed_ecosystems)}")
        if not package:
            problems.append(f"{where}: missing package")
            continue
        key = (ecosystem, normalise(str(package)))
        if key in seen:
            problems.append(f"{where}: duplicate entry for {ecosystem}:{package}")
        seen.add(key)
        alternatives = entry.get("alternatives")
        if not isinstance(alternatives, list) or not alternatives:
            problems.append(f"{where}: needs at least one alternative")
            continue
        for jndex, alternative in enumerate(alternatives):
            spot = f"{where}.alternatives[{jndex}]"
            if not isinstance(alternative, dict) or not alternative.get("name"):
                problems.append(f"{spot}: missing name")
                continue
            diff = alternative.get("api_diff")
            if diff is not None:
                try:
                    value = float(diff)
                except (TypeError, ValueError):
                    problems.append(f"{spot}: api_diff is not a number")
                    continue
                if not 0 <= value <= 1:
                    problems.append(f"{spot}: api_diff must be within [0, 1]")
                if not alternative.get("basis"):
                    problems.append(f"{spot}: api_diff needs a basis string")
            if alternative.get("migration") not in {
                None,
                "drop-in",
                "minor",
                "moderate",
                "rewrite",
            }:
                problems.append(f"{spot}: unknown migration label")
            if not alternative.get("reason"):
                problems.append(f"{spot}: needs a reason (the report prints it)")
    return problems


def iter_entries(map_object: AlternativeMap) -> Iterable[tuple[str, str, list[Alternative]]]:
    for (ecosystem, package), alternatives in sorted(map_object.entries.items()):
        yield ecosystem, package, alternatives
