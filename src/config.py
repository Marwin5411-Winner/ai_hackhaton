"""Locked constants from the Technical Summary Sheet."""

N = 15
SENSOR_R = 2  # Chebyshev radius
START = (0, 0)
GOAL = (14, 14)
TICK_MS = 180  # viz delay so movement is camera-visible
MAX_TICKS = N * N * 4  # hard stop against infinite wander

# 4-connected unit moves. Order biases A* toward the goal (right/down first).
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP = (0, -1)
ACTIONS = (RIGHT, DOWN, LEFT, UP)
ACTION_NAMES = {
    RIGHT: "MOVE_RIGHT",
    DOWN: "MOVE_DOWN",
    LEFT: "MOVE_LEFT",
    UP: "MOVE_UP",
}

CELL_PX = 32
LOG_WIDTH = 42
