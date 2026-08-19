"""Deterministic 15×15 maps. All are solvable; demo/deadend force visible replans."""
from __future__ import annotations
from collections.abc import Callable
from .config import GOAL, N, START


def _clean(obstacles: set[tuple[int, int]]) -> set[tuple[int, int]]:
    obstacles.discard(START)
    obstacles.discard(GOAL)
    return {c for c in obstacles if 0 <= c[0] < N and 0 <= c[1] < N}


def demo() -> set[tuple[int, int]]:
    """Near-full column at x=7. Free-space A* crosses it; first sense-along-path replans."""
    obs = {(7, y) for y in range(0, 13)}
    obs |= {(3, 9), (4, 9), (10, 4), (12, 11), (1, 12)}
    return _clean(obs)


def deadend() -> set[tuple[int, int]]:
    """U-trap on the greedy top corridor, plus a late column so the first plan dies fast."""
    obs: set[tuple[int, int]] = set()
    # Cul-de-sac sitting on y=0 around x=8..10 (outside initial r=2).
    obs |= {(7, 0), (11, 0), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1)}
    # Column that every remaining route must discover later.
    obs |= {(6, y) for y in range(0, 12)}
    return _clean(obs)


def maze() -> set[tuple[int, int]]:
    """Alternating horizontal bars. Longer video; still 4-connected solvable."""
    obs: set[tuple[int, int]] = set()
    for i, y in enumerate(range(2, 14, 3)):
        gap = 1 if i % 2 == 0 else N - 2
        for x in range(N):
            if x not in (gap, gap + 1 if gap == 1 else gap - 1):
                obs.add((x, y))
    return _clean(obs)


MAPS: dict[str, Callable[[], set[tuple[int, int]]]] = {
    "demo": demo,
    "deadend": deadend,
    "maze": maze,
}


def load(name: str) -> set[tuple[int, int]]:
    try:
        return MAPS[name]()
    except KeyError as exc:
        known = ", ".join(MAPS)
        raise SystemExit(f"unknown map {name!r}; choose one of: {known}") from exc