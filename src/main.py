"""Entry point: python -m src.main --map city"""

from __future__ import annotations

import argparse
from .agent import Agent, Status, oracle_cost
from .logger import Logger
from .maps import MAPS, load
from .traffic import TrafficController
from .world import GridWorld


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emergency Response Ambulance — Dynamic A* live replanning"
    )
    parser.add_argument(
        "--map",
        default="city",
        choices=sorted(MAPS),
        help="city map (default: city)",
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
    scenario = load(args.map)
    world = GridWorld(set(scenario.obstacles))
    logger = Logger()
    logger.log(
        f"Ambulance  map={scenario.name}  depot={world.start}  hospital={world.goal}  "
        f"buildings={len(world.static)}  traffic_ticks={scenario.spawn_ticks}"
    )
    traffic = TrafficController(
        world,
        spawn_ticks=scenario.spawn_ticks,
        look_ahead=scenario.look_ahead,
    )
    agent = Agent(world, logger, traffic=traffic)
    if args.headless:
        status = run_headless(agent, world)
        return 0 if status is Status.GOAL else 1
    from .viz import RescueViz

    RescueViz(world, agent).run()
    return 0 if agent.status is Status.GOAL else 1


if __name__ == "__main__":
    raise SystemExit(main())
