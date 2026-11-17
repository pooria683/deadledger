"""The dependency graph: directness, depth, and why a package is reachable.

Two questions matter for a mortality report and a flat list cannot answer
either:

* **Is it critical?**  Critical means "direct, non-dev".  A dead transitive
  dependency is somebody else's migration problem; a dead direct one is yours.
* **How far away is it?**  Depth tells a reader how much of the tree breaks.

Where the lockfile does not record edges (Pipfile.lock, yarn.lock), the graph
degrades honestly: everything non-dev is treated as direct and the report
carries a warning rather than inventing a tree.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .lockfiles import Inventory, Node


@dataclass
class NodeFacts:
    key: str
    depth: int | None          # 0 = direct
    paths: int                 # number of distinct paths from the project
    parents: list[str] = field(default_factory=list)
    critical: bool = False
    reasons_off_path: list[str] = field(default_factory=list)


@dataclass
class GraphAnalysis:
    facts: dict[str, NodeFacts]
    flat: bool
    warnings: list[str] = field(default_factory=list)

    def critical_keys(self) -> list[str]:
        return [key for key, fact in self.facts.items() if fact.critical]


def analyse(inventory: Inventory) -> GraphAnalysis:
    """Compute depth, fan-in, and criticality for every node."""
    children = inventory.children()
    has_edges = bool(inventory.edges)
    flat = not has_edges

    depth: dict[str, int] = {}
    paths: dict[str, int] = {}
    parents: dict[str, set[str]] = {}

    roots = sorted(inventory.direct)
    queue: deque[tuple[str, int]] = deque()
    for key in roots:
        depth[key] = 0
        paths[key] = 1
        parents.setdefault(key, set())
        queue.append((key, 0))

    # Breadth-first over the lockfile's own edges.  Cycles are legal in npm;
    # the visited-depth check keeps the walk finite.
    while queue:
        current, current_depth = queue.popleft()
        for child in sorted(children.get(current, ())):
            if child not in inventory.nodes:
                continue
            next_depth = current_depth + 1
            improved = child not in depth or next_depth < depth[child]
            if improved:
                depth[child] = next_depth
                queue.append((child, next_depth))
            paths[child] = paths.get(child, 0) + paths.get(current, 1)
            parents.setdefault(child, set()).add(current)

    if flat:
        for key, node in inventory.nodes.items():
            if node.dev:
                continue
            if key not in depth:
                depth[key] = 0
                paths.setdefault(key, 1)
                parents.setdefault(key, set())

    facts: dict[str, NodeFacts] = {}
    for key, node in inventory.nodes.items():
        node_depth = depth.get(key)
        is_direct = key in inventory.direct or node_depth == 0
        facts[key] = NodeFacts(
            key=key,
            depth=node_depth,
            paths=max(1, paths.get(key, 0)),
            parents=sorted(parents.get(key, ())),
            critical=bool(is_direct and not node.dev),
        )

    return GraphAnalysis(facts=facts, flat=flat, warnings=list(inventory.warnings))


def depth_label(depth: int | None) -> str:
    if depth is None:
        return "unknown depth"
    if depth == 0:
        return "direct"
    return f"transitive (depth {depth})"


def reachability_sentence(node: Node, fact: NodeFacts) -> str:
    """Answer "why do I have this?" in one line, for the report."""
    if fact.depth == 0:
        return "declared directly by this project"
    if fact.parents:
        shown = ", ".join(fact.parents[:3])
        extra = f" and {len(fact.parents) - 3} more" if len(fact.parents) > 3 else ""
        via = f"via {shown}{extra}"
    else:
        via = "with no recorded parent"
    return f"depth {fact.depth}, {via}"
