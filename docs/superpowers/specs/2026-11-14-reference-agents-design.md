# Step 2 design: random and greedy agents, batch matches, start menu

**Intent.** Roadmap step 2 of "Planejamento: Agente de Connect 4 com Busca Adversarial"
(https://claude.ai/artifact/XirPuwNYULC7nnfWGbtR49). Random and greedy players are the baselines the
search agent will be measured against (doc section 5: tournaments alternating who starts, win rate).

**Goals.** Two reference bots; single games with any pair of players (human × human, human × greedy,
greedy × greedy, …) that can be played or watched; batch bot-vs-bot matches that print win/draw counts;
an opening menu, with flags to skip it.

**Non-goals.** Search agents, heuristics, timing metrics, charts (later steps).

**Anti-goals.** A greedy bot so weak it loses to trivial traps (useless as a baseline); runs that can't
be reproduced.

## Approaches

- A. Choose players per game only; no batches.
- **B. A + batch matches with a results table (chosen by the user)**, plus an opening menu the user
  asked for. Flags still skip the menu for scripted runs.

## Design

- `GreedyAgent`: win → block (random among threats if several) → avoid columns that let the opponent
  win right on top → random among the rest (any legal move if none is safe). Uses `play`/`undo`;
  leaves the board unchanged. `RandomAgent`: uniform over legal moves. Both take a `random.Random`.
- `Board.is_winning_move(col, player=None)`: optional player so bots can test the opponent's threats.
- `game.run_game` (no I/O) and `game.play_game` (rendering, "X played column N", delay between moves
  when no human is playing).
- `arena.run_match(kind_a, kind_b, games, seed)`: A is Red in even games, B in odd ones; per-player
  wins/draws/losses split by colour; average game length; picks and records a seed when none is given.
- `menu.Menu`: 1) play/watch a single game, 2) batch, q) quit. Agent numbers are the same in every
  prompt (1 human, 2 random, 3 greedy); a batch lists only bots.
- CLI: `--red/--yellow {human,random,greedy}`, `--games N`, `--seed`, `--delay`; no flags → menu.

**Calls made by Claude (open to correction):** the greedy "avoid gifts" rule; default delay 0.6 s;
default batch size 100; one shared RNG per match; consistent menu numbering across prompts.

**Left to the builder.** Table layout details.
