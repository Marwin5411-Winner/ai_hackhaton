"""Ground-truth occupancy grid. The agent never reads this except via the sensor."""

from __future__ import annotations

from .config import ACTIONS, N


class GridWorld:
    def __init__(
        self,
        obstacles: set[tuple[int, int]],
        n: int = N,
        start: tuple[int, int] = (0, 0),
        goal: tuple[int, int] = (14, 14),
    ) -> None:
        self.n = n
        self.start = start
        self.goal = goal
        self.static = set(obstacles)
        self.static.discard(start)
        self.static.discard(goal)
        self.dynamic: set[tuple[int, int]] = set()
        self.obstacles = set(self.static)

    def spawn(self, cell: tuple[int, int]) -> bool:
        """Drop a live traffic blockage. Never covers the depot or the hospital."""
        if cell in (self.start, self.goal) or not self.in_bounds(*cell):
            return False
        if cell in self.obstacles:
            return False
        self.dynamic.add(cell)
        self.obstacles.add(cell)
        return True

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.n and 0 <= y < self.n

    def blocked(self, x: int, y: int) -> bool:
        return (x, y) in self.obstacles

    def passable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and not self.blocked(x, y)

    def neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        for dx, dy in ACTIONS:
            nx, ny = x + dx, y + dy
            if self.passable(nx, ny):
                out.append((nx, ny))
        return out

    def try_move(
        self, pos: tuple[int, int], action: tuple[int, int]
    ) -> tuple[tuple[int, int], bool]:
        """Apply a unit move. Blocked/OOB moves are rejected before execution."""
        nx, ny = pos[0] + action[0], pos[1] + action[1]
        if not self.passable(nx, ny):
            return pos, False
        return (nx, ny), True
