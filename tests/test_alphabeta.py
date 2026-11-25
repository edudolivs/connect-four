import random
import unittest

from connect_four.agents import AlphaBetaAgent, MinimaxAgent, make_agent
from connect_four.arena import format_result, run_match
from connect_four.board import RED, YELLOW, Board
from connect_four.search import WIN_SCORE, alphabeta, minimax


def board_from_moves(moves):
    """Play 0-based columns alternately, Red first. Cells are (row, col), row 0 = bottom."""
    board = Board()
    for col in moves:
        board.play(col)
    return board


def random_positions(count, seed=0, max_moves=20):
    """Reproducible non-terminal positions reached by random play."""
    rng = random.Random(seed)
    positions = []
    while len(positions) < count:
        board = Board()
        for _ in range(rng.randrange(max_moves)):
            board.play(rng.choice(board.legal_moves()))
            if board.is_terminal():
                break
        if not board.is_terminal():
            positions.append(board)
    return positions


class TestAlphaBetaMatchesMinimax(unittest.TestCase):
    def test_same_move_and_score_on_random_positions(self):
        for i, board in enumerate(random_positions(40, seed=1)):
            for depth in (1, 2, 3, 4):
                for player in (board.current_player,):
                    with self.subTest(position=i, depth=depth):
                        full = minimax(board, depth, player)
                        pruned = alphabeta(board, depth, player)
                        self.assertEqual((pruned.move, pruned.score), (full.move, full.score))
                        self.assertLessEqual(pruned.nodes, full.nodes)

    def test_same_score_from_the_other_side(self):
        # Searching for the player NOT to move (minimizing at the root) must agree too.
        for board in random_positions(10, seed=2):
            other = YELLOW if board.current_player == RED else RED
            self.assertEqual(alphabeta(board, 3, other).score, minimax(board, 3, other).score)

    def test_unordered_gives_same_score(self):
        for board in random_positions(10, seed=3):
            player = board.current_player
            self.assertEqual(
                alphabeta(board, 4, player, ordered=False).score, minimax(board, 4, player).score
            )

    def test_tactics(self):
        win = board_from_moves([0, 1, 0, 1, 0, 1])  # Red to move wins in column 0
        self.assertEqual(alphabeta(win, 3, RED).move, 0)
        self.assertEqual(alphabeta(win, 3, RED).score, WIN_SCORE + 2)
        block = board_from_moves([0, 1, 0, 2, 0])  # Yellow to move must block column 0
        self.assertEqual(alphabeta(block, 2, YELLOW).move, 0)
        double = board_from_moves([1, 6, 2, 6])  # column 3 makes a double threat
        self.assertEqual(alphabeta(double, 3, RED).move, 3)

    def test_leaves_board_unchanged(self):
        board = board_from_moves([3, 3, 2, 4, 2])
        alphabeta(board, 4, board.current_player)
        self.assertEqual(board, board_from_moves([3, 3, 2, 4, 2]))
        self.assertEqual(board.moves_played, 5)

    def test_edge_cases(self):
        finished = board_from_moves([0, 1, 0, 1, 0, 1, 0])
        result = alphabeta(finished, 3, YELLOW)
        self.assertIsNone(result.move)
        self.assertLessEqual(result.score, -WIN_SCORE)
        leaf = alphabeta(board_from_moves([3]), 0, RED, evaluate_fn=lambda b, p: 42)
        self.assertEqual((leaf.move, leaf.score, leaf.nodes), (None, 42, 1))
        with self.assertRaises(ValueError):
            alphabeta(Board(), -1, RED)


class TestPruningGain(unittest.TestCase):
    def test_far_fewer_nodes_than_minimax(self):
        board = Board()
        full = minimax(board, 5, RED).nodes
        pruned = alphabeta(board, 5, RED).nodes
        self.assertLess(pruned * 5, full)  # at least 5x fewer nodes at depth 5

    def test_center_first_ordering_helps(self):
        board = Board()
        ordered = alphabeta(board, 6, RED).nodes
        unordered = alphabeta(board, 6, RED, ordered=False).nodes
        self.assertLess(ordered, unordered)


class TestAlphaBetaAgent(unittest.TestCase):
    def test_plays_like_minimax_with_fewer_nodes(self):
        for board in random_positions(8, seed=4):
            mm, ab = MinimaxAgent(depth=3), AlphaBetaAgent(depth=3)
            self.assertEqual(ab.choose_move(board), mm.choose_move(board))
            self.assertLessEqual(ab.last_result.nodes, mm.last_result.nodes)

    def test_make_agent(self):
        agent = make_agent("alphabeta", depth=5)
        self.assertIsInstance(agent, AlphaBetaAgent)
        self.assertEqual((agent.name, agent.depth), ("AlphaBeta", 5))
        with self.assertRaises(ValueError):
            AlphaBetaAgent(depth=0)


class TestMatchMetrics(unittest.TestCase):
    def test_moves_time_and_nodes_are_recorded(self):
        result = run_match("alphabeta", "greedy", 4, seed=1, depth=2)
        ab, greedy = result.metrics
        self.assertEqual(ab.moves + greedy.moves, result.total_moves)
        self.assertTrue(ab.searched)
        self.assertGreater(ab.avg_nodes, 1)
        self.assertFalse(greedy.searched)
        self.assertEqual(greedy.nodes, 0)
        self.assertGreater(ab.seconds, 0)
        self.assertGreaterEqual(ab.max_seconds, ab.avg_seconds)

    def test_fake_clock_gives_exact_times(self):
        ticks = iter(range(10_000))
        result = run_match("random", "random", 2, seed=1, clock=lambda: next(ticks))
        for m in result.metrics:
            self.assertEqual(m.avg_seconds, 1.0)  # each choose_move spans exactly one tick
            self.assertEqual(m.max_seconds, 1.0)

    def test_alphabeta_and_minimax_tie_with_same_moves(self):
        # Same depth, same evaluation, deterministic play: mirrored games, identical choices.
        result = run_match("alphabeta", "minimax", 2, seed=1, depth=3)
        self.assertEqual(result.totals(0)["wins"], result.totals(1)["wins"])
        ab, mm = result.metrics
        self.assertLess(ab.avg_nodes, mm.avg_nodes)

    def test_format_shows_metrics(self):
        text = format_result(run_match("alphabeta", "random", 2, seed=1, depth=2))
        self.assertIn("per move", text)
        self.assertIn("avg nodes", text)
        lines = text.splitlines()
        random_row = [line for line in lines if line.startswith("random") and "ms" in line][0]
        self.assertTrue(random_row.rstrip().endswith("-"))  # random does not search


if __name__ == "__main__":
    unittest.main()
