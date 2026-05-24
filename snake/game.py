"""Game loop — wires controllers + state + renderer together.

This module is the only thing that talks to all subsystems at once.
Everything underneath it is independently testable.
"""

from __future__ import annotations

import sys
from typing import Optional

import pygame

from snake.config import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    DEFAULT_DIFFICULTY,
    DIFFICULTIES,
    GRID_HEIGHT,
    GRID_WIDTH,
    HIGH_SCORE_PATH,
    INITIAL_LENGTH,
    Difficulty,
)
from snake.controllers import KeyboardController
from snake.food import Food
from snake.highscore import HighScoreStore
from snake.snake import Snake


def _try_init_camera_and_hand_controller():
    """Best-effort attempt to open a webcam + start hand tracking.

    Returns (cap, hand_controller) on success, or (None, None) if any step
    fails. The game stays fully playable on keyboard if this returns None.
    """
    try:
        import cv2  # noqa: WPS433

        from snake.controllers import HandController  # noqa: WPS433
    except ImportError as exc:
        print(f"[snakehands] camera input disabled ({exc.name} not installed)")
        return None, None

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[snakehands] camera input disabled (no webcam detected)")
        return None, None
    cap.set(3, CAMERA_WIDTH)
    cap.set(4, CAMERA_HEIGHT)

    try:
        hand = HandController()
    except Exception as exc:  # cvzone / mediapipe init can fail loudly  # noqa: BLE001
        print(f"[snakehands] hand tracker init failed: {exc}")
        cap.release()
        return None, None

    return cap, hand


def run() -> int:
    """Main entry point. Returns shell exit code."""
    from snake.renderer import Renderer  # imported here so headless tests skip pygame

    renderer = Renderer()
    clock = pygame.time.Clock()
    high_scores = HighScoreStore(HIGH_SCORE_PATH)

    cap, hand_controller = _try_init_camera_and_hand_controller()
    camera_available = cap is not None
    camera_active = camera_available  # auto-on if available

    difficulty: Difficulty = DEFAULT_DIFFICULTY
    snake = Snake(GRID_WIDTH, GRID_HEIGHT, initial_length=INITIAL_LENGTH, wrap=difficulty.wrap)
    food = Food(GRID_WIDTH, GRID_HEIGHT)
    food.respawn(occupied=snake.body)
    score = 0
    paused = False
    game_over = False
    is_new_best = False

    def reset() -> None:
        nonlocal snake, food, score, game_over, is_new_best
        snake = Snake(GRID_WIDTH, GRID_HEIGHT, initial_length=INITIAL_LENGTH, wrap=difficulty.wrap)
        food = Food(GRID_WIDTH, GRID_HEIGHT)
        food.respawn(occupied=snake.body)
        score = 0
        game_over = False
        is_new_best = False

    def set_difficulty(d: Difficulty) -> None:
        nonlocal difficulty
        difficulty = d
        reset()

    try:
        while True:
            clock.tick(difficulty.fps)

            # ─── input ──────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return _shutdown(renderer, cap)
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return _shutdown(renderer, cap)
                if event.key == pygame.K_r and game_over:
                    reset()
                    continue
                if event.key == pygame.K_SPACE and not game_over:
                    paused = not paused
                    continue
                if event.key == pygame.K_c and camera_available:
                    camera_active = not camera_active
                    continue
                # 1 / 2 / 3 select difficulty (also resets the round)
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    if idx < len(DIFFICULTIES):
                        set_difficulty(DIFFICULTIES[idx])
                        continue
                # Direction keys
                direction = KeyboardController.from_pygame_key(event.key)
                if direction is not None and not paused and not game_over:
                    snake.change_direction(direction)

            # ─── hand input ─────────────────────────────────────────────────
            if camera_active and cap is not None and hand_controller is not None and not paused and not game_over:
                import cv2  # noqa: WPS433

                ok, frame = cap.read()
                if ok:
                    frame = cv2.flip(frame, 1)
                    direction, annotated = hand_controller.update(frame)
                    if direction is not None:
                        snake.change_direction(direction)
                    cv2.imshow("Hand Tracking", annotated)
                    cv2.waitKey(1)

            # ─── tick world ─────────────────────────────────────────────────
            if not paused and not game_over:
                if not snake.step():
                    game_over = True
                    is_new_best = high_scores.submit(difficulty.name, score)
                elif snake.head == food.position:
                    snake.grow()
                    score += 10 * difficulty.score_multiplier
                    # If the board is full, respawn would raise; treat that as a win.
                    try:
                        food.respawn(occupied=snake.body)
                    except RuntimeError:
                        game_over = True
                        is_new_best = high_scores.submit(difficulty.name, score)

            # ─── render ─────────────────────────────────────────────────────
            renderer.begin_frame()
            renderer.draw_snake(snake)
            renderer.draw_food(food)
            renderer.draw_hud(
                score=score,
                high_score=high_scores.get(difficulty.name),
                difficulty_name=difficulty.name,
                camera_active=camera_active,
                paused=paused,
            )
            if game_over:
                renderer.draw_game_over(score=score, is_new_best=is_new_best)
            renderer.end_frame()

    except KeyboardInterrupt:
        return _shutdown(renderer, cap)


def _shutdown(renderer, cap) -> int:
    if cap is not None:
        cap.release()
        try:
            import cv2  # noqa: WPS433
            cv2.destroyAllWindows()
        except ImportError:
            pass
    renderer.quit()
    return 0


if __name__ == "__main__":
    sys.exit(run())
