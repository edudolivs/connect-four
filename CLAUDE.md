# Connect Four — adversarial search agent

Personal project: build a Connect Four agent using adversarial search, starting from a playable
terminal game and layering search techniques on top. The full plan lives in the doc
"Planejamento: Agente de Connect 4 com Busca Adversarial":
https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49 (read it through the Claude Docs connector).

## Commands

```bash
python3 -m connect_four                                   # menu: play/watch a game or run a batch
python3 -m connect_four --red human --yellow greedy       # single game, skips the menu
python3 -m connect_four --red greedy --yellow random --games 1000 --seed 42   # batch of bot games
NO_COLOR=1 python3 -m connect_four                        # without ANSI colors
python3 -m unittest -v                                    # run the test suite
```

Agent kinds: `human`, `random`, `greedy` (`--delay` sets the pause between bot moves when watching).
Batches alternate who plays Red, print wins/draws/losses per side, and always report the seed so a
run can be reproduced.

## Roadmap (doc section 6)

1. Board, rules, human vs. human — done (colored CLI game)
2. **Random and greedy agents** ← current step, plus start menu and batch matches (start of the Arena)
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
  `escolher_jogada(estado)`) plus `name` and `is_human`. Reference agents: `HumanAgent`,
  `RandomAgent`, `GreedyAgent` (win → block → avoid giving the opponent a win on top → random).
  Bots take a `random.Random` for reproducibility; build them with `make_agent(kind, ...)`.
  New agents: add a class and register its kind in `KINDS`/`BOT_KINDS` and `make_agent`.
- `Game` (`connect_four/game.py`): `run_game` (no I/O, used by batches/search experiments) and
  `play_game` (on-screen wrapper).
- `Arena` (`connect_four/arena.py`): `run_match(kind_a, kind_b, games, seed)` → `MatchResult`;
  `format_result` prints the table. Extend here for tournaments and metrics (doc section 5).
- Menu/CLI (`connect_four/menu.py`, `connect_four/__main__.py`): menu with no args, argparse flags otherwise.
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
