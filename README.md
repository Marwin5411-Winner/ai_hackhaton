# Emergency Response Ambulance

Dynamic A\* live replanning. An ambulance drives to the hospital; traffic jams spawn on the current route; it intercepts the block and reroutes from where it is — it does not restart.

- **Course:** BCA 301 — Artificial Intelligence
- **Track:** Track 4 — Emergency Response Ambulance (Unit 2/3, Dynamic Replanning)
- **Repo:** https://github.com/Marwin5411-Winner/ai_hackhaton
- **Demo Video:** \<link\>

Team (fill before submit): Group ID `10` · 1. `Maria Rachel Manoj 2441631` · 2. `Marvin Roupmong 2441632` · 3. `Meet Garg 2441633`

All three members must have visible commits on this repository.

## Scenario

An emergency ambulance must reach a hospital on a dynamic grid where traffic blockages appear in real time. The agent runs Dynamic A* / Replanning Search: when a blockage spawns on the pre-computed route, it intercepts the block and recalculates a new path automatically, mid-motion, without restarting the run.

## Run

Python 3.11+ (stdlib only — Tkinter + `heapq`). No `pip install`.

```bash
python3 -m src.main --map city
python3 -m src.main --map rush
python3 -m src.main --map gridlock
python3 -m src.main --map city --headless
```

Split the window for the 60–90s video: city grid on the left, this terminal on the right.

Watch for: ambulance moving → orange traffic appears on the blue route → `TRAFFIC` then `REPLAN` in the log → new route, still going to **H**.

## PEAS (short)

| | |
|---|---|
| **Performance** | Hospital reached; path cost; nodes expanded; replans; wall-clock; collisions = 0 |
| **Environment** | 15×15 city grid, static buildings, **dynamic traffic** that appears on the live route |
| **Actuators** | `MOVE_UP / DOWN / LEFT / RIGHT` (one cell per tick) |
| **Sensors** | Route monitor (block on remaining path) + local scan |

Algorithm

1. A\* a path from the depot `(0,0)` to the hospital `(14,14)` around known buildings.
2. Drive along that path.
3. At scripted ticks, a traffic jam spawns **on the remaining route**.
4. Intercept → replan A\* from the **current cell** (not from the start).
5. Keep driving. Repeat if another jam hits.

## Maps

| Name | Why it exists |
|---|---|
| `city` | Open streets, two jams — default video map |
| `rush` | Tighter corridor; a jam seals the greedy street |
| `gridlock` | Denser blocks; longer camera run |
