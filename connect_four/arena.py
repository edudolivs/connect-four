"""Batch matches between bots, alternating who plays first."""

from __future__ import annotations

import random
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

from .agents import BOT_KINDS, DEFAULT_DEPTH, Agent, make_agent
from .board import RED, YELLOW, Board
from .game import run_game

OUTCOMES = ("wins", "draws", "losses")
ROLES = ("red", "yellow")


@dataclass
class MoveMetrics:
    """Per-player cost of choosing moves over a match (doc section 5 metrics)."""

    moves: int = 0
    seconds: float = 0.0
    max_seconds: float = 0.0
    nodes: int = 0
    searched: bool = False  # True when the agent reports search nodes (minimax, alphabeta)

    def record(self, seconds: float, nodes: int | None) -> None:
        self.moves += 1
        self.seconds += seconds
        self.max_seconds = max(self.max_seconds, seconds)
        if nodes is not None:
            self.nodes += nodes
            self.searched = True

    @property
    def avg_seconds(self) -> float:
        return self.seconds / self.moves if self.moves else 0.0

    @property
    def avg_nodes(self) -> float:
        return self.nodes / self.moves if self.moves else 0.0


class _Measured:
    """Wraps an agent to time each ``choose_move`` and read its search node count."""

    def __init__(self, agent: Agent, metrics: MoveMetrics, clock: Callable[[], float]) -> None:
        self._agent = agent
        self._metrics = metrics
        self._clock = clock
        self.name = agent.name
        self.is_human = agent.is_human

    def choose_move(self, board: Board) -> int:
        start = self._clock()
        col = self._agent.choose_move(board)
        elapsed = self._clock() - start
        last = getattr(self._agent, "last_result", None)
        self._metrics.record(elapsed, last.nodes if last is not None else None)
        return col


@dataclass
class MatchResult:
    kind_a: str
    kind_b: str
    games: int
    seed: int
    total_moves: int = 0
    # stats[i][role] counts outcomes for player i (0 = A, 1 = B) when playing that role.
    stats: list[dict[str, Counter]] = field(
        default_factory=lambda: [{role: Counter() for role in ROLES} for _ in range(2)]
    )
    # metrics[i]: time and search nodes per move for player i.
    metrics: list[MoveMetrics] = field(default_factory=lambda: [MoveMetrics(), MoveMetrics()])

    def totals(self, i: int) -> Counter:
        return self.stats[i]["red"] + self.stats[i]["yellow"]

    @property
    def avg_length(self) -> float:
        return self.total_moves / self.games if self.games else 0.0


def run_match(
    kind_a: str,
    kind_b: str,
    games: int,
    seed: int | None = None,
    depth: int = DEFAULT_DEPTH,
    on_game: Callable[[int, MatchResult], None] | None = None,
    clock: Callable[[], float] = time.perf_counter,
) -> MatchResult:
    """Play ``games`` games between two bot kinds. A plays Red in even games, B in odd ones.

    Without a seed one is picked and recorded, so every run can be reproduced.
    ``depth`` is the search depth for minimax/alphabeta players. ``on_game(done, result)`` runs
    after each game with the number of games finished and the partial result (e.g. for a progress
    bar). Each player's time per move (and search nodes, for search agents) goes in ``metrics``.
    """
    for kind in (kind_a, kind_b):
        if kind not in BOT_KINDS:
            raise ValueError(f"batch matches need bots ({', '.join(BOT_KINDS)}), got {kind!r}")
    if games < 1:
        raise ValueError("games must be at least 1")
    if seed is None:
        seed = random.randrange(1_000_000)

    rng = random.Random(seed)
    result = MatchResult(kind_a, kind_b, games, seed)
    agent_a = _Measured(make_agent(kind_a, rng=rng, depth=depth), result.metrics[0], clock)
    agent_b = _Measured(make_agent(kind_b, rng=rng, depth=depth), result.metrics[1], clock)

    for game in range(games):
        a_is_red = game % 2 == 0
        red, yellow = (agent_a, agent_b) if a_is_red else (agent_b, agent_a)
        board = run_game(red, yellow)
        result.total_moves += board.moves_played
        winner = board.winner()
        for i in (0, 1):
            plays_red = (i == 0) == a_is_red
            color = RED if plays_red else YELLOW
            if winner is None:
                outcome = "draws"
            else:
                outcome = "wins" if winner == color else "losses"
            result.stats[i]["red" if plays_red else "yellow"][outcome] += 1
        if on_game:
            on_game(game + 1, result)
    return result


def format_result(result: MatchResult) -> str:
    names = [result.kind_a, result.kind_b]
    if names[0] == names[1]:
        names = [f"{names[0]} (A)", f"{names[1]} (B)"]
    width = max(12, *(len(n) + 2 for n in names))

    def row(label: str, counts: Counter, pct: bool) -> str:
        cells = "".join(f"{counts[o]:>8}" for o in OUTCOMES)
        total = sum(counts[o] for o in OUTCOMES)
        rate = f"{100 * counts['wins'] / total:>7.1f}%" if pct and total else ""
        return f"{label:<{width}}{cells}{rate}".rstrip()

    lines = [
        f"{result.kind_a} vs {result.kind_b}: {result.games} game{'s' if result.games != 1 else ''}, "
        f"sides alternate, seed {result.seed}",
        f"{'':<{width}}{'wins':>8}{'draws':>8}{'losses':>8}{'win%':>8}",
    ]
    for i, name in enumerate(names):
        lines.append(row(name, result.totals(i), pct=True))
        lines.append(row("  as Red", result.stats[i]["red"], pct=False))
        lines.append(row("  as Yellow", result.stats[i]["yellow"], pct=False))
    lines.append(f"avg length: {result.avg_length:.1f} moves")
    lines.append("")
    lines.append(f"{'per move':<{width}}{'avg time':>11}{'max time':>11}{'avg nodes':>12}")
    for name, m in zip(names, result.metrics):
        nodes = f"{m.avg_nodes:,.0f}" if m.searched else "-"
        lines.append(
            f"{name:<{width}}{format_ms(m.avg_seconds):>11}{format_ms(m.max_seconds):>11}{nodes:>12}"
        )
    return "\n".join(lines)


def format_ms(seconds: float) -> str:
    ms = seconds * 1000
    return f"{ms:.2f} ms" if ms < 10 else f"{ms:,.0f} ms"
