"""Spawn traffic on the ambulance's remaining route so it must live-reroute."""

from __future__ import annotations

from .world import GridWorld


class TrafficController:
    def __init__(
        self,
        world: GridWorld,
        spawn_ticks: tuple[int, ...] = (5, 14),
        look_ahead: int = 5,
    ) -> None:
        self.world = world
        self.remaining_ticks = set(spawn_ticks)
        self.look_ahead = look_ahead
        self.spawned: list[tuple[int, int]] = []

    def maybe_spawn(
        self,
        tick: int,
        remaining_path: list[tuple[int, int]],
        pos: tuple[int, int],
    ) -> tuple[int, int] | None:
        if tick not in self.remaining_ticks:
            return None
        self.remaining_ticks.discard(tick)
        ahead = remaining_path[self.look_ahead :]
        for cell in ahead:
            if cell in (pos, self.world.start, self.world.goal):
                continue
            if self.world.spawn(cell):
                self.spawned.append(cell)
                return cell
        return None
