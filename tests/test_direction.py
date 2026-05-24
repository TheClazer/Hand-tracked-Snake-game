"""Tests for the Direction enum + turn validation."""

from __future__ import annotations

import pytest

from snake.direction import Direction


def test_opposite_is_symmetric() -> None:
    for d in Direction:
        assert d.opposite().opposite() is d


@pytest.mark.parametrize(
    "a,b",
    [
        (Direction.UP, Direction.DOWN),
        (Direction.DOWN, Direction.UP),
        (Direction.LEFT, Direction.RIGHT),
        (Direction.RIGHT, Direction.LEFT),
    ],
)
def test_opposites_blocked(a: Direction, b: Direction) -> None:
    assert not a.can_turn_to(b)


@pytest.mark.parametrize(
    "a,b",
    [
        (Direction.UP, Direction.LEFT),
        (Direction.UP, Direction.RIGHT),
        (Direction.DOWN, Direction.LEFT),
        (Direction.DOWN, Direction.RIGHT),
        (Direction.LEFT, Direction.UP),
        (Direction.LEFT, Direction.DOWN),
        (Direction.RIGHT, Direction.UP),
        (Direction.RIGHT, Direction.DOWN),
    ],
)
def test_perpendicular_turns_allowed(a: Direction, b: Direction) -> None:
    assert a.can_turn_to(b)


def test_turning_to_self_allowed() -> None:
    """No-op turns shouldn't be blocked — only 180° reversals."""
    for d in Direction:
        assert d.can_turn_to(d)


def test_deltas() -> None:
    assert Direction.UP.dx == 0 and Direction.UP.dy == -1
    assert Direction.DOWN.dx == 0 and Direction.DOWN.dy == 1
    assert Direction.LEFT.dx == -1 and Direction.LEFT.dy == 0
    assert Direction.RIGHT.dx == 1 and Direction.RIGHT.dy == 0
