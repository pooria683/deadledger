"""Lockfile parsing: turn six formats into one graph.

The graph is the whole point.  Version 1 of the rubric wanted to answer
"how deep is this problem?" and a flat list of pins cannot do that, so every
parser here produces :class:`Inventory` -- a set of nodes plus the edges that
actually exist in the lockfile, not edges inferred from the registry later.

Supported, in the order :func:`detect_lockfile` prefers them (a project often
has several, and the most constrained one wins):

======================  ==========================================
poetry.lock             TOML, `[[package]]` with `category`/`groups`
uv.lock                 TOML, PEP 751-ish `[[package]]`
Pipfile.lock            JSON, `default` vs `develop`
package-lock.json       JSON, `packages` (v2/v3) or `dependencies` (v1)
Cargo.lock              TOML, `[[package]]` + `dependencies`
requirements.txt        pins, optionally with `# via` (pip-compile)
yarn.lock               (detected, and we say we cannot build edges)
======================  ==========================================
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .errors import NoLockfile

#: Names that are pinned in the lockfile but are almost never "maintenance
#: risks" for your project: test runners, linters, type stubs, build tools.
#: Dev-only dependencies are collected but excluded from criticality by default.
DEV_NAME_HINTS = re.compile(
    r"(^|[-_.])(pytest|pytest-.+|hypothesis|coverage|mypy|ruff|black|flake8|pylint|"
    r"isort|tox|nox|pre-commit|sphinx|mkdocs|twine|build|wheel|setuptools|pip|"
    r"virtualenv|pyinstaller|faker|freezegun|responses|pytest-cov)($|[-_.])",
    re.I,
)


@dataclass
class Node:
    """One installed package instance."""

    ecosystem: str
    name: str
    version: str | None
    key: str
    dev: bool = False
    source: str = "lockfile"  # lockfile path, for the report's provenance line
    extras: tuple[str, ...] = ()
    declared_by_project: bool = False


@dataclass
class Edge:
    """``parent`` requires ``child``.  ``parent=None`` means the project itself."""

    parent: str | None
    child: str
    depth_hint: str = ""  # e.g. '==2.31.0' or '^1.2' -- kept for prose only


@dataclass
class Inventory:
    ecosystem: str
    lockfile: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    direct: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)
    project_name: str | None = None

    def add(self, node: Node) -> None:
        self.nodes[node.key] = node

    def add_edge(self, parent: str | None, child: str, hint: str = "") -> None:
        self.edges.append(Edge(parent=parent, child=child, depth_hint=hint))

    def children(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for edge in self.edges:
            if edge.parent is None:
                continue
            out.setdefault(edge.parent, set()).add(edge.child)
        return out

    def direct_nodes(self) -> list[Node]:
        return [self.nodes[key] for key in self.direct if key in self.nodes]

    def transitive_nodes(self) -> list[Node]:
        return [n for k, n in self.nodes.items() if k not in self.direct]


# ---------------------------------------------------------------------------
# Lockfile detection
# ---------------------------------------------------------------------------

#: Ordered by specificity.  A repo with both requirements.txt and poetry.lock
#: should be audited against poetry.lock: it is the resolved truth.
LOCKFILE_ORDER = (
    ("poetry.lock", "pypi", "poetry"),
    ("uv.lock", "pypi", "uv"),
    ("pdm.lock", "pypi", "pdm"),
    ("Pipfile.lock", "pypi", "pipenv"),
    ("package-lock.json", "npm", "npm"),
    ("npm-shrinkwrap.json", "npm", "npm"),
    ("pnpm-lock.yaml", "npm", "pnpm"),
    ("yarn.lock", "npm", "yarn"),
    ("Cargo.lock", "crates", "cargo"),
    ("requirements.txt", "pypi", "pip"),
    ("requirements-dev.txt", "pypi", "pip"),
    ("constraints.txt", "pypi", "pip"),
)

LOCKFILE_NAMES = {name for name, _, _ in LOCKFILE_ORDER}


def detect_lockfile(directory: Path | str = ".", *, explicit: str | None = None) -> Path:
    """Find the lockfile to audit.

    ``explicit`` wins.  Otherwise we walk *up* from the given directory until
    we find a known lockfile name, so ``deadledger audit`` works from a
    subdirectory of the project the way ``git`` does.
    """
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise NoLockfile(f"no such lockfile: {path}")
        return path.resolve()

    start = Path(directory).resolve()
    for current in [start, *start.parents]:
        for name, _, _ in LOCKFILE_ORDER:
            candidate = current / name
            if candidate.is_file():
                return candidate
        matches = sorted(
            child
            for child in current.glob("*")
            if child.is_file() and child.name in LOCKFILE_NAMES
        )
        if matches:
            return matches[0]
    raise NoLockfile(
        "no lockfile found in the current directory or any parent.\n"
        "  looked for: " + ", ".join(name for name, _, _ in LOCKFILE_ORDER) + "\n"
        "  point at one explicitly with --lockfile"
    )


def parse_lockfile(path: Path | str) -> Inventory:
    path = Path(path)
    name = path.name
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:  # pragma: no cover - unusual encodings
        text = path.read_text(encoding="utf-8", errors="replace")

    if name == "poetry.lock":
        return _parse_poetry(path, text)
    if name in {"uv.lock", "pdm.lock"}:
        return _parse_pep503_toml(path, text)
    if name == "Pipfile.lock":
        return _parse_pipfile(path, text)
    if name in {"package-lock.json", "npm-shrinkwrap.json"}:
        return _parse_package_lock(path, text)
    if name == "Cargo.lock":
        return _parse_cargo_lock(path, text)
    if name == "yarn.lock":
        return _parse_yarn(path, text)
    if name == "pnpm-lock.yaml":
        return _parse_pnpm_stub(path)
    if name.endswith(".txt") or name == "constraints.txt":
        return _parse_requirements(path, text)
    raise NoLockfile(f"unsupported lockfile format: {name}")


# ---------------------------------------------------------------------------
# PyPI: requirements.txt
# ---------------------------------------------------------------------------

_REQ_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?:\[(?P<extras>[^\]]+)\])?"
    r"\s*(?P<op>===|==|~=|>=|<=|!=|>|<)?\s*(?P<version>[^;\s#]+)?"
    r"(?P<rest>.*)$"
)


def _normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def _parse_requirements(path: Path, text: str) -> Inventory:
    """Parse a requirements file, including pip-compile's ``# via`` blocks.

    Two layouts exist in the wild and both are handled:

    * plain pins, one per line;
    * pip-compile output, where the ``# via`` comment comes *after* its pin::

          django==3.2.6
              # via -r requirements.in
          sqlparse==0.4.1
              # via django

    ``via -r requirements.in`` / ``via -c constraints.txt`` means "declared by
    the project"; anything else names the parents that pulled the pin in.

    A file with *no* ``# via`` comments is not pip-compile output, so it is a
    hand-maintained list of what the project depends on: every non-dev pin in it
    is direct.  Getting this wrong is not cosmetic -- directness decides what
    counts as critical, and treating a hand-written requirements file as 100 %
    transitive silently turns a mortality report into a list of things nobody
    has to make a decision about.
    """
    inv = Inventory(ecosystem="pypi", lockfile=path)
    lines = text.splitlines()
    generated = any(line.strip().startswith("# via") for line in lines)
    current_key: str | None = None
    index = 0
    while index < len(lines):
        raw = lines[index]
        index += 1
        line = raw.strip()
        if not line:
            current_key = None
            continue
        if line.startswith("#"):
            continue
        if line.startswith("-"):
            continue  # --index-url, -r includes, -c constraints
        match = _REQ_RE.match(line)
        if not match:
            inv.warnings.append(f"unparsed line: {line[:80]}")
            continue
        name = _normalise(match.group("name"))
        version = match.group("version") if match.group("op") in ("==", "===") else None
        extras = tuple(e.strip() for e in (match.group("extras") or "").split(",") if e.strip())
        key = f"{name}@{version}" if version else name
        inv.add(
            Node(
                ecosystem="pypi",
                name=name,
                version=version,
                key=key,
                dev=bool(DEV_NAME_HINTS.search(name)),
                source=str(path),
                extras=extras,
            )
        )
        current_key = key
        if not generated and not inv.nodes[key].dev:
            # Hand-written requirements file: the line is the declaration.
            inv.direct.add(key)
        # Consume the indented "# via ..." lines that follow this pin.
        while index < len(lines):
            follower = lines[index].strip()
            if not follower:
                break
            if not follower.startswith("#"):
                break
            index += 1
            body = follower.lstrip("# ").strip()
            if not body.lower().startswith("via"):
                continue
            spec = body[3:].strip()
            for parent in re.split(r",\s*", spec):
                parent = parent.strip()
                if not parent:
                    continue
                if parent.startswith(("-r", "-c")):
                    # Declared by the project itself.
                    inv.direct.add(key)
                    continue
                parent_name = _normalise(parent)
                inv.add_edge(parent_name, key, "pip-compile comment")
    return inv


# ---------------------------------------------------------------------------
# PyPI: poetry.lock (TOML)
# ---------------------------------------------------------------------------


def _load_toml(text: str) -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ only
        tomllib = None  # type: ignore[assignment]
    if tomllib is not None:
        return tomllib.loads(text)
    import tomli  # type: ignore[import-not-found]

    return tomli.loads(text)


def _parse_poetry(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="pypi", lockfile=path)
    document = _load_toml(text)
    packages = document.get("package") or []
    if not isinstance(packages, list):
        raise NoLockfile(f"{path}: unexpected poetry.lock structure")

    by_name: dict[str, list[Node]] = {}
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = _normalise(str(package.get("name") or ""))
        if not name:
            continue
        version = str(package.get("version") or "") or None
        categories = package.get("groups") or (
            [package.get("category")] if package.get("category") else []
        )
        dev = bool(categories) and all(c in {"dev", "docs"} for c in categories)
        optional = bool(package.get("optional"))
        key = f"{name}@{version}" if version else name
        node = Node(
            ecosystem="pypi",
            name=name,
            version=version,
            key=key,
            dev=dev or optional,
            source=str(path),
        )
        inv.add(node)
        by_name.setdefault(name, []).append(node)

    for package in packages:
        if not isinstance(package, dict):
            continue
        parent_name = _normalise(str(package.get("name") or ""))
        parent_version = str(package.get("version") or "") or None
        parent_key = f"{parent_name}@{parent_version}" if parent_version else parent_name
        dependencies = package.get("dependencies") or {}
        if isinstance(dependencies, dict):
            for dep_name, spec in dependencies.items():
                dep_key = _resolve_dependency(by_name, _normalise(dep_name), spec)
                if dep_key:
                    inv.add_edge(parent_key, dep_key, str(spec)[:40])

    _poetry_directs(inv, document, by_name)
    return inv


def _resolve_dependency(
    by_name: dict[str, list[Node]], name: str, spec: Any
) -> str | None:
    candidates = by_name.get(name)
    if not candidates:
        return None
    pinned = None
    if isinstance(spec, str):
        match = re.search(r"==?\s*([0-9][^\s,;]*)", spec)
        pinned = match.group(1) if match else None
    elif isinstance(spec, list):
        for entry in spec:
            if isinstance(entry, str):
                match = re.search(r"==?\s*([0-9][^\s,;]*)", entry)
                if match:
                    pinned = match.group(1)
                    break
    if pinned:
        for node in candidates:
            if node.version == pinned:
                return node.key
    return candidates[0].key


def _poetry_directs(
    inv: Inventory, document: dict[str, Any], by_name: dict[str, list[Node]]
) -> None:
    """Poetry v1 does not record which deps are direct, so read pyproject.toml.

    Reading the neighbouring pyproject.toml is a *read* of the user's own
    project; nothing is transmitted.  If it is absent we fall back to
    "everything main is direct" and say so, because directness drives the
    criticality of the orphan simulation.
    """
    pyproject = inv.lockfile.parent / "pyproject.toml"
    declared: set[str] = set()
    if pyproject.is_file():
        try:
            project = _load_toml(pyproject.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - malformed pyproject is not fatal
            inv.warnings.append(f"could not read {pyproject.name}: {exc}")
            project = {}
        inv.project_name = (project.get("project") or {}).get("name") or (
            project.get("tool", {}).get("poetry", {}).get("name")
        )
        for section in (
            (project.get("project") or {}).get("dependencies"),
            (project.get("project") or {}).get("optional-dependencies"),
            (project.get("tool", {}).get("poetry", {}) or {}).get("dependencies"),
        ):
            if isinstance(section, dict):
                for name in section:
                    declared.add(_normalise(name))
                for value in section.values() if section is not None else []:
                    if isinstance(value, list):  # optional-dependencies is {group: {...}}
                        continue
            elif isinstance(section, list):  # list of dicts: skip
                continue
        optional_groups = (project.get("project") or {}).get("optional-dependencies") or {}
        if isinstance(optional_groups, dict):
            for group in optional_groups.values():
                if isinstance(group, dict):
                    declared.update(_normalise(str(n)) for n in group)
                elif isinstance(group, list):
                    for entry in group:
                        declared.add(_normalise(str(entry).split("[")[0].split("=")[0]))
        # Poetry dependency groups (dev, docs) are not "direct" for criticality.
        declared.discard("python")

    for name in declared:
        for node in by_name.get(name, []):
            if not node.dev:
                inv.direct.add(node.key)

    if not declared:
        for key, node in inv.nodes.items():
            if not node.dev:
                inv.direct.add(key)
        inv.warnings.append(
            "poetry.lock does not record direct dependencies and no pyproject.toml "
            "was found; treating every non-dev package as direct"
        )
    else:
        inv.warnings.append(
            f"direct dependencies taken from {pyproject.name if pyproject.is_file() else 'pyproject.toml'}"
        )
    return None


# ---------------------------------------------------------------------------
# PyPI: uv.lock / pdm.lock (TOML, PEP 751-ish)
# ---------------------------------------------------------------------------


def _parse_pep503_toml(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="pypi", lockfile=path)
    document = _load_toml(text)
    packages = document.get("package") or []
    by_name: dict[str, list[Node]] = {}
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = _normalise(str(package.get("name") or ""))
        version = str(package.get("version") or "") or None
        if not name:
            continue
        key = f"{name}@{version}" if version else name
        inv.add(Node(ecosystem="pypi", name=name, version=version, key=key, source=str(path)))
        by_name.setdefault(name, []).append(inv.nodes[key])

    roots = document.get("manifest") or {}
    root_names = set()
    for table in (roots.get("dependencies"), roots.get("dev-dependencies")):
        if isinstance(table, list):
            for entry in table:
                if isinstance(entry, dict):
                    root_names.add(_normalise(str(entry.get("name") or "")))
                elif isinstance(entry, str):
                    root_names.add(_normalise(entry))
    for group in (roots.get("optional-dependencies") or {}).values() if isinstance(
        roots.get("optional-dependencies"), dict
    ) else []:
        for entry in group if isinstance(group, list) else []:
            if isinstance(entry, dict):
                root_names.add(_normalise(str(entry.get("name") or "")))

    for package in packages:
        if not isinstance(package, dict):
            continue
        name = _normalise(str(package.get("name") or ""))
        version = str(package.get("version") or "") or None
        key = f"{name}@{version}" if version else name
        if name in root_names:
            inv.direct.add(key)
        for dep in (package.get("dependencies") or []) + (package.get("dev-dependencies") or []):
            if not isinstance(dep, dict):
                continue
            dep_name = _normalise(str(dep.get("name") or ""))
            candidates = by_name.get(dep_name)
            if candidates:
                inv.add_edge(key, candidates[0].key, str(dep.get("specifier") or ""))

    if not root_names:
        inv.warnings.append(
            f"{path.name}: no [manifest] section; treating every package as transitive"
        )
    return inv


def _parse_pnpm_stub(path: Path) -> Inventory:
    import sys

    inv = Inventory(ecosystem="npm", lockfile=path)
    inv.warnings.append(
        "pnpm-lock.yaml is YAML; DeadLedger parses JS YAML free of dependencies, "
        "so it is not supported yet -- use package-lock.json or --lockfile"
    )
    if sys.version_info >= (3, 11):
        pass
    return inv


# ---------------------------------------------------------------------------
# PyPI: Pipfile.lock (JSON)
# ---------------------------------------------------------------------------


def _parse_pipfile(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="pypi", lockfile=path)
    document = json.loads(text)
    for section, dev in (("default", False), ("develop", True)):
        for name, spec in (document.get(section) or {}).items():
            version = None
            if isinstance(spec, dict):
                raw = str(spec.get("version") or "")
                match = re.match(r"==\s*(.+)", raw)
                version = match.group(1).strip() if match else None
            norm = _normalise(name)
            key = f"{norm}@{version}" if version else norm
            inv.add(
                Node(
                    ecosystem="pypi",
                    name=norm,
                    version=version,
                    key=key,
                    dev=dev,
                    source=str(path),
                )
            )
            inv.direct.add(key)
    inv.warnings.append(
        "Pipfile.lock does not record dependency edges; the tree is flat"
    )
    return inv


# ---------------------------------------------------------------------------
# npm: package-lock.json
# ---------------------------------------------------------------------------


def _parse_package_lock(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="npm", lockfile=path)
    document = json.loads(text)
    inv.project_name = document.get("name")

    if "packages" in document:
        packages = document.get("packages") or {}
        by_path: dict[str, Node] = {}
        for rel_path, meta in packages.items():
            if not isinstance(meta, dict):
                continue
            if not rel_path:  # the root project itself
                continue
            name = meta.get("name") or rel_path.rsplit("node_modules/", 1)[-1]
            if not name:
                continue
            version = str(meta.get("version") or "") or None
            key = f"{_normalise(name)}@{version}" if version else _normalise(name)
            node = Node(
                ecosystem="npm",
                name=str(name),
                version=version,
                key=key,
                dev=bool(meta.get("dev")),
                source=str(path),
            )
            inv.add(node)
            by_path[rel_path] = node
        root = packages.get("") or {}
        declared = set((root.get("dependencies") or {})) | set((root.get("optionalDependencies") or {}))
        dev_declared = set(root.get("devDependencies") or {})
        for rel_path, node in by_path.items():
            if _normalise(node.name) in {_normalise(d) for d in declared} and not node.dev:
                inv.direct.add(node.key)
            if _normalise(node.name) in {_normalise(d) for d in dev_declared}:
                inv.nodes[node.key].dev = True
        for rel_path, meta in packages.items():
            if not isinstance(meta, dict) or rel_path not in by_path:
                continue
            parent = by_path[rel_path]
            for section in ("dependencies", "optionalDependencies", "peerDependencies"):
                for dep_name in (meta.get(section) or {}):
                    child_key = _find_child(by_path, rel_path, dep_name)
                    if child_key:
                        inv.add_edge(parent.key, child_key)
        return inv

    # v1: nested dependencies
    def walk(entries: dict[str, Any], parent_key: str | None) -> None:
        for name, meta in entries.items():
            if not isinstance(meta, dict):
                continue
            version = str(meta.get("version") or "") or None
            key = f"{_normalise(name)}@{version}" if version else _normalise(name)
            inv.add(
                Node(
                    ecosystem="npm",
                    name=name,
                    version=version,
                    key=key,
                    dev=bool(meta.get("dev")),
                    source=str(path),
                )
            )
            if parent_key is None:
                inv.direct.add(key)
            else:
                inv.add_edge(parent_key, key)
            walk(meta.get("dependencies") or {}, key)

    walk(document.get("dependencies") or {}, None)
    return inv


def _find_child(by_path: dict[str, Node], parent_path: str, dep_name: str) -> str | None:
    """npm's resolution: nearest ``node_modules/<name>`` walking up the tree."""
    prefix = parent_path
    while True:
        candidate = f"{prefix}/node_modules/{dep_name}" if prefix else f"node_modules/{dep_name}"
        if candidate in by_path:
            return by_path[candidate].key
        if not prefix:
            return None
        prefix = prefix.rsplit("/node_modules/", 1)[0] if "/node_modules/" in prefix else ""


