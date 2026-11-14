"""Run with ``python3 -m connect_four`` for human vs. human."""

import sys

from .agents import HumanAgent
from .board import RED, YELLOW
from .game import play_game
from .render import player_name, use_color


def main() -> int:
    color = use_color()
    red = HumanAgent(player_name(RED, color))
    yellow = HumanAgent(player_name(YELLOW, color))
    try:
        play_game(red, yellow, color=color)
    except (KeyboardInterrupt, EOFError):
        print("\nGame aborted.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
