"""Shared pytest fixtures."""

from __future__ import annotations

import random
from pathlib import Path

import pytest


@pytest.fixture
def deterministic_rng() -> random.Random:
    """A seeded RNG so Food.respawn is repeatable in tests."""
    return random.Random(42)


@pytest.fixture
def tmp_highscore_path(tmp_path: Path) -> Path:
    """A temp file path for HighScoreStore that's isolated per test."""
    return tmp_path / "scores.json"
