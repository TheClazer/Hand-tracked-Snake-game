"""Pygame rendering layer — the only module that knows how to draw pixels.

Kept thin on purpose: every method takes the game state it needs as
arguments and returns nothing. Game-logic modules (snake, food, etc.)
never import from here.
"""

from __future__ import annotations

import pygame

from snake.config import (
    BLACK,
    FOOD,
    GAME_OVER_RED,
    GRID_LINE,
    GRID_SIZE,
    HUD_TEXT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SNAKE_BODY,
    SNAKE_HEAD,
    WHITE,
)
from snake.food import Food
from snake.snake import Snake


class Renderer:
    """Owns the pygame surface and draws the game state."""

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SnakeHands")
        self._hud_font = pygame.font.Font(None, 32)
        self._title_font = pygame.font.Font(None, 72)
        self._small_font = pygame.font.Font(None, 24)

    # ─── frame composition ──────────────────────────────────────────────────

    def begin_frame(self) -> None:
        self.screen.fill(BLACK)
        self._draw_grid()

    def end_frame(self) -> None:
        pygame.display.flip()

    # ─── world ──────────────────────────────────────────────────────────────

    def draw_snake(self, snake: Snake) -> None:
        for i, (gx, gy) in enumerate(snake.body):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(
                self.screen,
                color,
                (gx * GRID_SIZE, gy * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2),
                border_radius=4,
            )

    def draw_food(self, food: Food) -> None:
        cx = food.position[0] * GRID_SIZE + GRID_SIZE // 2
        cy = food.position[1] * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(self.screen, FOOD, (cx, cy), GRID_SIZE // 2 - 2)

    # ─── HUD ────────────────────────────────────────────────────────────────

    def draw_hud(
        self,
        *,
        score: int,
        high_score: int,
        difficulty_name: str,
        camera_active: bool,
        paused: bool,
    ) -> None:
        score_text = self._hud_font.render(
            f"Score {score}    Best {high_score}    [{difficulty_name}]",
            True,
            HUD_TEXT,
        )
        self.screen.blit(score_text, (10, 8))

        hints = []
        if paused:
            hints.append("PAUSED — Space to resume")
        else:
            hints.append("Space: pause")
        hints.append("C: camera " + ("ON" if camera_active else "OFF"))
        hints.append("1/2/3: difficulty")
        hints.append("Esc: quit")
        hint_surf = self._small_font.render("   ".join(hints), True, HUD_TEXT)
        self.screen.blit(hint_surf, (10, SCREEN_HEIGHT - 26))

    def draw_game_over(self, *, score: int, is_new_best: bool) -> None:
        title = self._title_font.render("GAME OVER", True, GAME_OVER_RED)
        score_line = self._hud_font.render(f"Final score: {score}", True, WHITE)
        if is_new_best:
            extra = self._hud_font.render("NEW BEST!", True, FOOD)
        else:
            extra = self._small_font.render("Press R to restart, Esc to quit", True, WHITE)

        cx = SCREEN_WIDTH // 2
        self.screen.blit(title, (cx - title.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
        self.screen.blit(score_line, (cx - score_line.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(extra, (cx - extra.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        if is_new_best:
            restart = self._small_font.render("Press R to restart, Esc to quit", True, WHITE)
            self.screen.blit(restart, (cx - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 90))

    # ─── internals ──────────────────────────────────────────────────────────

    def _draw_grid(self) -> None:
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (SCREEN_WIDTH, y))

    def quit(self) -> None:
        pygame.quit()
