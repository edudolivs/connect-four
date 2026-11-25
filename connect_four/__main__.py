"""Entry point: ``python3 -m connect_four`` opens the menu; flags skip it.

Examples:
    python3 -m connect_four                                  # menu
    python3 -m connect_four --red human --yellow greedy      # single game
    python3 -m connect_four --red greedy --yellow random --games 1000 --seed 42   # batch
    python3 -m connect_four --red human --yellow minimax --depth 4  # play against minimax
"""

from __future__ import annotations

import argparse
import random
import sys

from .agents import BOT_KINDS, DEFAULT_DEPTH, KINDS, make_agent
from .arena import format_result
from .board import RED, YELLOW
from .game import play_game
from .menu import Menu
from .progress import run_match_with_progress
from .render import player_name, use_color


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m connect_four",
        description="Connect Four in the terminal. Without --red/--yellow/--games, opens a menu.",
    )
    parser.add_argument("--red", choices=KINDS, help="Red player (moves first)")
    parser.add_argument("--yellow", choices=KINDS, help="Yellow player")
    parser.add_argument("--games", type=int, help="run a batch of N bot games (sides alternate)")
    parser.add_argument("--seed", type=int, help="random seed, for reproducible runs")
    parser.add_argument(
        "--depth", type=int, default=DEFAULT_DEPTH,
        help=f"search depth in plies for minimax players (default {DEFAULT_DEPTH})",
    )
    parser.add_argument("--delay", type=float, default=0.6, help="seconds between moves when watching bots (default 0.6)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    color = use_color()

    if args.depth < 1:
        parser.error("--depth must be at least 1")
    if args.games is not None:
        if args.games < 1:
            parser.error("--games must be at least 1")
        if args.red not in BOT_KINDS or args.yellow not in BOT_KINDS:
            parser.error(f"--games needs --red and --yellow set to bots ({', '.join(BOT_KINDS)})")

    try:
        if args.games is not None:
            print(format_result(run_match_with_progress(args.red, args.yellow, args.games, args.seed, args.depth)))
        elif args.red or args.yellow:
            rng = random.Random(args.seed)

            def agent(kind: str | None, player: int):
                kind = kind or "human"
                name = player_name(player, color) if kind == "human" else None
                return make_agent(kind, name, rng, depth=args.depth)

            play_game(agent(args.red, RED), agent(args.yellow, YELLOW), color=color, delay=args.delay)
        else:
            Menu(color=color, delay=args.delay, seed=args.seed, depth=args.depth).run()
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
