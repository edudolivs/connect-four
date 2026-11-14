# Step 1 design: colored CLI Connect Four

**Intent.** First step of the roadmap in "Planejamento: Agente de Connect 4 com Busca Adversarial"
(https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49): board, rules, and human vs. human, as a simple
colored terminal game. It is the foundation the search agents will reuse, so the board API matters
more than the UI.

**Goals.** Correct rules (drops, full columns, 4-in-a-row in all directions, draws); a board API a
search can use (legal moves, play, undo, win check); a pluggable `Agent.choose_move(board)` interface
with a human agent; colored, readable terminal output.

**Non-goals.** AI agents, GUI, networking, bitboards (later step).

**Anti-goals.** I/O inside `Board`; a UI so elaborate it slows down the real work (search).

**Constraints.** Personal project, no outside requirements. Python, standard library only.

## Approaches

- **A. Plain ANSI-colored text, type a column number (chosen by the user).** Zero dependencies,
  easy to test, input mirrors how agents choose a column.
- B. Same game rendered with `rich`. Prettier, but a dependency for looks only.
- C. Full-screen `curses` with arrow-key cursor. Most game-like, ~3× the UI code, hard to test,
  awkward on Windows, and mostly thrown away once agents play.

## Design

- `connect_four/board.py` — `Board`: 6×7 grid, column heights, current player, move history.
  `legal_moves()` (center-first), `play(col)`, `undo()`, `winner()`, `is_full()`, `is_terminal()`.
  Win check only looks at lines through the last move. `ValueError` on illegal moves.
- `connect_four/agents.py` — `Agent` protocol and `HumanAgent` (prompts 1–7, re-prompts on bad input).
- `connect_four/render.py` — `render(board, color)`; colors off when `NO_COLOR` is set or stdout is
  not a TTY.
- `connect_four/game.py` — `play_game(red, yellow)` loop; clean exit on Ctrl+C/EOF.
- Tests in `tests/` with `unittest`.

**Calls made by Claude (open to correction):** English identifiers (`choose_move` for
`escolher_jogada`); `unittest` over pytest to stay dependency-free; Python 3.10+; Red moves first;
`undo()` takes no argument (uses move history).

**Left to the builder.** Exact glyphs and spacing of the board.
