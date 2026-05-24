"""Pure-logic Food: random cell, never spawns on the snake."""

from __future__ import annotations

import random
from typing import Iterable

Cell = tuple[int, int]


class Food:
    """A single food pellet that respawns on demand.

    Args:
        grid_width:  number of cells across.
        grid_height: number of cells tall.
        rng:         injectable random.Random for deterministic tests.
    """

    def __init__(
        self,
        grid_width: int,
        grid_height: int,
        rng: random.Random | None = None,
    ) -> None:
        if grid_width < 1 or grid_height < 1:
            raise ValueError(
                f"grid must be ≥ 1×1, got {grid_width}×{grid_height}"
            )
        self.grid_width = grid_width
        self.grid_height = grid_height
        self._rng = rng or random.Random()
        self.position: Cell = (0, 0)
        self.respawn(occupied=())

    def respawn(self, occupied: Iterable[Cell]) -> Cell:
        """Place food at a random cell not in `occupied`.

        Raises:
            RuntimeError: if every cell is occupied (board fully filled).
        """
        occupied_set = set(occupied)
        total_cells = self.grid_width * self.grid_height
        if len(occupied_set) >= total_cells:
            raise RuntimeError("no free cells left to spawn food — you won")

        # Enumerate free cells once; uniform random pick is O(grid).
        free = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in occupied_set
        ]
        self.position = self._rng.choice(free)
        return self.position
