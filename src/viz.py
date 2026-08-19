"""Tkinter city grid + live dispatch log for the ambulance."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont

from .agent import Agent, Status
from .config import CELL_PX, GOAL, LOG_WIDTH, N, START, TICK_MS
from .world import GridWorld

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------

BG = "#0b0e14"           # window background
PANEL = "#12161f"          # header / stat cards
PANEL_ALT = "#161c28"       # canvas + log background
BORDER = "#232b3a"
GRID_LINE = "#1b2230"
ACCENT = "#3fa9f5"

COLOR = {
    "fog": "#232b3a",
    "free": "#3a4254",
    "wall": "#1c2330",
    "traffic": "#f97316",
    "path": "#38bdf8",
    "sensor": "#7dd3fc",
    "start": "#34d399",
    "agent": "#e11d48",
    "goal": "#22c55e",
}

TEXT_PRIMARY = "#e7edf5"
TEXT_SECONDARY = "#8b96ab"
TEXT_MUTED = "#5b6478"

class StatusStyle:
    """Resolves a display color and label for agent.status without needing
    to know the exact member names of the real Status enum (which may not
    match RUNNING/REACHED/STUCK exactly). Looked up by enum member *name*,
    so it works whether the real enum calls it REACHED, DONE, SUCCESS, etc.
    """

    COLOR_BY_NAME = {
        "RUNNING": "#34d399",
        "GOAL": "#22c55e",
        "REACHED": "#fbbf24",
        "GOAL_REACHED": "#fbbf24",
        "DONE": "#fbbf24",
        "SUCCESS": "#fbbf24",
        "FINISHED": "#fbbf24",
        "COMPLETE": "#fbbf24",
        "UNREACHABLE": "#ff6b57",
        "TIMEOUT": "#ff6b57",
        "STUCK": "#ff6b57",
        "FAILED": "#ff6b57",
        "NO_PATH": "#ff6b57",
        "BLOCKED": "#ff6b57",
        "ERROR": "#ff6b57",
    }
    DEFAULT_COLOR = "#8b96ab"

    @classmethod
    def color(cls, status) -> str:
        name = getattr(status, "name", str(status)).upper()
        return cls.COLOR_BY_NAME.get(name, cls.DEFAULT_COLOR)

    @classmethod
    def label(cls, status) -> str:
        value = getattr(status, "value", None)
        if isinstance(value, str) and value:
            return value.upper()
        return getattr(status, "name", str(status)).upper()

MARGIN_LEFT = 26   # room for row-index ticks
MARGIN_TOP = 22     # room for column-index ticks


def _pick_font(root: tk.Misc, preferred: list[str], fallback: str) -> str:
    """Cross-platform monospace: use whichever preferred family is actually
    installed, so the UI doesn't silently fall back to a mismatched default
    font on a teammate's Windows/Linux machine.
    """
    available = set(tkfont.families(root))
    for name in preferred:
        if name in available:
            return name
    return fallback


class RescueViz:
    def __init__(self, world: GridWorld, agent: Agent) -> None:
        self.world = world
        self.agent = agent

        self.root = tk.Tk()
        self.root.title("Ambulance — Dynamic A* Live Replanning")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        mono = _pick_font(
            self.root,
            ["JetBrains Mono", "Cascadia Code", "SF Mono", "Consolas", "Menlo"],
            "Courier",
        )
        self.font_mono = mono
        self.font_title = (mono, 15, "bold")
        self.font_subtitle = (mono, 10)
        self.font_section = (mono, 11, "bold")
        self.font_log = (mono, 10)
        self.font_stat_label = (mono, 9)
        self.font_stat_value = (mono, 17, "bold")
        self.font_legend = (mono, 9)
        self.font_tick = (mono, 8)

        self._build_header()
        self._build_canvas()
        self._build_sidebar()

        agent.log.listeners.append(self._on_log)
        for line in agent.log.lines:
            self._on_log(line)

        self._draw()
        self._update_status()

    # -- layout ---------------------------------------------------------------

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=PANEL)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.columnconfigure(0, weight=1)

        title_box = tk.Frame(header, bg=PANEL)
        title_box.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        tk.Label(
            title_box, text="AMBULANCE DISPATCH", fg=TEXT_PRIMARY, bg=PANEL, font=self.font_title
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text=f"Track 4  ·  {N}×{N} city  ·  live traffic  ·  Dynamic A*",
            fg=TEXT_SECONDARY,
            bg=PANEL,
            font=self.font_subtitle,
        ).pack(anchor="w", pady=(3, 0))

        status_box = tk.Frame(header, bg=PANEL)
        status_box.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        self.status_dot = tk.Canvas(status_box, width=10, height=10, bg=PANEL, highlightthickness=0)
        self.status_dot.grid(row=0, column=0, padx=(0, 8))
        self._status_dot_id = self.status_dot.create_oval(
            1, 1, 9, 9, fill=StatusStyle.color(Status.RUNNING), outline=""
        )
        self.status_text = tk.StringVar(value="RUNNING")
        tk.Label(
            status_box, textvariable=self.status_text, fg=TEXT_PRIMARY, bg=PANEL,
            font=(self.font_mono, 11, "bold"),
        ).grid(row=0, column=1)

        tk.Frame(self.root, bg=ACCENT, height=2).grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_canvas(self) -> None:
        board_w = N * CELL_PX + MARGIN_LEFT
        board_h = N * CELL_PX + MARGIN_TOP

        wrap = tk.Frame(self.root, bg=PANEL, padx=10, pady=10)
        wrap.grid(row=2, column=0, sticky="nw", padx=12, pady=12)

        self.canvas = tk.Canvas(
            wrap, width=board_w, height=board_h, bg=PANEL_ALT,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.canvas.pack()

    def _build_sidebar(self) -> None:
        side = tk.Frame(self.root, bg=BG)
        side.grid(row=2, column=1, sticky="nsew", padx=(0, 12), pady=12)
        self.root.columnconfigure(1, weight=1)

        # -- live stat cards --
        stats = tk.Frame(side, bg=BG)
        stats.pack(fill="x", pady=(0, 10))
        self.stat_vars = {
            "steps": tk.StringVar(value="0"),
            "replans": tk.StringVar(value="0"),
            "remaining": tk.StringVar(value="-"),
        }
        for i, (key, label) in enumerate([("steps", "STEPS"), ("replans", "REPLANS"), ("remaining", "REMAIN")]):
            card = tk.Frame(stats, bg=PANEL, padx=10, pady=8)
            card.grid(row=0, column=i, sticky="ew", padx=(0, 6) if i < 2 else 0)
            stats.columnconfigure(i, weight=1)
            tk.Label(card, text=label, fg=TEXT_MUTED, bg=PANEL, font=self.font_stat_label).pack(anchor="w")
            tk.Label(
                card, textvariable=self.stat_vars[key], fg=TEXT_PRIMARY, bg=PANEL, font=self.font_stat_value
            ).pack(anchor="w")

        # -- mission log --
        tk.Label(side, text="MISSION LOG", fg=TEXT_SECONDARY, bg=BG, font=self.font_section).pack(anchor="w")

        log_frame = tk.Frame(side, bg=BORDER)
        log_frame.pack(fill="both", expand=True, pady=(4, 10))

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_box = tk.Text(
            log_frame, width=LOG_WIDTH, height=22, bg=PANEL_ALT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, font=self.font_log, wrap="word",
            state="disabled", relief="flat", padx=8, pady=6,
            yscrollcommand=scrollbar.set,
        )
        self.log_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_box.yview)

        # color-code event types so the log reads at a glance
        self.log_box.tag_configure("sense", foreground=COLOR["sensor"])
        self.log_box.tag_configure("traffic", foreground=COLOR["traffic"])
        self.log_box.tag_configure("replan", foreground=COLOR["goal"])
        self.log_box.tag_configure("plan", foreground=COLOR["start"])
        self.log_box.tag_configure("metrics", foreground=TEXT_SECONDARY)
        self.log_box.tag_configure("default", foreground=TEXT_PRIMARY)

        # -- legend --
        tk.Label(side, text="LEGEND", fg=TEXT_SECONDARY, bg=BG, font=self.font_section).pack(anchor="w")
        legend_frame = tk.Frame(side, bg=BG)
        legend_frame.pack(fill="x", pady=(4, 0))
        legend_items = [
            ("free", "road"), ("wall", "building"),
            ("traffic", "traffic jam"), ("path", "route"),
            ("start", "depot"), ("agent", "ambulance"),
            ("goal", "hospital"),
        ]
        for i, (key, label) in enumerate(legend_items):
            row, col = divmod(i, 2)
            item = tk.Frame(legend_frame, bg=BG)
            item.grid(row=row, column=col, sticky="w", padx=(0, 14), pady=2)
            swatch = tk.Canvas(item, width=10, height=10, bg=BG, highlightthickness=0)
            swatch.pack(side="left", padx=(0, 6))
            swatch.create_rectangle(1, 1, 9, 9, fill=COLOR[key], outline="")
            tk.Label(item, text=label, fg=TEXT_SECONDARY, bg=BG, font=self.font_legend).pack(side="left")

    # -- log --------------------------------------------------------------------

    def _on_log(self, line: str) -> None:
        first_line = line.split("\n", 1)[0]
        if "TRAFFIC" in first_line:
            tag = "traffic"
        elif "REPLAN" in first_line:
            tag = "replan"
        elif "PLAN" in first_line:
            tag = "plan"
        elif "SENSE" in first_line:
            tag = "sense"
        elif "----" in first_line:
            tag = "metrics"
        else:
            tag = "default"

        self.log_box.configure(state="normal")
        self.log_box.insert("end", line + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # -- drawing ------------------------------------------------------------------

    def _cell_color(self, cell: tuple[int, int]) -> str:
        agent = self.agent
        if cell == agent.pos:
            return COLOR["agent"]
        if cell == GOAL:
            return COLOR["goal"]
        if cell == START:
            return COLOR["start"]
        if cell in self.world.dynamic:
            return COLOR["traffic"]
        remaining = set(agent.remaining_path()[1:])
        if cell in remaining and cell not in self.world.obstacles:
            return COLOR["path"]
        if cell in self.world.static:
            return COLOR["wall"]
        return COLOR["free"]

    def _draw_ticks(self) -> None:
        step = 5
        for x in range(0, N, step):
            cx = MARGIN_LEFT + x * CELL_PX + CELL_PX / 2
            self.canvas.create_text(cx, MARGIN_TOP / 2, text=str(x), fill=TEXT_MUTED, font=self.font_tick)
        for y in range(0, N, step):
            cy = MARGIN_TOP + y * CELL_PX + CELL_PX / 2
            self.canvas.create_text(MARGIN_LEFT / 2, cy, text=str(y), fill=TEXT_MUTED, font=self.font_tick)

    def _draw(self) -> None:
        self.canvas.delete("all")
        self._draw_ticks()
        for y in range(N):
            for x in range(N):
                x0 = MARGIN_LEFT + x * CELL_PX
                y0 = MARGIN_TOP + y * CELL_PX
                self.canvas.create_rectangle(
                    x0, y0, x0 + CELL_PX, y0 + CELL_PX,
                    fill=self._cell_color((x, y)), outline=GRID_LINE,
                )
                if (x, y) == GOAL:
                    self.canvas.create_text(
                        x0 + CELL_PX / 2, y0 + CELL_PX / 2,
                        text="H", fill="#052e16", font=self.font_legend,
                    )

        ax, ay = self.agent.pos
        pad = 6
        x0 = MARGIN_LEFT + ax * CELL_PX
        y0 = MARGIN_TOP + ay * CELL_PX
        self.canvas.create_oval(
            x0 + pad, y0 + pad, x0 + CELL_PX - pad, y0 + CELL_PX - pad,
            outline="#ffffff", width=2,
        )

    # -- status / metrics --------------------------------------------------------

    def _update_status(self) -> None:
        status = self.agent.status
        self.status_dot.itemconfig(self._status_dot_id, fill=StatusStyle.color(status))
        self.status_text.set(StatusStyle.label(status))
        self.stat_vars["steps"].set(str(self.agent.log.metrics.ticks))
        self.stat_vars["replans"].set(str(self.agent.log.metrics.replans))
        remaining = max(0, len(self.agent.remaining_path()) - 1)
        self.stat_vars["remaining"].set(str(remaining))

    def _pulse(self) -> None:
        if self.agent.status is Status.RUNNING:
            self.agent.tick()
            self._draw()
            self._update_status()
            self.root.after(TICK_MS, self._pulse)
            return
        self._draw()
        self._update_status()
        from .agent import oracle_cost

        self.agent.log.finalize(oracle_cost(self.world))

    def run(self) -> None:
        self.root.after(TICK_MS, self._pulse)
        self.root.mainloop()