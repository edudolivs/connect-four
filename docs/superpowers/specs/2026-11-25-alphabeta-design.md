# Step 4 design: alpha-beta pruning, move ordering and search metrics

**Intent.** Roadmap step 4 of "Planejamento: Agente de Connect 4 com Busca Adversarial"
(https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49): get minimax's exact decisions while visiting
far fewer nodes, so deeper searches fit in a reasonable time per move.

**Goals.** `alphabeta` with the same move and score as `minimax` at the same depth; center-first move
ordering with a switch to turn it off (to measure its value); an `alphabeta` agent kind; per-move
time and node metrics in batches (doc section 5).

**Non-goals.** Transposition table, iterative deepening, time limits (step 6); heuristic changes (step 5).

**Anti-goals.** An alpha-beta that differs from minimax in any decision — that would be a bug, not an
optimisation.

## Approaches

- **Separate `alphabeta` function next to `minimax` (chosen).** Minimax stays as the correctness
  reference and the baseline for the node-count comparison.
- Replace minimax with alpha-beta. Loses the reference and the comparison.
- Negamax formulation. Shorter, but reads differently from the existing minimax; not worth it now.

## Design

- `search.alphabeta(board, depth, player, evaluate_fn, ordered=True)`: same terminal scores as minimax
  (`±(WIN_SCORE + plies left)`, 0 for draws, heuristic at depth 0); full window at the root; strict
  comparison so ties keep the first move in order, exactly like minimax. `ordered=False` tries columns
  left to right.
- `AlphaBetaAgent(MinimaxAgent)`: only the `search` function differs.
- `arena`: agents are wrapped to time `choose_move` and read `last_result.nodes`; `MatchResult.metrics`
  holds per-player `MoveMetrics`; `format_result` adds avg/max time and avg nodes per move.

## Measured (10 mid-game positions, 8–14 moves in, averages)

| depth | minimax nodes / time | alpha-beta unordered | alpha-beta center-first | reduction |
|------:|---------------------:|---------------------:|------------------------:|----------:|
| 4 | 2,471 / 37 ms | 647 / 9 ms | 306 / 3 ms | 8× |
| 5 | 16,200 / 251 ms | 2,919 / 40 ms | 1,205 / 15 ms | 13× |
| 6 | 106,470 / 1.6 s | 9,440 / 123 ms | 3,182 / 37 ms | 33× |
| 7 | — | 42,615 / 574 ms | 11,059 / 131 ms | |
| 8 | — | 127,459 / 1.6 s | 29,634 / 353 ms | |

Center-first ordering alone cuts alpha-beta's nodes by ~3–4×.

## Found along the way

Two deterministic search agents replay the same two games in every batch (one per colour), so their
win rates say little. Tournaments between search agents need variety: random openings or random
tie-breaking between equal moves (to decide in step 6/7).

**Calls made by Claude (open to correction):** metrics added in this step rather than later;
`ordered` flag kept for the report; agent kind named `alphabeta`.
