# Connect Four — adversarial search agent

Personal project: build a Connect Four agent using adversarial search, starting from a playable
terminal game and layering search techniques on top. The full plan lives in the doc
"Planejamento: Agente de Connect 4 com Busca Adversarial":
https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49 (read it through the Claude Docs connector).

## Commands

```bash
python3 -m connect_four          # play human vs. human in the terminal
NO_COLOR=1 python3 -m connect_four   # same, without ANSI colors
python3 -m unittest -v           # run the test suite
```

## Roadmap (doc section 6)

1. **Board, rules, human vs. human** ← current step (colored CLI game)
2. Random and greedy agents (greedy: win if possible, block if needed)
3. Minimax with fixed depth
4. Alpha-beta pruning and move ordering (center columns first)
5. Refined heuristic
6. Iterative deepening (time limit) and transposition table (Zobrist hash or bitboard key)
7. Experiments, charts, and report (optional: MCTS for comparison)

## Architecture (doc section 4)

Keep responsibilities separate so algorithms can be swapped:

- `Board` / State (`connect_four/board.py`): representation, legal moves, play/undo, win check.
  Pure logic, **no I/O**. Plain 6×7 grid for now; may move to bitboards (two 64-bit ints) for speed.
- `Evaluator` (future): heuristic for non-terminal states — 4-cell windows with 2–3 own pieces,
  center-column bonus, opponent threat penalty, odd/even row threats. **Keep weights as parameters.**
- `Search` (future): minimax/alpha-beta, transposition table, time control.
- `Agent` (`connect_four/agents.py`): single interface `choose_move(board) -> int` (the doc's
  `escolher_jogada(estado)`). Reference agents: human (terminal), random, greedy.
- `Game` / `Arena` (`connect_four/game.py`): game loop now; agent-vs-agent tournaments later.
- Rendering (`connect_four/render.py`): ANSI-colored board text, kept out of `Board`.

## Rules of the game model

- Columns are 0–6 internally; humans see and type 1–7.
- Utility for search: +win / −loss / 0 draw (use large values like ±1000 to combine with the heuristic).
- `Board.legal_moves()` returns columns center-first so search gets move ordering for free.

## Conventions

- Python 3.10+, standard library only unless a dependency is clearly worth it.
- Code and identifiers in English (the planning doc is in Portuguese).
- Tests with stdlib `unittest` under `tests/`. Cover win detection in all four directions,
  full columns, and draws; add tests for every new agent/search feature.
- Validate search correctness against known positions — Connect Four is solved (first player wins
  by playing the center); Pascal Pons' public solver is a good reference.
- Metrics to track once search exists: win rate, nodes expanded, time per move, gains from
  pruning and the transposition table.
- Design docs go in `docs/superpowers/specs/`.
