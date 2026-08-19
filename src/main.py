"""Entry point: python -m src.main --map demo"""

from __future__ import annotations

import argparse
from .agent import Agent, Status, oracle_cost
from .logger import Logger
from .maps import MAPS, load
from .world import GridWorld


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autonomous Rescue Bot — Dynamic A* on a partially observable grid"
    )
    parser.add_argument(
        "--map",
        default="demo",
        choices=sorted(MAPS),
        help="deterministic map (default: demo)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="run without Tkinter (prints the live log to stdout)",
    )
    return parser.parse_args(argv)


def run_headless(agent: Agent, world: GridWorld) -> Status:
    while agent.status is Status.RUNNING:
        agent.tick()
    agent.log.finalize(oracle_cost(world))
    return agent.status


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    world = GridWorld(load(args.map))
    logger = Logger()
    logger.log(
        f"Rescue Bot  map={args.map}  start={world.start}  goal={world.goal}  "
        f"obstacles={len(world.obstacles)}"
    )
    agent = Agent(world, logger)
    if args.headless:
        status = run_headless(agent, world)
        return 0 if status is Status.GOAL else 1
    from .viz import RescueViz

    RescueViz(world, agent).run()
    return 0 if agent.status is Status.GOAL else 1


if __name__ == "__main__":
    raise SystemExit(main())
