"""SnakeHands — classic Snake, steered with your actual hand.

A camera-controlled Snake game built on Pygame for rendering and
cvzone/MediaPipe for index-finger tracking. Keyboard fallback is
always available so the game runs without a webcam.

Modules:
    config       — runtime constants and tunables
    direction    — Direction enum + 180° turn validation
    snake        — pure game-logic Snake class (no pygame coupling)
    food         — Food class with safe-spawn against snake body
    highscore    — JSON-backed local high-score persistence
    controllers  — HandController + KeyboardController
    renderer     — pygame rendering layer
    game         — main game loop wiring everything together

The pure logic modules (snake, food, direction, highscore) have zero
pygame/cv2/cvzone imports, so they're cheap to unit-test in CI.
"""

__version__ = "1.0.0"
__author__ = "Rayyan Ahmed Shaikh"
__license__ = "MIT"
