"""Connect Four board: state, legal moves, play/undo and win detection. No I/O."""

from __future__ import annotations

ROWS = 6
COLS = 7
CONNECT = 4

EMPTY = 0
RED = 1
YELLOW = 2

# Center-first order: better move ordering for alpha-beta later.
CENTER_ORDER = sorted(range(COLS), key=lambda c: (abs(c - COLS // 2), c))

# (row step, col step) for horizontal, vertical and both diagonals.
_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def other(player: int) -> int:
    return YELLOW if player == RED else RED


class Board:
    """A 6x7 grid. Row 0 is the bottom; columns are 0-based."""

    def __init__(self) -> None:
        self._grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self._heights = [0] * COLS
        self._history: list[int] = []
        self._winner: int | None = None
        self.current_player = RED

    # --- queries -----------------------------------------------------------

    def cell(self, row: int, col: int) -> int:
        return self._grid[row][col]

    @property
    def moves_played(self) -> int:
        return len(self._history)

    @property
    def last_move(self) -> int | None:
        return self._history[-1] if self._history else None

    def is_legal(self, col: int) -> bool:
        return 0 <= col < COLS and self._heights[col] < ROWS and self._winner is None

    def legal_moves(self) -> list[int]:
        return [c for c in CENTER_ORDER if self.is_legal(c)]

    def winner(self) -> int | None:
        return self._winner

    def is_full(self) -> bool:
        return len(self._history) == ROWS * COLS

    def is_terminal(self) -> bool:
        return self._winner is not None or self.is_full()

    def is_winning_move(self, col: int) -> bool:
        """Would the current player win by playing ``col``? Leaves the board unchanged."""
        if not self.is_legal(col):
            return False
        return self._connects(self._heights[col], col, self.current_player)

    # --- mutations ---------------------------------------------------------

    def play(self, col: int) -> None:
        if not self.is_legal(col):
            raise ValueError(f"illegal move: column {col}")
        row = self._heights[col]
        player = self.current_player
        self._grid[row][col] = player
        self._heights[col] += 1
        self._history.append(col)
        if self._connects(row, col, player):
            self._winner = player
        self.current_player = other(player)

    def undo(self) -> None:
        if not self._history:
            raise IndexError("no move to undo")
        col = self._history.pop()
        self._heights[col] -= 1
        self._grid[self._heights[col]][col] = EMPTY
        # A won game ends immediately, so the position before the last move had no winner.
        self._winner = None
        self.current_player = other(self.current_player)

    # --- helpers -----------------------------------------------------------

    def _connects(self, row: int, col: int, player: int) -> bool:
        """Does a ``player`` piece at (row, col) complete a line of four?"""
        for dr, dc in _DIRECTIONS:
            count = 1
            for sign in (1, -1):
                r, c = row + sign * dr, col + sign * dc
                while 0 <= r < ROWS and 0 <= c < COLS and self._grid[r][c] == player:
                    count += 1
                    r, c = r + sign * dr, c + sign * dc
            if count >= CONNECT:
                return True
        return False

    def __eq__(self, other_board: object) -> bool:
        if not isinstance(other_board, Board):
            return NotImplemented
        return self._grid == other_board._grid and self.current_player == other_board.current_player

    def __repr__(self) -> str:
        return f"Board(moves={self._history!r})"
