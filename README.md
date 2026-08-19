Emergency Response Ambulance — Dynamic A* Replanning

An ambulance agent navigating to a hospital on a partially observable 15×15 city grid, live-rerouting the moment a traffic blockage appears on its planned route — no restart.

- Course: BCA 301-5 — Artificial Intelligence
- Track: Track 4 — Emergency Response Ambulance (Unit 2/3 — Dynamic Replanning)
- Repo: https://github.com/Marwin5411-Winner/ai_hackhaton
- Demo Video:

Team (fill before submit): Group ID `10` · 1. `Maria Rachel Manoj 2441631` · 2. `Marvin Roupmong 2441632` · 3. `Meet Garg 2441633`

All three members must have visible commits on this repository.

## Scenario

An emergency ambulance must reach a hospital on a dynamic grid where traffic blockages appear in real time. The agent runs Dynamic A* / Replanning Search: when a blockage spawns on the pre-computed route, it intercepts the block and recalculates a new path automatically, mid-motion, without restarting the run.

## Run

Python 3.11+ (stdlib only — Tkinter + `heapq`). No `pip install`.

```bash
python3 -m src.main --map demo
python3 -m src.main --map deadend
python3 -m src.main --map maze
python3 -m src.main --map demo --headless   
```

Deliverable checklist

- [ ] Ambulance visibly moving toward the hospital
- [ ] A blockage is encountered mid-route (not known in advance)
- [ ] Live reroute happens automatically — no restart, no manual intervention
- [ ] Ambulance reaches the hospital

PEAS 

|Performance | Hospital reached; route cost; nodes expanded; reroutes; wall-clock; collisions = 0 |
| Environment| 15×15 city grid, static unknown traffic blockages, partial observability (local traffic sensor, Chebyshev r=2), deterministic, single ambulance |
|Actuators| `MOVE_UP / DOWN / LEFT / RIGHT` (4-connected road segments, unit cost, one cell per tick) |
|Sensors| Local traffic scan r=2, GPS odometer (x, y), hospital location register |

Algorithm

The ambulance's belief map of the city starts empty — unscanned roads are assumed clear. After each traffic scan (`SENSE`), if the currently planned route intersects a newly detected blockage, the ambulance replans from its current position (Manhattan heuristic, admissible and consistent) and continues driving on the new route without stopping the simulation. Moves into a detected blockage are rejected before execution, so the ambulance never drives into a wall it already knows about.


## Maps

| Name | Why it exists |
| `demo` | Blockage sits across every shortest route — guaranteed reroute |
| `deadend` | Dead-end detour on the greedy route, then a late blockage |
| `maze` | Longer route, useful if `demo` finishes too fast for the video |