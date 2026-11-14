"""Text rendering of a board, with optional ANSI colors."""

from __future__ import annotations

import os
import sys

from .board import COLS, EMPTY, RED, ROWS, YELLOW, Board

RESET = "\x1b[0m"
_ANSI = {RED: "\x1b[1;31m", YELLOW: "\x1b[1;33m"}
_DIM = "\x1b[2m"

_PLAIN = {EMPTY: ".", RED: "X", YELLOW: "O"}
_NAMES = {RED: "Red", YELLOW: "Yellow"}


def use_color(stream=None) -> bool:
    """Colors on unless NO_COLOR is set or the stream is not a terminal."""
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def piece(player: int, color: bool) -> str:
    if not color:
        return _PLAIN[player]
    if player == EMPTY:
        return f"{_DIM}·{RESET}"
    return f"{_ANSI[player]}●{RESET}"


def player_name(player: int, color: bool) -> str:
    name = _NAMES[player]
    return f"{_ANSI[player]}{name}{RESET}" if color else f"{name} ({_PLAIN[player]})"


def render(board: Board, color: bool = True) -> str:
    lines = []
    for row in range(ROWS - 1, -1, -1):
        cells = " | ".join(piece(board.cell(row, col), color) for col in range(COLS))
        lines.append(f"| {cells} |")
    lines.append("".join(f"  {col + 1} " for col in range(COLS)).rstrip())
    return "\n".join(lines)