# ---------------------------------------------------------------------------
# crates: Cargo.lock
# ---------------------------------------------------------------------------


def _parse_cargo_lock(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="crates", lockfile=path)
    document = _load_toml(text)
    packages = document.get("package") or []
    by_name: dict[str, list[Node]] = {}
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = str(package.get("name") or "")
        version = str(package.get("version") or "") or None
        if not name:
            continue
        key = f"{name}@{version}" if version else name
        node = Node(
            ecosystem="crates",
            name=name,
            version=version,
            key=key,
            dev=False,
            source=str(path),
        )
        inv.add(node)
        by_name.setdefault(name, []).append(node)

    # The workspace's own crates are not dependencies of themselves: exclude
    # anything declared in Cargo.toml's [package] name (and workspace members).
    manifest = inv.lockfile.parent / "Cargo.toml"
    if manifest.is_file():
        local = _local_crate_names(manifest)
        for name in local:
            for node in list(by_name.get(name, [])):
                inv.nodes.pop(node.key, None)
        by_name = {
            name: [n for n in nodes if n.key in inv.nodes]
            for name, nodes in by_name.items()
        }

    # Cargo.lock v3+ lists each package's own dependencies; v1/v2 had a single
    # top-level list where "dependencies" was the whole graph.
    has_per_package = any(isinstance(p, dict) and p.get("dependencies") is not None for p in packages)
    if has_per_package:
        for package in packages:
            if not isinstance(package, dict):
                continue
            name = str(package.get("name") or "")
            version = str(package.get("version") or "") or None
            parent_key = f"{name}@{version}" if version else name
            for dep in package.get("dependencies") or []:
                dep_name, dep_version = _split_cargo_dep(str(dep))
                candidates = by_name.get(dep_name) or []
                chosen = next((c for c in candidates if c.version == dep_version), None)
                if chosen is None and candidates:
                    chosen = candidates[0]
                if chosen:
                    inv.add_edge(parent_key, chosen.key)
        # Cargo does not mark direct deps in the lock; use Cargo.toml if present.
        if manifest.is_file():
            declared = _cargo_declared(manifest)
            for name in declared:
                for node in by_name.get(name, []):
                    inv.direct.add(node.key)
            inv.warnings.append(f"direct dependencies taken from {manifest.name}")
        else:
            inv.warnings.append(
                "Cargo.lock does not mark direct dependencies and no Cargo.toml was "
                "found; every package is treated as transitive"
            )
    else:
        for key in inv.nodes:
            inv.direct.add(key)
        inv.warnings.append("Cargo.lock v1/v2 format: the dependency graph is flat")
    return inv


