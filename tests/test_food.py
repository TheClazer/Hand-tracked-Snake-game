"""Tests for the Food class."""

from __future__ import annotations

import random

import pytest

from snake.food import Food


def test_spawn_inside_grid(deterministic_rng: random.Random) -> None:
    f = Food(10, 8, rng=deterministic_rng)
    x, y = f.position
    assert 0 <= x < 10
    assert 0 <= y < 8


def test_respawn_avoids_occupied_cells(deterministic_rng: random.Random) -> None:
    occupied = [(x, 0) for x in range(10)]  # entire top row taken
    f = Food(10, 8, rng=deterministic_rng)
    pos = f.respawn(occupied)
    assert pos not in occupied
    assert pos[1] != 0  # must be off the top row


def test_respawn_fills_board_raises(deterministic_rng: random.Random) -> None:
    occupied = [(x, y) for x in range(2) for y in range(2)]  # 2x2 fully occupied
    f = Food(2, 2, rng=deterministic_rng)
    with pytest.raises(RuntimeError):
        f.respawn(occupied)


def test_invalid_grid_raises() -> None:
    with pytest.raises(ValueError):
        Food(0, 5)
    with pytest.raises(ValueError):
        Food(5, 0)


def test_respawn_is_deterministic_with_seed() -> None:
    """Same seed + same occupied set → same position. Important for reproducible tests."""
    f1 = Food(10, 10, rng=random.Random(123))
    f2 = Food(10, 10, rng=random.Random(123))
    assert f1.position == f2.position
    assert f1.respawn(occupied=[(0, 0)]) == f2.respawn(occupied=[(0, 0)])
