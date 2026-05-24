"""Runtime constants and tunables.

Everything in here is intentionally a module-level constant so unit tests
and the renderer can import without side effects. If you want to tweak
gameplay (faster snake, smaller grid, harsher self-collision), this is
the only file you should need to touch.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# ─── window ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

# ─── grid ────────────────────────────────────────────────────────────────────
GRID_SIZE: int = 20  # pixels per cell
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE   # 40
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE  # 30

# ─── colors (RGB) ────────────────────────────────────────────────────────────
BLACK: tuple[int, int, int] = (0, 0, 0)
WHITE: tuple[int, int, int] = (255, 255, 255)
GRID_LINE: tuple[int, int, int] = (40, 40, 40)
SNAKE_HEAD: tuple[int, int, int] = (255, 80, 80)
SNAKE_BODY: tuple[int, int, int] = (80, 220, 100)
FOOD: tuple[int, int, int] = (90, 140, 255)
HUD_TEXT: tuple[int, int, int] = (240, 240, 240)
GAME_OVER_RED: tuple[int, int, int] = (255, 60, 60)

# ─── snake ───────────────────────────────────────────────────────────────────
INITIAL_LENGTH: int = 3

# ─── hand tracking ───────────────────────────────────────────────────────────
DETECTION_CONFIDENCE: float = 0.8
MAX_HANDS: int = 1
DIRECTION_THRESHOLD: int = 30  # pixels of finger travel before re-arming a turn
CAMERA_WIDTH: int = 640
CAMERA_HEIGHT: int = 480

# ─── persistence ─────────────────────────────────────────────────────────────
HIGH_SCORE_PATH: Path = Path.home() / ".snakehands" / "highscore.json"


# ─── difficulty ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Difficulty:
    """A named gameplay difficulty.

    `fps` controls snake speed — Pygame frames-per-second. `wrap` controls
    whether the snake teleports across edges (True) or dies on wall hit (False).
    `score_multiplier` makes harder modes worth more points per food.
    """

    name: str
    fps: int
    wrap: bool
    score_multiplier: int


EASY = Difficulty(name="EASY",   fps=10, wrap=True,  score_multiplier=1)
NORMAL = Difficulty(name="NORMAL", fps=15, wrap=True,  score_multiplier=2)
HARD = Difficulty(name="HARD",   fps=22, wrap=False, score_multiplier=4)

DIFFICULTIES: tuple[Difficulty, ...] = (EASY, NORMAL, HARD)
DEFAULT_DIFFICULTY: Difficulty = NORMAL
