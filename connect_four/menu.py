"""Interactive start menu: play/watch single games or run batches of bot matches."""

from __future__ import annotations

import random
import time
from typing import Callable

from .agents import BOT_KINDS, DEFAULT_DEPTH, KINDS, make_agent
from .arena import format_result, run_match
from .board import RED, YELLOW
from .game import play_game
from .render import player_name

DEFAULT_GAMES = 100

MENU = """
Connect Four
  1) Play or watch a single game
  2) Run a batch of bot matches
  q) Quit"""


class Menu:
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[[str], None] = print,
        color: bool = True,
        delay: float = 0.6,
        seed: int | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
        depth: int = DEFAULT_DEPTH,
    ) -> None:
        self._input = input_fn
        self._print = print_fn
        self._color = color
        self._delay = delay
        self._seed = seed
        self._rng = random.Random(seed)
        self._sleep = sleep_fn
        self._depth = depth

    def run(self) -> None:
        while True:
            self._print(MENU)
            choice = self._input("> ").strip().lower()
            if choice == "1":
                self.single_game()
            elif choice == "2":
                self.batch()
            elif choice in ("q", "quit", "exit"):
                return
            else:
                self._print("Please choose 1, 2 or q.")

    def single_game(self) -> None:
        red_kind = self._ask_kind(f"{player_name(RED, self._color)} player", KINDS)
        yellow_kind = self._ask_kind(f"{player_name(YELLOW, self._color)} player", KINDS)
        red = self._agent(red_kind, RED)
        yellow = self._agent(yellow_kind, YELLOW)
        play_game(red, yellow, self._color, self._print, self._delay, self._sleep)

    def batch(self) -> None:
        kind_a = self._ask_kind("Bot A", BOT_KINDS)
        kind_b = self._ask_kind("Bot B", BOT_KINDS)
        games = self._ask_int("Number of games", DEFAULT_GAMES)
        self._print("")
        self._print(format_result(run_match(kind_a, kind_b, games, self._seed, self._depth)))

    def _agent(self, kind: str, player: int):
        name = player_name(player, self._color) if kind == "human" else None
        return make_agent(kind, name, self._rng, self._input, self._print, self._depth)

    def _ask_kind(self, label: str, kinds: tuple[str, ...]) -> str:
        # Numbers follow KINDS everywhere, so "3" is always greedy, whichever list is shown.
        numbered = {str(KINDS.index(kind) + 1): kind for kind in kinds}
        options = ", ".join(f"{n} {kind}" for n, kind in numbered.items())
        while True:
            answer = self._input(f"{label} [{options}]: ").strip().lower()
            if answer in numbered:
                return numbered[answer]
            if answer in kinds:
                return answer
            self._print(f"Please choose one of: {options}.")

    def _ask_int(self, label: str, default: int) -> int:
        while True:
            answer = self._input(f"{label} [{default}]: ").strip()
            if not answer:
                return default
            if answer.isdigit() and int(answer) >= 1:
                return int(answer)
            self._print("Please type a whole number of at least 1.")
