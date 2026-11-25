# Connect Four — adversarial search agent

Personal project: build a Connect Four agent using adversarial search, starting from a playable
terminal game and layering search techniques on top. The full plan lives in the doc
"Planejamento: Agente de Connect 4 com Busca Adversarial":
https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49 (read it through the Claude Docs connector).

## Commands

```bash
python3 -m connect_four                                   # menu: play/watch a game or run a batch
python3 -m connect_four --red human --yellow greedy       # single game, skips the menu
python3 -m connect_four --red human --yellow alphabeta --depth 7 # play against the search agent
python3 -m connect_four --red greedy --yellow random --games 1000 --seed 42   # batch of bot games
python3 -m connect_four --red alphabeta --yellow minimax --games 10 --depth 5  # compare search cost
NO_COLOR=1 python3 -m connect_four                        # without ANSI colors
python3 -m unittest -v                                    # run the test suite
```

Agent kinds: `human`, `random`, `greedy`, `minimax`, `alphabeta` (`--depth` sets the search depth in
plies for both search agents, default 4; `--delay` sets the pause between bot moves when watching).
Batches alternate who plays Red, print wins/draws/losses per side plus avg/max time and avg search
nodes per move, and always report the seed so a run can be reproduced.
Search agents are deterministic: a batch between two of them repeats the same two games. While they run, a progress bar with ETA and running score is drawn on stderr
(only when it is a terminal; `connect_four/progress.py`, fed by `run_match(..., on_game=...)`).

## Roadmap (doc section 6)

1. Board, rules, human vs. human — done (colored CLI game)
2. Random and greedy agents — done, plus start menu and batch matches (start of the Arena)
3. Minimax with fixed depth — done
4. **Alpha-beta pruning and move ordering (center columns first)** ← current step
   (8× fewer nodes than minimax at depth 4, 33× at depth 6, on mid-game positions)
5. Refined heuristic
6. Iterative deepening (time limit) and transposition table (Zobrist hash or bitboard key)
7. Experiments, charts, and report (optional: MCTS for comparison)

## Architecture (doc section 4)

Keep responsibilities separate so algorithms can be swapped:

- `Board` / State (`connect_four/board.py`): representation, legal moves, play/undo, win check.
  Pure logic, **no I/O**. Plain 6×7 grid for now; may move to bitboards (two 64-bit ints) for speed.
- `Evaluator` (`connect_four/evaluate.py`): heuristic for non-terminal states — 4-cell windows with 2–3 own
  pieces, center-column bonus, opponent threat penalty; odd/even row threats come in step 5.
  **Keep weights as parameters** (`Weights`).
- `Search` (`connect_four/search.py`): `minimax(board, depth, player, evaluate_fn)` and
  `alphabeta(..., ordered=True)` → `SearchResult(move, score, nodes)`. Alpha-beta must return the
  same move and score as minimax (tested on random positions); `ordered=False` tries columns left to
  right, to measure the ordering gain. Transposition table and time control go here next.
- `Agent` (`connect_four/agents.py`): single interface `choose_move(board) -> int` (the doc's
  `escolher_jogada(estado)`) plus `name` and `is_human`. Reference agents: `HumanAgent`,
  `RandomAgent`, `GreedyAgent` (win → block → avoid giving the opponent a win on top → random),
  `MinimaxAgent(depth, weights)` (keeps `last_result` for metrics) and `AlphaBetaAgent` (subclass
  that only swaps the `search` function).
  Bots take a `random.Random` for reproducibility; build them with `make_agent(kind, ...)`.
  New agents: add a class and register its kind in `KINDS`/`BOT_KINDS` and `make_agent`.
- `Game` (`connect_four/game.py`): `run_game` (no I/O, used by batches/search experiments) and
  `play_game` (on-screen wrapper).
- `Arena` (`connect_four/arena.py`): `run_match(kind_a, kind_b, games, seed, depth)` → `MatchResult`
  with outcomes and per-player `MoveMetrics` (moves, avg/max seconds, avg nodes; agents are wrapped
  to time `choose_move` and read `last_result.nodes`). `format_result` prints the table.
  Extend here for tournaments (doc section 5).
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
