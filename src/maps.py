"""City maps. Static buildings are known; traffic is spawned later on the route."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .config import GOAL, N, START


@dataclass(frozen=True)
class Scenario:
    name: str
    obstacles: frozenset[tuple[int, int]]
    spawn_ticks: tuple[int, ...]
    look_ahead: int


def _clean(obstacles: set[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    obstacles.discard(START)
    obstacles.discard(GOAL)
    return frozenset(c for c in obstacles if 0 <= c[0] < N and 0 <= c[1] < N)


def _blocks(origins: list[tuple[int, int]], w: int = 2, h: int = 2) -> set[tuple[int, int]]:
    obs: set[tuple[int, int]] = set()
    for bx, by in origins:
        for dx in range(w):
            for dy in range(h):
                obs.add((bx + dx, by + dy))
    return obs


def city() -> Scenario:
    """Open streets. Two traffic hits on the first A* route — the video map."""
    obs = _blocks([(2, 2), (2, 8), (2, 12), (8, 2), (8, 10), (11, 5), (11, 12)])
    return Scenario("city", _clean(obs), spawn_ticks=(5, 14), look_ahead=5)


def rush() -> Scenario:
    """Tighter corridor. One jam seals the greedy street and forces a detour."""
    obs = _blocks([(3, 1), (3, 5), (3, 9), (7, 3), (7, 8), (10, 1), (10, 10)])
    obs |= {(6, y) for y in range(0, 10)}
    return Scenario("rush", _clean(obs), spawn_ticks=(4, 12), look_ahead=4)


def gridlock() -> Scenario:
    """Denser blocks. Longer run if the city demo feels too short on camera."""
    obs: set[tuple[int, int]] = set()
    for i, y in enumerate(range(2, 14, 3)):
        gap = 1 if i % 2 == 0 else N - 2
        skip = {gap, gap + 1 if gap == 1 else gap - 1}
        for x in range(N):
            if x not in skip:
                obs.add((x, y))
    return Scenario("gridlock", _clean(obs), spawn_ticks=(6, 16, 28), look_ahead=4)


MAPS: dict[str, Callable[[], Scenario]] = {
    "demo": city,
    "city": city,
    "rush": rush,
    "deadend": rush,
    "gridlock": gridlock,
    "maze": gridlock,
}


def load(name: str) -> Scenario:
    try:
        return MAPS[name]()
    except KeyError as exc:
        known = ", ".join(sorted(MAPS))
        raise SystemExit(f"unknown map {name!r}; choose one of: {known}") from exc
