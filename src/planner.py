"""A* on a 4-connected unit grid. Heuristic: Manhattan (admissible + consistent)."""

from __future__ import annotations

import heapq
from collections.abc import Callable
from dataclasses import dataclass

from .config import ACTIONS, N


@dataclass(frozen=True)
class PlanStats:
    nodes_expanded: int
    peak_frontier: int
    path_cost: int  # len(path) - 1, or -1 if unreachable


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    start: tuple[int, int],
    goal: tuple[int, int],
    is_blocked: Callable[[int, int], bool],
    n: int = N,
) -> tuple[list[tuple[int, int]], PlanStats]:
    """Plan a path from start to goal. Unreachable → empty path and path_cost -1."""
    if start == goal:
        return [start], PlanStats(nodes_expanded=1, peak_frontier=1, path_cost=0)
    if is_blocked(*goal) or is_blocked(*start):
        return [], PlanStats(nodes_expanded=0, peak_frontier=0, path_cost=-1)

    counter = 0
    open_heap: list[tuple[int, int, int, tuple[int, int]]] = []
    g: dict[tuple[int, int], int] = {start: 0}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    heapq.heappush(open_heap, (manhattan(start, goal), 0, counter, start))
    closed: set[tuple[int, int]] = set()
    nodes_expanded = 0
    peak_frontier = 1

    while open_heap:
        peak_frontier = max(peak_frontier, len(open_heap))
        _f, g_pop, _id, node = heapq.heappop(open_heap)
        if node in closed:
            continue
        if g_pop != g.get(node):
            continue
        closed.add(node)
        nodes_expanded += 1

        if node == goal:
            path = _reconstruct(parent, goal)
            return path, PlanStats(nodes_expanded, peak_frontier, len(path) - 1)

        x, y = node
        for dx, dy in ACTIONS:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < n and 0 <= ny < n):
                continue
            if is_blocked(nx, ny):
                continue
            cand = (nx, ny)
            ng = g[node] + 1
            if ng >= g.get(cand, 1_000_000):
                continue
            g[cand] = ng
            parent[cand] = node
            counter += 1
            heapq.heappush(open_heap, (ng + manhattan(cand, goal), ng, counter, cand))

    return [], PlanStats(nodes_expanded, peak_frontier, path_cost=-1)


def _reconstruct(
    parent: dict[tuple[int, int], tuple[int, int] | None], goal: tuple[int, int]
) -> list[tuple[int, int]]:
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
