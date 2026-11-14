"""Game loop: alternate agents until a win or a draw."""

from __future__ import annotations

from typing import Callable

from .agents import Agent
from .board import RED, YELLOW, Board
from .render import player_name, render

CLEAR = "\x1b[2J\x1b[H"


def play_game(
    red: Agent,
    yellow: Agent,
    color: bool = True,
    print_fn: Callable[[str], None] = print,
) -> int | None:
    """Play one game and return the winner (RED/YELLOW) or None for a draw."""
    board = Board()
    agents = {RED: red, YELLOW: yellow}

    def show() -> None:
        prefix = CLEAR if color else ""
        print_fn(f"{prefix}\n{render(board, color)}\n")

    while not board.is_terminal():
        show()
        player = board.current_player
        col = agents[player].choose_move(board)
        board.play(col)

    show()
    winner = board.winner()
    if winner is None:
        print_fn("It's a draw!")
    else:
        print_fn(f"{player_name(winner, color)} wins!")
    return winner
