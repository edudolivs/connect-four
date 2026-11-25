"""Adversarial search. Step 3: plain minimax to a fixed depth (no pruning yet)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .board import Board
from .evaluate import evaluate

WIN_SCORE = 1000

EvalFn = Callable[[Board, int], int]


@dataclass
class SearchResult:
    move: int | None  # best column, or None when the position is already over
    score: int  # from the searching player's point of view
    nodes: int  # positions visited, root included


def minimax(board: Board, depth: int, player: int, evaluate_fn: EvalFn = evaluate) -> SearchResult:
    """Best move for ``player`` looking ``depth`` plies ahead. Leaves the board unchanged.

    Wins score ``WIN_SCORE + plies left``, so faster wins (and slower losses) are preferred.
    Ties keep the first move in ``legal_moves()`` order, which is center-first.
    """
    if depth < 0:
        raise ValueError("depth must be at least 0")
    nodes = 0

    def search(depth_left: int) -> tuple[int, int | None]:
        nonlocal nodes
        nodes += 1
        winner = board.winner()
        if winner is not None:
            score = WIN_SCORE + depth_left
            return (score if winner == player else -score), None
        if board.is_full():
            return 0, None
        if depth_left == 0:
            return evaluate_fn(board, player), None

        maximizing = board.current_player == player
        best_score, best_move = None, None
        for col in board.legal_moves():
            board.play(col)
            try:
                score, _ = search(depth_left - 1)
            finally:
                board.undo()
            if best_score is None or (score > best_score if maximizing else score < best_score):
                best_score, best_move = score, col
        return best_score, best_move

    score, move = search(depth)
    return SearchResult(move, score, nodes)
