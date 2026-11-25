"""Heuristic for non-terminal positions. A simple first version; step 5 refines it."""

from __future__ import annotations

from dataclasses import dataclass

from .board import COLS, CONNECT, EMPTY, ROWS, Board, other


@dataclass(frozen=True)
class Weights:
    """Points per feature, kept as parameters so they can be tuned in experiments."""

    three: int = 5  # own window with 3 pieces and 1 empty cell
    two: int = 2  # own window with 2 pieces and 2 empty cells
    opp_three: int = 4  # opponent window with 3 pieces and 1 empty cell (subtracted)
    center: int = 3  # per own piece in the center column


DEFAULT_WEIGHTS = Weights()
CENTER_COL = COLS // 2


def _windows() -> tuple[tuple[tuple[int, int], ...], ...]:
    """Every line of four cells on the board: 24 horizontal, 21 vertical, 12 + 12 diagonal."""
    windows = []
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        for row in range(ROWS):
            for col in range(COLS):
                cells = tuple((row + i * dr, col + i * dc) for i in range(CONNECT))
                if all(0 <= r < ROWS and 0 <= c < COLS for r, c in cells):
                    windows.append(cells)
    return tuple(windows)


WINDOWS = _windows()


def evaluate(board: Board, player: int, weights: Weights = DEFAULT_WEIGHTS) -> int:
    """Score the position from ``player``'s point of view (positive = good for ``player``)."""
    opponent = other(player)
    score = weights.center * sum(board.cell(row, CENTER_COL) == player for row in range(ROWS))
    for window in WINDOWS:
        pieces = [board.cell(r, c) for r, c in window]
        mine = pieces.count(player)
        theirs = pieces.count(opponent)
        empty = pieces.count(EMPTY)
        if theirs == 0:
            if mine == 3 and empty == 1:
                score += weights.three
            elif mine == 2 and empty == 2:
                score += weights.two
        elif mine == 0 and theirs == 3 and empty == 1:
            score -= weights.opp_three
    return score
