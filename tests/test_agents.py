import random
import unittest
from unittest import mock

from connect_four.agents import GreedyAgent, HumanAgent, RandomAgent, make_agent
from connect_four.board import RED, Board


def board_from_moves(moves):
    """Play 0-based columns alternately, Red first. Cells below are (row, col), row 0 = bottom."""
    board = Board()
    for col in moves:
        board.play(col)
    return board


def greedy(seed=0):
    return GreedyAgent(rng=random.Random(seed))


class TestRandomAgent(unittest.TestCase):
    def test_only_legal_moves(self):
        board = board_from_moves([0] * 6 + [6] * 6)  # columns 0 and 6 full
        agent = RandomAgent(rng=random.Random(1))
        for _ in range(200):
            self.assertIn(agent.choose_move(board), range(1, 6))

    def test_same_seed_same_moves(self):
        board = Board()
        a = RandomAgent(rng=random.Random(7))
        b = RandomAgent(rng=random.Random(7))
        self.assertEqual([a.choose_move(board) for _ in range(30)], [b.choose_move(board) for _ in range(30)])


class TestGreedyAgent(unittest.TestCase):
    def test_takes_vertical_win(self):
        # Red: (0,0) (1,0) (2,0). Red to move.
        board = board_from_moves([0, 1, 0, 1, 0, 2])
        self.assertEqual(greedy().choose_move(board), 0)

    def test_prefers_own_win_over_block(self):
        # Red has three in column 0, Yellow three in column 1. Red to move wins rather than blocks.
        board = board_from_moves([0, 1, 0, 1, 0, 1])
        self.assertEqual(greedy().choose_move(board), 0)

    def test_blocks_vertical_threat(self):
        # Red: (0,0) (1,0) (2,0). Yellow to move must block column 0.
        board = board_from_moves([0, 1, 0, 2, 0])
        self.assertEqual(greedy().choose_move(board), 0)

    def test_blocks_horizontal_threat(self):
        # Red: (0,1) (0,2) (0,3) threatens (0,0) and (0,4). Yellow to move blocks one of them.
        board = board_from_moves([1, 1, 2, 2, 3])
        for seed in range(10):
            self.assertIn(greedy(seed).choose_move(board), (0, 4))

    def test_blocks_diagonal_threat(self):
        # Red: (0,0) (1,1) (2,2); column 3 holds R, Y, R so (3,3) is next. Yellow to move.
        board = board_from_moves([0, 1, 1, 2, 3, 2, 2, 3, 3])
        self.assertFalse(board.is_winning_move(3))  # Yellow has no win of its own there
        self.assertTrue(board.is_winning_move(3, player=RED))
        for seed in range(10):
            self.assertEqual(greedy(seed).choose_move(board), 3)

    def test_avoids_gifting_a_win(self):
        # Row 0: _ R R Y R _ _   Row 1: _ Y Y Y R _ _   Red to move.
        # Dropping in column 0 lets Yellow land on (1,0) and complete row 1.
        board = board_from_moves([1, 1, 2, 2, 4, 3, 4, 3])
        board.play(0)
        self.assertTrue(board.is_winning_move(0))  # sanity: column 0 really is a gift
        board.undo()
        for seed in range(50):
            self.assertNotEqual(greedy(seed).choose_move(board), 0)

    def test_falls_back_to_any_legal_move_when_none_is_safe(self):
        board = board_from_moves([3, 3])
        with mock.patch.object(GreedyAgent, "_gives_opponent_a_win", return_value=True):
            self.assertIn(greedy().choose_move(board), board.legal_moves())

    def test_leaves_board_unchanged(self):
        board = board_from_moves([3, 3, 2, 4, 2])
        greedy().choose_move(board)
        self.assertEqual(board, board_from_moves([3, 3, 2, 4, 2]))
        self.assertEqual(board.moves_played, 5)


class TestMakeAgent(unittest.TestCase):
    def test_kinds(self):
        self.assertIsInstance(make_agent("human", "Red"), HumanAgent)
        self.assertIsInstance(make_agent("random"), RandomAgent)
        self.assertIsInstance(make_agent("greedy"), GreedyAgent)
        self.assertEqual(make_agent("greedy").name, "Greedy")

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            make_agent("minimax")


if __name__ == "__main__":
    unittest.main()
