"""Tests for HighScoreStore persistence."""

from __future__ import annotations

from pathlib import Path

from snake.highscore import HighScoreStore


def test_empty_when_no_file(tmp_highscore_path: Path) -> None:
    store = HighScoreStore(tmp_highscore_path)
    assert store.get("NORMAL") == 0
    assert store.all() == {}


def test_submit_new_best(tmp_highscore_path: Path) -> None:
    store = HighScoreStore(tmp_highscore_path)
    assert store.submit("NORMAL", 100) is True
    assert store.get("NORMAL") == 100


def test_submit_lower_score_rejected(tmp_highscore_path: Path) -> None:
    store = HighScoreStore(tmp_highscore_path)
    store.submit("NORMAL", 100)
    assert store.submit("NORMAL", 50) is False
    assert store.get("NORMAL") == 100


def test_persists_across_instances(tmp_highscore_path: Path) -> None:
    HighScoreStore(tmp_highscore_path).submit("HARD", 250)
    fresh = HighScoreStore(tmp_highscore_path)
    assert fresh.get("HARD") == 250


def test_per_difficulty_isolation(tmp_highscore_path: Path) -> None:
    store = HighScoreStore(tmp_highscore_path)
    store.submit("EASY", 50)
    store.submit("HARD", 200)
    assert store.get("EASY") == 50
    assert store.get("NORMAL") == 0
    assert store.get("HARD") == 200


def test_corrupt_json_resets_silently(tmp_highscore_path: Path) -> None:
    tmp_highscore_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_highscore_path.write_text("{this is not valid json", encoding="utf-8")
    store = HighScoreStore(tmp_highscore_path)
    assert store.all() == {}  # didn't crash, just empty


def test_non_dict_json_resets_silently(tmp_highscore_path: Path) -> None:
    tmp_highscore_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_highscore_path.write_text("[1, 2, 3]", encoding="utf-8")
    store = HighScoreStore(tmp_highscore_path)
    assert store.all() == {}


def test_negative_scores_dropped_on_load(tmp_highscore_path: Path) -> None:
    tmp_highscore_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_highscore_path.write_text('{"EASY": -10, "HARD": 50}', encoding="utf-8")
    store = HighScoreStore(tmp_highscore_path)
    assert store.get("EASY") == 0
    assert store.get("HARD") == 50
