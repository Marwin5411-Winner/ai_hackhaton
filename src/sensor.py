"""Local proximity scan: occupancy of every cell within Chebyshev distance r."""

from __future__ import annotations

from .config import SENSOR_R
from .world import GridWorld


def scan(
    world: GridWorld, pos: tuple[int, int], r: int = SENSOR_R
) -> dict[tuple[int, int], bool]:
    """Return {cell: occupied} for every in-bounds cell with chebyshev(pos, cell) <= r."""
    x0, y0 = pos
    reading: dict[tuple[int, int], bool] = {}
    for y in range(y0 - r, y0 + r + 1):
        for x in range(x0 - r, x0 + r + 1):
            if not world.in_bounds(x, y):
                continue
            if max(abs(x - x0), abs(y - y0)) > r:
                continue
            reading[(x, y)] = world.blocked(x, y)
    return reading
