"""Players. Every agent picks a 0-based column via ``choose_move(board)``."""

from __future__ import annotations

import random
from typing import Callable, Protocol

from .board import COLS, Board, other
from .evaluate import DEFAULT_WEIGHTS, Weights, evaluate
from .search import SearchResult, minimax

KINDS = ("human", "random", "greedy", "minimax")
BOT_KINDS = ("random", "greedy", "minimax")
DEFAULT_DEPTH = 4


class Agent(Protocol):
    name: str
    is_human: bool

    def choose_move(self, board: Board) -> int: ...


class HumanAgent:
    """Asks a person in the terminal for a column (1-7)."""

    is_human = True

    def __init__(
        self,
        name: str,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[[str], None] = print,
    ) -> None:
        self.name = name
        self._input = input_fn
        self._print = print_fn

    def choose_move(self, board: Board) -> int:
        while True:
            answer = self._input(f"{self.name}, choose a column (1-{COLS}): ").strip()
            if not answer.isdigit() or not 1 <= int(answer) <= COLS:
                self._print(f"Please type a number from 1 to {COLS}.")
                continue
            col = int(answer) - 1
            if not board.is_legal(col):
                self._print(f"Column {answer} is full. Pick another.")
                continue
            return col


class RandomAgent:
    """Plays a uniformly random legal column."""

    is_human = False

    def __init__(self, name: str = "Random", rng: random.Random | None = None) -> None:
        self.name = name
        self._rng = rng or random.Random()

    def choose_move(self, board: Board) -> int:
        return self._rng.choice(board.legal_moves())


class GreedyAgent:
    """Looks one move ahead: win if possible, else block, else avoid gifting a win, else random."""

    is_human = False

    def __init__(self, name: str = "Greedy", rng: random.Random | None = None) -> None:
        self.name = name
        self._rng = rng or random.Random()

    def choose_move(self, board: Board) -> int:
        moves = board.legal_moves()

        for col in moves:
            if board.is_winning_move(col):
                return col

        opponent = other(board.current_player)
        threats = [col for col in moves if board.is_winning_move(col, opponent)]
        if threats:
            # With two or more threats the game is lost anyway; block one of them.
            return self._rng.choice(threats)

        safe = [col for col in moves if not self._gives_opponent_a_win(board, col)]
        return self._rng.choice(safe or moves)

    @staticmethod
    def _gives_opponent_a_win(board: Board, col: int) -> bool:
        board.play(col)
        try:
            return any(board.is_winning_move(reply) for reply in board.legal_moves())
        finally:
            board.undo()


class MinimaxAgent:
    """Searches ``depth`` plies with plain minimax and the heuristic in ``evaluate.py``."""

    is_human = False

    def __init__(
        self, name: str = "Minimax", depth: int = DEFAULT_DEPTH, weights: Weights = DEFAULT_WEIGHTS
    ) -> None:
        if depth < 1:
            raise ValueError("depth must be at least 1")
        self.name = name
        self.depth = depth
        self.weights = weights
        self.last_result: SearchResult | None = None  # nodes/score of the last search, for metrics

    def choose_move(self, board: Board) -> int:
        result = minimax(board, self.depth, board.current_player, self._evaluate)
        self.last_result = result
        return result.move

    def _evaluate(self, board: Board, player: int) -> int:
        return evaluate(board, player, self.weights)


def make_agent(
    kind: str,
    name: str | None = None,
    rng: random.Random | None = None,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    depth: int = DEFAULT_DEPTH,
) -> Agent:
    """Build an agent by kind: ``human``, ``random``, ``greedy`` or ``minimax``."""
    label = name or kind.capitalize()
    if kind == "human":
        return HumanAgent(label, input_fn, print_fn)
    if kind == "random":
        return RandomAgent(label, rng)
    if kind == "greedy":
        return GreedyAgent(label, rng)
    if kind == "minimax":
        return MinimaxAgent(label, depth)
    raise ValueError(f"unknown agent kind: {kind!r} (expected one of {', '.join(KINDS)})")