def _split_cargo_dep(text: str) -> tuple[str, str | None]:
    match = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*(\d[^\s]*)?", text)
    if not match:
        return text.strip(), None
    name, version = match.group(1), match.group(2)
    if version and version.startswith("("):
        version = version.strip("()")
    return name, version


def _local_crate_names(manifest: Path) -> set[str]:
    """Names of the crates in *this* workspace (not dependencies)."""
    try:
        document = _load_toml(manifest.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return set()
    names = set()
    package = document.get("package") or {}
    if package.get("name"):
        names.add(str(package["name"]))
    for member in (document.get("workspace") or {}).get("members") or []:
        member_manifest = manifest.parent / str(member) / "Cargo.toml"
        if member_manifest.is_file():
            names |= _local_crate_names(member_manifest)
    return names


def _cargo_declared(manifest: Path) -> set[str]:
    try:
        document = _load_toml(manifest.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - workspaces, cfg tables, etc.
        return set()
    names: set[str] = set()
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        names.update(str(k) for k in (document.get(section) or {}))
    for table in (document.get("target") or {}).values():
        if isinstance(table, dict):
            for section in ("dependencies", "dev-dependencies", "build-dependencies"):
                names.update(str(k) for k in (table.get(section) or {}))
    if not names:
        for section in ("dependencies", "dev-dependencies"):
            names.update(str(k) for k in ((document.get("workspace") or {}).get(section) or {}))
    return names


# ---------------------------------------------------------------------------
# yarn.lock
# ---------------------------------------------------------------------------


def _parse_yarn(path: Path, text: str) -> Inventory:
    inv = Inventory(ecosystem="npm", lockfile=path)
    inv.warnings.append(
        "yarn.lock: DeadLedger reads the pins but does not build edges from "
        "YAML, so depth and directness are unavailable for this project. "
        "Prefer package-lock.json when both exist."
    )
    version_re = re.compile(r'^\s*version:?\s+"?([^"\s]+)"?')
    header_re = re.compile(r'^"?(@?[^@\s]+)@')
    current: list[str] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and raw.rstrip().endswith(":"):
            spec = raw.rstrip().rstrip(":")
            names = [header_re.match(part.strip().strip('"')).group(1) for part in spec.split(", ") if header_re.match(part.strip().strip('"'))]
            current = names
            continue
        match = version_re.match(raw)
        if match and current:
            version = match.group(1)
            for name in current:
                norm = _normalise(name)
                key = f"{norm}@{version}"
                if key not in inv.nodes:
                    inv.add(
                        Node(
                            ecosystem="npm",
                            name=name,
                            version=version,
                            key=key,
                            source=str(path),
                        )
                    )
            current = []
    return inv


# ---------------------------------------------------------------------------
# convenience
# ---------------------------------------------------------------------------


def inventory_from(path: Path | str) -> Inventory:
    return parse_lockfile(Path(path))


def ecosystem_of(path: Path | str) -> str:
    inv = parse_lockfile(Path(path))
    return inv.ecosystem


def iter_lockfiles(directory: Path) -> Iterable[Path]:
    for name, _, _ in LOCKFILE_ORDER:
        candidate = directory / name
        if candidate.is_file():
            yield candidate
