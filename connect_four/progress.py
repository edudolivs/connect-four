"""Terminal progress bar for batch matches."""

from __future__ import annotations

import sys
import time
from typing import Callable, TextIO

from .agents import DEFAULT_DEPTH
from .arena import MatchResult, run_match

FILL = "█"
EMPTY = "░"
CLEAR_LINE = "\x1b[K"


def format_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{secs:02}" if hours else f"{minutes}:{secs:02}"


class ProgressBar:
    """Redraws one terminal line: ``[█████░░░░░] 42/100  42%  0:07 elapsed  ~0:10 left``.

    Draws nothing unless enabled; by default it is enabled only when ``stream`` is a terminal,
    so piped output and tests stay clean.
    """

    def __init__(
        self,
        total: int,
        stream: TextIO | None = None,
        width: int = 24,
        enabled: bool | None = None,
        clock: Callable[[], float] = time.monotonic,
        min_interval: float = 0.1,
    ) -> None:
        self.total = total
        self.stream = stream or sys.stderr
        self.width = width
        self.enabled = enabled if enabled is not None else _isatty(self.stream)
        self._clock = clock
        self._min_interval = min_interval
        self._start = clock()
        self._last_draw: float | None = None
        self._last_line = ""

    def render(self, done: int, elapsed: float, suffix: str = "") -> str:
        fraction = done / self.total if self.total else 1.0
        filled = int(fraction * self.width)
        bar = FILL * filled + EMPTY * (self.width - filled)
        parts = [f"[{bar}] {done}/{self.total}", f"{fraction:4.0%}", f"{format_duration(elapsed)} elapsed"]
        if 0 < done < self.total:
            parts.append(f"~{format_duration(elapsed / done * (self.total - done))} left")
        if suffix:
            parts.append(suffix)
        return "  ".join(parts)

    def update(self, done: int, suffix: str = "") -> None:
        if not self.enabled:
            return
        now = self._clock()
        throttled = self._last_draw is not None and now - self._last_draw < self._min_interval
        if throttled and done < self.total:
            return
        self._last_draw = now
        self._last_line = self.render(done, now - self._start, suffix)
        self.stream.write(f"\r{self._last_line}{CLEAR_LINE}")
        self.stream.flush()

    def close(self) -> None:
        """End the bar's line, leaving the final state (with total time) on screen."""
        if self.enabled and self._last_draw is not None:
            self.stream.write("\n")
            self.stream.flush()


def _isatty(stream: TextIO) -> bool:
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


def run_match_with_progress(
    kind_a: str,
    kind_b: str,
    games: int,
    seed: int | None = None,
    depth: int = DEFAULT_DEPTH,
    stream: TextIO | None = None,
) -> MatchResult:
    """``run_match`` with a live progress bar and running score (A wins · B wins · draws)."""
    bar = ProgressBar(games, stream=stream)

    def on_game(done: int, result: MatchResult) -> None:
        a, b = result.totals(0), result.totals(1)
        bar.update(done, f"A {a['wins']} · B {b['wins']} · draws {a['draws']}")

    try:
        return run_match(kind_a, kind_b, games, seed, depth, on_game=on_game)
    finally:
        bar.close()
