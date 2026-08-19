"""Ambulance sense–plan–act loop. Replans from the current cell when traffic hits the route."""

from __future__ import annotations

from enum import Enum

from .config import ACTION_NAMES, GOAL, MAX_TICKS, N, SENSOR_R, START
from .logger import Logger
from .planner import astar
from .sensor import scan
from .traffic import TrafficController
from .world import GridWorld


class Status(str, Enum):
    RUNNING = "running"
    GOAL = "goal"
    UNREACHABLE = "unreachable"
    TIMEOUT = "timeout"


class Agent:
    def __init__(
        self,
        world: GridWorld,
        logger: Logger,
        traffic: TrafficController | None = None,
    ) -> None:
        self.world = world
        self.log = logger
        self.traffic = traffic
        self.radius = SENSOR_R
        self.pos: tuple[int, int] = START
        # City map is known. Live traffic is added when it spawns on the route.
        self.known_obstacles: set[tuple[int, int]] = set(world.static)
        self.known_free: set[tuple[int, int]] = set()
        self.path: list[tuple[int, int]] = []
        self.path_index = 0
        self.tick_id = 0
        self.status = Status.RUNNING
        self._planned_once = False

    def at_goal(self) -> bool:
        return self.pos == GOAL

    def remaining_path(self) -> list[tuple[int, int]]:
        if not self.path:
            return []
        return self.path[self.path_index :]

    def path_blocked(self) -> bool:
        if not self.path:
            return True
        for cell in self.path[self.path_index + 1 :]:
            if cell in self.known_obstacles:
                return True
        return False

    def sense(self) -> list[tuple[int, int]]:
        reading = scan(self.world, self.pos)
        new_walls: list[tuple[int, int]] = []
        for cell, occupied in reading.items():
            if occupied:
                if cell not in self.known_obstacles:
                    new_walls.append(cell)
                self.known_obstacles.add(cell)
                self.known_free.discard(cell)
            else:
                self.known_free.add(cell)
        new_walls.sort()
        self.log.sense(self.tick_id, self.pos, new_walls)
        return new_walls

    def replan(self, reason: str) -> bool:
        def is_blocked(x: int, y: int) -> bool:
            return (x, y) in self.known_obstacles

        path, stats = astar(self.pos, GOAL, is_blocked, n=N)
        is_replan = self._planned_once
        self._planned_once = True
        if not path:
            self.path = []
            self.log.plan(
                self.tick_id,
                self.pos,
                -1,
                stats.nodes_expanded,
                stats.peak_frontier,
                reason,
                replan=is_replan,
            )
            return False
        self.path = path
        self.path_index = 0
        self.log.plan(
            self.tick_id,
            self.pos,
            stats.path_cost,
            stats.nodes_expanded,
            stats.peak_frontier,
            reason,
            replan=is_replan,
        )
        return True

    def step(self) -> bool:
        if len(self.path) <= self.path_index + 1:
            return True
        nxt = self.path[self.path_index + 1]
        action = (nxt[0] - self.pos[0], nxt[1] - self.pos[1])
        new_pos, ok = self.world.try_move(self.pos, action)
        if not ok:
            self.log.blocked(self.tick_id, self.pos, nxt)
            self.path = []
            return False
        self.pos = new_pos
        self.path_index += 1
        name = ACTION_NAMES.get(action, str(action))
        self.log.step(self.tick_id, name, self.pos)
        return True

    def tick(self) -> Status:
        if self.status != Status.RUNNING:
            return self.status
        self.tick_id += 1
        self.log.metrics.ticks = self.tick_id

        if self.tick_id > MAX_TICKS:
            self.status = Status.TIMEOUT
            self.log.log(f"t={self.tick_id:03d} TIMEOUT")
            return self.status

        spawned = None
        if self.traffic:
            spawned = self.traffic.maybe_spawn(self.tick_id, self.remaining_path(), self.pos)
            if spawned:
                self.known_obstacles.add(spawned)
                self.known_free.discard(spawned)
                self.log.traffic(self.tick_id, spawned)

        new_walls = self.sense()
        if self.at_goal():
            self.status = Status.GOAL
            self.log.goal(self.tick_id, self.pos)
            return self.status

        reason = None
        if not self.path:
            reason = "no_plan"
        elif spawned:
            reason = "traffic_on_route"
        elif self.path_blocked():
            reason = "traffic_on_route" if new_walls else "path_blocked"

        if reason:
            if not self.replan(reason):
                self.status = Status.UNREACHABLE
                self.log.unreachable(self.tick_id, self.pos)
                return self.status

        self.step()
        if self.at_goal():
            self.status = Status.GOAL
            self.log.goal(self.tick_id, self.pos)
        return self.status


def oracle_cost(world: GridWorld) -> int:
    path, stats = astar(START, GOAL, world.blocked, n=world.n)
    return stats.path_cost
