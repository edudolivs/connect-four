# Step 3 design: fixed-depth minimax

**Intent.** Roadmap step 3 of "Planejamento: Agente de Connect 4 com Busca Adversarial"
(https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49): the first search agent. Kept simple on purpose — it is the
baseline that alpha-beta (step 4) and the refined heuristic (step 5) will be measured against.

**Goals.** A heuristic with tunable weights; plain minimax to a fixed depth that counts nodes; a `minimax` agent kind
usable in single games, batches, the menu and the CLI (`--depth`).

**Non-goals.** Pruning, odd/even threat analysis, time limits, transposition tables (steps 4–6).

**Anti-goals.** Search code that mutates the board it was given; results that change between runs.

## Design

- `evaluate.py` — `Weights(three=5, two=2, opp_three=4, center=3)` and `evaluate(board, player, weights)`: sums over
  the 69 four-cell windows (+three for an own 3-and-empty window, +two for an own 2-and-2-empty window, −opp_three
  for an opponent 3-and-empty window) plus a bonus per own piece in the center column.
- `search.py` — `minimax(board, depth, player, evaluate_fn) -> SearchResult(move, score, nodes)`. Uses
  `play`/`undo`. Terminal utility ±(`WIN_SCORE` + plies left), `WIN_SCORE = 1000`, draw 0, so faster wins and slower
  losses are preferred. Ties keep the first move of `legal_moves()` (center-first), which makes it deterministic.
  `nodes` counts every position visited, root included.
- `agents.MinimaxAgent(name, depth=4, weights)` keeps `last_result` for metrics; registered as kind `minimax`.
- `run_match`, `Menu` and the CLI pass `depth` through to `make_agent`. The menu does not ask for a depth.

**Calls made by Claude (open to correction):** default depth 4 (about 30 ms per move); the heuristic weights; plain
minimax rather than negamax (closer to the textbook version, easier to compare against alpha-beta); the menu does not
ask for a depth.

## Baseline (seed 42, depth 4)

- minimax vs greedy: 20–0 over 20 games, sides alternating.
- minimax vs random: 20–0 over 20 games.
- Nodes and time per move against greedy, from one game: depth 2 ≈ 55 nodes / 1 ms; depth 3 ≈ 359 / 5 ms; depth 4 ≈ 1,974 / 28 ms;
  depth 5 ≈ 12,224 / 171 ms.
