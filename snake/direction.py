"""Direction enum and 180° turn validation.

Snake-style games have a classic bug where you press `LEFT` while moving
`RIGHT` and the snake reverses into itself for an instant self-collision.
This module exists to make that bug impossible by construction.
"""

from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """Cardinal directions encoded as (dx, dy) grid deltas."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    def opposite(self) -> "Direction":
        """Return the 180° opposite of this direction."""
        return _OPPOSITES[self]

    def can_turn_to(self, other: "Direction") -> bool:
        """True if turning from `self` to `other` is allowed (no instant reversal)."""
        return other is not self.opposite()


_OPPOSITES: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}
