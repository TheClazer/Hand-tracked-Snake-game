"""Input controllers: keyboard (always-on) + hand tracking (optional).

The HandController imports cvzone lazily so the rest of the game can
import this module on a machine without OpenCV/MediaPipe installed
(useful for headless CI test runs).
"""

from __future__ import annotations

from typing import Any, Optional

from snake.config import DETECTION_CONFIDENCE, DIRECTION_THRESHOLD, MAX_HANDS
from snake.direction import Direction


class KeyboardController:
    """Arrow / WASD → Direction. Stateless."""

    KEY_MAP_PYGAME: dict[int, Direction] = {}  # populated at runtime to avoid import cycle

    @classmethod
    def from_pygame_key(cls, key: int) -> Optional[Direction]:
        """Map a pygame key constant to a Direction (or None)."""
        # Imported here to keep this module pygame-free at import time.
        import pygame  # noqa: WPS433 — intentional local import

        if not cls.KEY_MAP_PYGAME:
            cls.KEY_MAP_PYGAME = {
                pygame.K_UP: Direction.UP,
                pygame.K_w: Direction.UP,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_s: Direction.DOWN,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_a: Direction.LEFT,
                pygame.K_RIGHT: Direction.RIGHT,
                pygame.K_d: Direction.RIGHT,
            }
        return cls.KEY_MAP_PYGAME.get(key)


class HandController:
    """Index-finger position → Direction via cvzone HandDetector.

    Tracks the dominant motion delta since the last accepted direction.
    Only emits a new direction when the finger has moved more than
    `DIRECTION_THRESHOLD` pixels along the dominant axis since the last
    sample — this debounces shaky hand input.
    """

    def __init__(
        self,
        detection_confidence: float = DETECTION_CONFIDENCE,
        max_hands: int = MAX_HANDS,
        threshold: int = DIRECTION_THRESHOLD,
    ) -> None:
        # Lazy import so unit tests can import this file without cvzone installed.
        from cvzone.HandTrackingModule import HandDetector  # noqa: WPS433

        self._detector = HandDetector(
            detectionCon=detection_confidence, maxHands=max_hands
        )
        self._prev_position: Optional[tuple[int, int]] = None
        self._current_direction: Optional[Direction] = None
        self._threshold = threshold

    def update(self, frame: Any) -> tuple[Optional[Direction], Any]:
        """Process one camera frame. Returns `(direction, annotated_frame)`.

        `direction` is None until a confident gesture is read.
        """
        hands, annotated = self._detector.findHands(frame, draw=True)

        if not hands:
            return self._current_direction, annotated

        # Landmark 8 = index finger tip
        index_tip = hands[0]["lmList"][8]
        x, y = int(index_tip[0]), int(index_tip[1])

        if self._prev_position is None:
            self._prev_position = (x, y)
            return self._current_direction, annotated

        dx = x - self._prev_position[0]
        dy = y - self._prev_position[1]

        if abs(dx) > self._threshold or abs(dy) > self._threshold:
            if abs(dx) > abs(dy):
                self._current_direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self._current_direction = Direction.DOWN if dy > 0 else Direction.UP
            self._prev_position = (x, y)

        return self._current_direction, annotated
