"""Game loop: alternate agents until a win or a draw."""

from __future__ import annotations

import time
from typing import Callable

from .agents import Agent
from .board import RED, YELLOW, Board
from .render import player_name, render

CLEAR = "\x1b[2J\x1b[H"

MoveHook = Callable[[Board, int, int], None]


def run_game(red: Agent, yellow: Agent, on_move: MoveHook | None = None) -> Board:
    """Play one game without any I/O. ``on_move(board, player, col)`` runs after each move."""
    board = Board()
    agents = {RED: red, YELLOW: yellow}
    while not board.is_terminal():
        player = board.current_player
        col = agents[player].choose_move(board)
        board.play(col)
        if on_move:
            on_move(board, player, col)
    return board


def play_game(
    red: Agent,
    yellow: Agent,
    color: bool = True,
    print_fn: Callable[[str], None] = print,
    delay: float = 0.0,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int | None:
    """Play one game on screen and return the winner (RED/YELLOW) or None for a draw.

    When no human is playing, waits ``delay`` seconds after each move so the game can be watched.
    """
    agents = {RED: red, YELLOW: yellow}
    watching = not any(getattr(a, "is_human", False) for a in agents.values())

    def label(player: int) -> str:
        name = player_name(player, color)
        agent = agents[player]
        return name if getattr(agent, "is_human", False) else f"{name} [{agent.name}]"

    def show(board: Board, note: str = "") -> None:
        prefix = CLEAR if color else ""
        print_fn(f"{prefix}\n{render(board, color)}\n{note}")

    def after_move(board: Board, player: int, col: int) -> None:
        show(board, f"{label(player)} played column {col + 1}.\n")
        if watching and delay > 0 and not board.is_terminal():
            sleep_fn(delay)

    show(Board())
    board = run_game(red, yellow, on_move=after_move)

    winner = board.winner()
    if winner is None:
        print_fn("It's a draw!")
    else:
        print_fn(f"{label(winner)} wins!")
    return winner
