"""Adversarial search: plain minimax (step 3) and alpha-beta pruning with move ordering (step 4)."""

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


def alphabeta(
    board: Board,
    depth: int,
    player: int,
    evaluate_fn: EvalFn = evaluate,
    ordered: bool = True,
) -> SearchResult:
    """Same result as ``minimax`` (move and score), visiting fewer nodes.

    Branches that cannot change the decision are cut: ``alpha`` is the best score ``player`` is
    already sure of, ``beta`` the best the opponent is sure of; once ``alpha >= beta`` the rest of
    that node's moves are skipped. Pruning works best when good moves come first, so moves are
    tried center-first (``ordered=True``, the order of ``legal_moves()``); ``ordered=False`` tries
    them left to right, to measure what ordering is worth.
    """
    if depth < 0:
        raise ValueError("depth must be at least 0")
    nodes = 0

    def moves() -> list[int]:
        legal = board.legal_moves()
        return legal if ordered else sorted(legal)

    def search(depth_left: int, alpha: float, beta: float) -> tuple[int, int | None]:
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
        for col in moves():
            board.play(col)
            try:
                score, _ = search(depth_left - 1, alpha, beta)
            finally:
                board.undo()
            # Strict comparison keeps the first best move, exactly like minimax.
            if best_score is None or (score > best_score if maximizing else score < best_score):
                best_score, best_move = score, col
            if maximizing:
                alpha = max(alpha, best_score)
            else:
                beta = min(beta, best_score)
            if alpha >= beta:
                break
        return best_score, best_move

    score, move = search(depth, float("-inf"), float("inf"))
    return SearchResult(move, score, nodes)
