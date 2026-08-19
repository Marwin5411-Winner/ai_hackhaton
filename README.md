# Autonomous Rescue Bot

Dynamic A\* replanning agent on a partially observable 15×15 grid.

- **Course:** BCA 301 — Artificial Intelligence
- **Track:** Unit 2 — Problem-Solving Agents (Informed Search + Dynamic Replanning)
- **Repo:** https://github.com/Marwin5411-Winner/ai_hackhaton
- **Demo Video:** \<link\>

Team (fill before submit): Group ID `\<GROUP ID\>` · 1. `\<Name\> (\<Reg No\>)` · 2. `\<Name\> (\<Reg No\>)` · 3. `\<Name\> (\<Reg No\>)`

All three members must have visible commits on this repository.

## Run

Python 3.11+ (stdlib only — Tkinter + `heapq`). No `pip install`.

```bash
python3 -m src.main --map demo
python3 -m src.main --map deadend
python3 -m src.main --map maze
python3 -m src.main --map demo --headless   # log only, no window
```

Split the window for the 60–90s video: grid on the left, this terminal on the right. The same decision lines print in both.

## PEAS (short)

| | |
|---|---|
| **Performance** | Goal reached; path cost; nodes expanded; replans; wall-clock; collisions = 0 |
| **Environment** | 15×15 occupancy grid, static unknown walls, partial observability (Chebyshev r=2), deterministic, single agent |
| **Actuators** | `MOVE_UP / DOWN / LEFT / RIGHT` (4-connected, unit cost, one cell per tick) |
| **Sensors** | Local occupancy scan r=2, odometer (x, y), goal register |

## Algorithm

Belief grid starts empty. Unobserved cells are assumed free. After each `SENSE`, if the remaining A\* path intersects a newly known wall, the agent replans from its current cell (Manhattan heuristic, admissible and consistent). Blocked moves are rejected before execution.

End-of-run metrics from `logger.py` fill the `<__>` fields in `SUMMARY.pdf`.

## Maps

| Name | Why it exists |
|---|---|
| `demo` | Column wall on every shortest free-space path — guaranteed replan |
| `deadend` | Cul-de-sac on the greedy corridor, then a late column |
| `maze` | Longer corridor run for the video if `demo` is too short |
