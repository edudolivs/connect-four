import random
import unittest

from connect_four.agents import GreedyAgent, RandomAgent
from connect_four.arena import format_result, run_match
from connect_four.game import run_game


class TestRunGame(unittest.TestCase):
    def test_bots_finish_a_game(self):
        rng = random.Random(3)
        moves = []
        board = run_game(RandomAgent(rng=rng), GreedyAgent(rng=rng), on_move=lambda b, p, c: moves.append(c))
        self.assertTrue(board.is_terminal())
        self.assertEqual(len(moves), board.moves_played)


class TestRunMatch(unittest.TestCase):
    def test_totals_add_up_and_sides_alternate(self):
        result = run_match("random", "random", 21, seed=5)
        for i in (0, 1):
            self.assertEqual(sum(result.totals(i).values()), 21)
        self.assertEqual(sum(result.stats[0]["red"].values()), 11)  # A is Red in games 0, 2, ..., 20
        self.assertEqual(sum(result.stats[0]["yellow"].values()), 10)
        self.assertEqual(result.totals(0)["wins"], result.totals(1)["losses"])
        self.assertEqual(result.totals(0)["draws"], result.totals(1)["draws"])

    def test_same_seed_same_result(self):
        a = run_match("greedy", "random", 30, seed=11)
        b = run_match("greedy", "random", 30, seed=11)
        self.assertEqual(a.stats, b.stats)
        self.assertEqual(a.total_moves, b.total_moves)

    def test_seed_is_recorded_when_not_given(self):
        self.assertIsInstance(run_match("random", "random", 1).seed, int)

    def test_greedy_beats_random(self):
        result = run_match("greedy", "random", 200, seed=42)
        self.assertGreater(result.totals(0)["wins"], 180)

    def test_minimax_beats_random(self):
        result = run_match("minimax", "random", 10, seed=1, depth=3)
        self.assertGreaterEqual(result.totals(0)["wins"], 9)

    def test_rejects_humans_and_bad_counts(self):
        with self.assertRaises(ValueError):
            run_match("human", "random", 10)
        with self.assertRaises(ValueError):
            run_match("random", "random", 0)

    def test_format_result(self):
        text = format_result(run_match("greedy", "greedy", 4, seed=1))
        self.assertIn("greedy vs greedy: 4 games, sides alternate, seed 1", text)
        self.assertIn("greedy (A)", text)
        self.assertIn("greedy (B)", text)
        self.assertIn("avg length:", text)


if __name__ == "__main__":
    unittest.main()
