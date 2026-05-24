"""Sanity tests for config module — catches accidental constant drift."""

from __future__ import annotations

from snake.config import (
    DEFAULT_DIFFICULTY,
    DIFFICULTIES,
    EASY,
    GRID_HEIGHT,
    GRID_SIZE,
    GRID_WIDTH,
    HARD,
    NORMAL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def test_grid_divides_screen_cleanly() -> None:
    assert SCREEN_WIDTH % GRID_SIZE == 0
    assert SCREEN_HEIGHT % GRID_SIZE == 0
    assert GRID_WIDTH == SCREEN_WIDTH // GRID_SIZE
    assert GRID_HEIGHT == SCREEN_HEIGHT // GRID_SIZE


def test_difficulties_are_distinct_and_ordered() -> None:
    fps_values = [d.fps for d in DIFFICULTIES]
    assert fps_values == sorted(fps_values), "DIFFICULTIES should be slow→fast"
    names = [d.name for d in DIFFICULTIES]
    assert len(set(names)) == len(names), "duplicate difficulty names"


def test_default_difficulty_is_in_list() -> None:
    assert DEFAULT_DIFFICULTY in DIFFICULTIES


def test_score_multipliers_make_sense() -> None:
    assert EASY.score_multiplier < NORMAL.score_multiplier < HARD.score_multiplier
