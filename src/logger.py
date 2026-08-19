"""Real-time decision log + end-of-run metrics for SUMMARY.pdf placeholders."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass


@dataclass
class Metrics:
    goal_reached: bool = False
    path_cost: int = 0
    nodes_expanded: int = 0
    peak_frontier: int = 0
    replans: int = 0
    wall_clock_s: float = 0.0
    oracle_cost: int = -1
    collisions: int = 0
    ticks: int = 0
    unreachable: bool = False


class Logger:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.metrics = Metrics()
        self._t0 = time.perf_counter()
        self.listeners: list = []

    def log(self, message: str) -> None:
        line = message
        self.lines.append(line)
        print(line, flush=True)
        for cb in self.listeners:
            cb(line)

    def sense(self, tick: int, pos: tuple[int, int], new_walls: list[tuple[int, int]]) -> None:
        extra = f"  new_walls={new_walls}" if new_walls else ""
        self.log(f"t={tick:03d} SENSE  pos={pos}{extra}")

    def plan(
        self,
        tick: int,
        pos: tuple[int, int],
        cost: int,
        expanded: int,
        frontier: int,
        reason: str,
        *,
        replan: bool,
    ) -> None:
        if replan:
            self.metrics.replans += 1
        self.metrics.nodes_expanded += expanded
        self.metrics.peak_frontier = max(self.metrics.peak_frontier, frontier)
        tag = "REPLAN" if replan else "PLAN  "
        self.log(
            f"t={tick:03d} {tag} pos={pos} reason={reason} "
            f"plan_cost={cost} expanded={expanded} frontier={frontier}"
        )

    def step(self, tick: int, action: str, pos: tuple[int, int]) -> None:
        self.metrics.path_cost += 1
        self.log(f"t={tick:03d} STEP   {action} -> {pos}")

    def blocked(self, tick: int, pos: tuple[int, int], target: tuple[int, int]) -> None:
        self.metrics.collisions += 1
        self.log(f"t={tick:03d} BLOCKED pos={pos} tried={target} (rejected, no collision)")

    def goal(self, tick: int, pos: tuple[int, int]) -> None:
        self.metrics.goal_reached = True
        self.log(f"t={tick:03d} GOAL   reached {pos}")

    def unreachable(self, tick: int, pos: tuple[int, int]) -> None:
        self.metrics.unreachable = True
        self.log(f"t={tick:03d} UNREACHABLE pos={pos} OPEN empty")

    def finalize(self, oracle_cost: int) -> Metrics:
        self.metrics.oracle_cost = oracle_cost
        self.metrics.wall_clock_s = time.perf_counter() - self._t0
        m = self.metrics
        sep = "-" * 52
        self.log(sep)
        self.log("SUMMARY METRICS (paste into SUMMARY.pdf <__> fields)")
        self.log(f"  goal_reached    = {m.goal_reached}")
        self.log(f"  path_cost       = {m.path_cost}")
        self.log(f"  nodes_expanded  = {m.nodes_expanded}")
        self.log(f"  peak_frontier   = {m.peak_frontier}")
        self.log(f"  replans         = {m.replans}")
        self.log(f"  wall_clock_s    = {m.wall_clock_s:.4f}")
        self.log(f"  oracle_cost     = {m.oracle_cost}")
        self.log(f"  collisions      = {m.collisions}")
        self.log(f"  ticks           = {m.ticks}")
        self.log(sep)
        sys.stdout.flush()
        return m
