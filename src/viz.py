"""Tkinter grid + live log. Fog of war: unknown cells stay hidden until sensed."""

from __future__ import annotations

import tkinter as tk

from .agent import Agent, Status
from .config import CELL_PX, GOAL, LOG_WIDTH, N, START, TICK_MS
from .world import GridWorld

COLOR = {
    "bg": "#1b1f2a",
    "fog": "#3a4254",
    "free": "#d9e4f2",
    "wall": "#12151c",
    "path": "#5dade2",
    "agent": "#e74c3c",
    "start": "#27ae60",
    "goal": "#f4d03f",
    "grid": "#2c3344",
    "text": "#e8eef5",
}


class RescueViz:
    def __init__(self, world: GridWorld, agent: Agent) -> None:
        self.world = world
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("Autonomous Rescue Bot — Dynamic A*")
        self.root.configure(bg=COLOR["bg"])

        board = N * CELL_PX
        self.canvas = tk.Canvas(
            self.root,
            width=board,
            height=board,
            bg=COLOR["bg"],
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, padx=12, pady=12, sticky="nw")

        side = tk.Frame(self.root, bg=COLOR["bg"])
        side.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="nsew")
        self.root.columnconfigure(1, weight=1)

        tk.Label(
            side,
            text="Decision log",
            fg=COLOR["text"],
            bg=COLOR["bg"],
            font=("Menlo", 13, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.log_box = tk.Text(
            side,
            width=LOG_WIDTH,
            height=28,
            bg="#10141c",
            fg="#b8f0c8",
            insertbackground=COLOR["text"],
            font=("Menlo", 11),
            wrap="word",
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, pady=(6, 8))

        self.status_var = tk.StringVar(value="status: running")
        tk.Label(
            side,
            textvariable=self.status_var,
            fg=COLOR["text"],
            bg=COLOR["bg"],
            font=("Menlo", 12),
            anchor="w",
            justify="left",
        ).pack(fill="x")

        legend = (
            "fog  free  wall  path  agent  goal\n"
            "Track 2 · 15×15 · r=2 Chebyshev · A* Manhattan"
        )
        tk.Label(
            side,
            text=legend,
            fg="#9aa7bd",
            bg=COLOR["bg"],
            font=("Menlo", 10),
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(8, 0))

        agent.log.listeners.append(self._on_log)
        for line in agent.log.lines:
            self._on_log(line)
        self._draw()

    def _on_log(self, line: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", line + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _cell_color(self, cell: tuple[int, int]) -> str:
        agent = self.agent
        if cell == agent.pos:
            return COLOR["agent"]
        if cell == GOAL:
            return COLOR["goal"]
        if cell == START:
            return COLOR["start"]
        remaining = set(agent.remaining_path()[1:])
        if cell in remaining and cell not in agent.known_obstacles:
            return COLOR["path"]
        if cell in agent.known_obstacles:
            return COLOR["wall"]
        if cell in agent.known_free:
            return COLOR["free"]
        return COLOR["fog"]

    def _draw(self) -> None:
        self.canvas.delete("all")
        for y in range(N):
            for x in range(N):
                x0, y0 = x * CELL_PX, y * CELL_PX
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + CELL_PX,
                    y0 + CELL_PX,
                    fill=self._cell_color((x, y)),
                    outline=COLOR["grid"],
                )
        # agent ring so it stays visible on the path
        ax, ay = self.agent.pos
        pad = 6
        self.canvas.create_oval(
            ax * CELL_PX + pad,
            ay * CELL_PX + pad,
            ax * CELL_PX + CELL_PX - pad,
            ay * CELL_PX + CELL_PX - pad,
            outline="#ffffff",
            width=2,
        )

    def _pulse(self) -> None:
        if self.agent.status is Status.RUNNING:
            self.agent.tick()
            self._draw()
            self.status_var.set(
                f"status: {self.agent.status.value}   pos={self.agent.pos}   "
                f"cost={self.agent.log.metrics.path_cost}   "
                f"replans={self.agent.log.metrics.replans}"
            )
            self.root.after(TICK_MS, self._pulse)
            return
        self._draw()
        self.status_var.set(f"status: {self.agent.status.value}   pos={self.agent.pos}")
        from .agent import oracle_cost

        self.agent.log.finalize(oracle_cost(self.world))

    def run(self) -> None:
        self.root.after(TICK_MS, self._pulse)
        self.root.mainloop()
