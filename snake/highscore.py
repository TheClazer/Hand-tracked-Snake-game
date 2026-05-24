"""JSON-backed local high-score persistence.

The store lives at `~/.snakehands/highscore.json` (overridable for tests).
It's per-difficulty so EASY/NORMAL/HARD each track their own best.

The file is tolerant: corrupt or missing JSON just resets to empty rather
than crashing the game.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


class HighScoreStore:
    """Per-difficulty high score, persisted as JSON."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._scores: dict[str, int] = {}
        self._load()

    # ─── public API ──────────────────────────────────────────────────────────

    def get(self, difficulty_name: str) -> int:
        """Return the best score for this difficulty (0 if never played)."""
        return self._scores.get(difficulty_name, 0)

    def all(self) -> Mapping[str, int]:
        """All difficulty → score pairs."""
        return dict(self._scores)

    def submit(self, difficulty_name: str, score: int) -> bool:
        """Submit a score. Returns True if it was a new best."""
        if score > self._scores.get(difficulty_name, 0):
            self._scores[difficulty_name] = score
            self._save()
            return True
        return False

    # ─── internals ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.path.exists():
            self._scores = {}
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._scores = {}
            return
        if not isinstance(data, dict):
            self._scores = {}
            return
        # Coerce values defensively — anything non-int gets dropped.
        self._scores = {
            str(k): int(v)
            for k, v in data.items()
            if isinstance(v, (int, float)) and v >= 0
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._scores, indent=2, sort_keys=True),
            encoding="utf-8",
        )
