"""Pure game-logic Snake — no pygame or cv2 imports, fully unit-testable."""

from __future__ import annotations

from collections import deque
from typing import Iterable

from snake.direction import Direction


# Type aliases for clarity; the snake body is just a deque of (x, y) tuples.
Cell = tuple[int, int]


class Snake:
    """The classic Snake. Pure logic, no rendering.

    Args:
        grid_width:  number of cells across.
        grid_height: number of cells tall.
        initial_length: how many body segments the snake spawns with.
        wrap: if True the snake teleports across edges; if False it dies on wall hit.
    """

    def __init__(
        self,
        grid_width: int,
        grid_height: int,
        initial_length: int = 3,
        *,
        wrap: bool = True,
    ) -> None:
        if grid_width < initial_length:
            raise ValueError(
                f"grid_width ({grid_width}) must be ≥ initial_length ({initial_length})"
            )
        if initial_length < 1:
            raise ValueError(f"initial_length must be ≥ 1, got {initial_length}")

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.wrap = wrap

        # Spawn horizontally near the center, head on the right
        start_x = grid_width // 2
        start_y = grid_height // 2
        self.body: deque[Cell] = deque(
            (start_x - i, start_y) for i in range(initial_length)
        )

        self._direction: Direction = Direction.RIGHT
        self._grow_pending: bool = False

    # ─── public API ──────────────────────────────────────────────────────────

    @property
    def head(self) -> Cell:
        return self.body[0]

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def length(self) -> int:
        return len(self.body)

    def change_direction(self, new_direction: Direction) -> bool:
        """Try to change direction. Returns True if accepted, False if blocked
        (e.g. instant 180° reversal)."""
        if self._direction.can_turn_to(new_direction):
            self._direction = new_direction
            return True
        return False

    def grow(self) -> None:
        """Queue a single segment of growth on the next move."""
        self._grow_pending = True

    def step(self) -> bool:
        """Advance one cell. Returns True if alive, False on collision.

        Self-collision: head into any body cell.
        Wall collision: head past grid edge when `wrap=False`.
        """
        hx, hy = self.head
        nx, ny = hx + self._direction.dx, hy + self._direction.dy

        if self.wrap:
            nx %= self.grid_width
            ny %= self.grid_height
        elif not (0 <= nx < self.grid_width and 0 <= ny < self.grid_height):
            return False  # hit the wall

        new_head: Cell = (nx, ny)

        # Tail-tip is about to leave when we don't grow — skip it from collision check
        body_to_check: Iterable[Cell] = (
            list(self.body) if self._grow_pending else list(self.body)[:-1]
        )
        if new_head in body_to_check:
            return False  # ate itself

        self.body.appendleft(new_head)
        if self._grow_pending:
            self._grow_pending = False
        else:
            self.body.pop()
        return True

    def overlaps(self, cell: Cell) -> bool:
        """True if `cell` is anywhere on the snake (head or body)."""
        return cell in self.body
