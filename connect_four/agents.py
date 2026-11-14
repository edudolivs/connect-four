"""Players. Every agent picks a 0-based column via ``choose_move(board)``."""

from __future__ import annotations

from typing import Callable, Protocol

from .board import COLS, Board


class Agent(Protocol):
    name: str

    def choose_move(self, board: Board) -> int: ...


class HumanAgent:
    """Asks a person in the terminal for a column (1-7)."""

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
