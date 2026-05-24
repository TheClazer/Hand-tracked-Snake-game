<div align="center">

# SnakeHands

**Classic Snake. Steered with your actual hand.**

A camera-controlled Snake game where you point your index finger and the snake follows. Built on Pygame for rendering and cvzone / MediaPipe for real-time hand landmark detection. Keyboard always works as a fallback.

[![CI](https://github.com/TheClazer/Hand-tracked-Snake-game/actions/workflows/ci.yml/badge.svg)](https://github.com/TheClazer/Hand-tracked-Snake-game/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-d4bbff?style=flat-square)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-c084fc?style=flat-square)](https://github.com/astral-sh/ruff)
[![Typed: mypy](https://img.shields.io/badge/typed-mypy-7aa2f7?style=flat-square)](https://mypy.readthedocs.io/)

</div>

---

## What it is

A Saturday-night project that turned into a real one. Point your index finger at your webcam, swipe in any of the four cardinal directions, and the snake follows. The camera feed runs in a tiny side window so you can see what the hand tracker sees.

If you don't have (or don't want) a webcam, arrow keys / WASD work the entire time. The game auto-detects camera availability at startup — if anything fails (no webcam, no permissions, OpenCV not installed), it just disables hand input and keeps going.

## Features

- **Hand-tracking input** via cvzone's HandDetector (MediaPipe under the hood) — index-finger position → direction
- **Keyboard fallback** always on (Arrow keys + WASD)
- **Three difficulty levels** — Easy (10 fps, wrap), Normal (15 fps, wrap), Hard (22 fps, hard walls)
- **Per-difficulty high score** persisted to `~/.snakehands/highscore.json`
- **Toggleable camera** mid-game (`C` key)
- **Pause** mid-round (`Space`)
- **Instant 180° turn protection** — no more pressing LEFT while moving RIGHT and dying instantly
- **Headless-friendly architecture** — pure game logic has no pygame/cv2 imports, so CI tests run on a Linux box with no display
- **`pip install -e .` installable** — gives you a `snakehands` command

## Quick start

### 1. Install

Requires **Python 3.11 or newer** and a working webcam (optional — keyboard mode works without one).

```bash
git clone https://github.com/TheClazer/Hand-tracked-Snake-game.git
cd Hand-tracked-Snake-game
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
```

### 2. Play

```bash
snakehands
# or, equivalently:
python -m snake
```

## Controls

| Action | Hand | Keyboard |
|---|---|---|
| Move up | Swipe index finger up | `↑` or `W` |
| Move down | Swipe index finger down | `↓` or `S` |
| Move left | Swipe index finger left | `←` or `A` |
| Move right | Swipe index finger right | `→` or `D` |
| Pause / Resume | — | `Space` |
| Toggle camera | — | `C` |
| Restart after game over | — | `R` |
| Quit | — | `Esc` or window close |
| Easy difficulty | — | `1` |
| Normal difficulty | — | `2` |
| Hard difficulty | — | `3` |

> Switching difficulty mid-game resets the round.

## Difficulty modes

| Mode | FPS | Walls | Score multiplier | Vibes |
|---|---:|---|---:|---|
| **Easy** | 10 | Wrap around | ×1 | Coffee in hand |
| **Normal** | 15 | Wrap around | ×2 | The default |
| **Hard** | 22 | Hard walls (you die on contact) | ×4 | Webcam shaking |

## Architecture

The codebase is deliberately split so the game logic can be unit-tested without a display or webcam.

```
snake/
├── __main__.py      # `python -m snake` entry
├── config.py        # constants + Difficulty dataclass
├── direction.py     # Direction enum + 180° turn guard
├── snake.py         # pure Snake class (no pygame imports)
├── food.py          # pure Food class (no pygame imports)
├── highscore.py     # JSON-backed high score store
├── controllers.py   # KeyboardController + HandController (lazy cvzone import)
├── renderer.py      # pygame rendering layer
└── game.py          # main loop wiring all of the above
```

The rule of the codebase: **anything in `snake.py`, `food.py`, `direction.py`, `highscore.py`, or `config.py` must not import pygame, cv2, or cvzone.** That keeps tests fast and lets the package install in environments without OpenCV.

## Development

### Run the test suite

```bash
pip install -e ".[dev]"
pytest
```

Tests cover Snake movement, growth, collision, 180° turn rejection, Food respawn (including the no-spawn-on-snake invariant), HighScoreStore persistence + corruption tolerance, and the Direction enum.

### Lint + type check

```bash
ruff check snake tests
mypy snake
```

### CI

Every push to `main` and every PR runs on Python 3.11 and 3.12, lints with ruff, type-checks with mypy, and runs the full test suite in a headless Xvfb-backed display. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Troubleshooting

**The camera window opens but the snake doesn't react.**
Make sure your index finger is clearly in the camera frame and well-lit. The detector needs ≥80% confidence to register a hand. Try raising your hand against a plain background.

**`pip install mediapipe` fails on Python 3.13.**
MediaPipe doesn't yet ship wheels for Python 3.13. Use 3.11 or 3.12. The `.python-version` in this repo pins to 3.11.

**No webcam detected — game starts in keyboard-only mode.**
That's expected behavior. Connect a webcam and restart the game.

**On Linux, `pygame` errors with `ALSA lib confmisc.c:855:(parse_card)`.**
That's a noisy ALSA warning, not a real error — the game still runs. To silence it, add a null PulseAudio sink or run with `SDL_AUDIODRIVER=dummy`.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Built by [Rayyan Ahmed Shaikh](https://github.com/TheClazer) at R.V. College of Engineering, Bangalore. PRs welcome.</sub>
