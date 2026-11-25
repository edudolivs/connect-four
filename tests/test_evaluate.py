import unittest

from connect_four.board import RED, YELLOW, Board
from connect_four.evaluate import WINDOWS, Weights, evaluate


def board_from_moves(moves):
    """Play 0-based columns alternately, Red first."""
    board = Board()
    for col in moves:
        board.play(col)
    return board


class TestEvaluate(unittest.TestCase):
    def test_window_count(self):
        # 24 horizontal + 21 vertical + 12 per diagonal direction.
        self.assertEqual(len(WINDOWS), 69)

    def test_empty_board_is_neutral(self):
        self.assertEqual(evaluate(Board(), RED), 0)
        self.assertEqual(evaluate(Board(), YELLOW), 0)

    def test_center_piece_beats_edge_piece(self):
        self.assertGreater(evaluate(board_from_moves([3]), RED), evaluate(board_from_moves([0]), RED))

    def test_three_scores_more_than_two(self):
        # Red on row 0: columns 0-1 vs 0-1-2 (Yellow stacks column 6 meanwhile).
        two = board_from_moves([0, 6, 1, 6])
        three = board_from_moves([0, 6, 1, 6, 2])
        self.assertGreater(evaluate(three, RED), evaluate(two, RED))

    def test_good_for_red_is_bad_for_yellow(self):
        board = board_from_moves([0, 6, 1, 6, 2])  # Red has an open three on row 0
        self.assertGreater(evaluate(board, RED), 0)
        self.assertLess(evaluate(board, YELLOW), 0)

    def test_weights_are_parameters(self):
        board = board_from_moves([3])
        self.assertEqual(evaluate(board, RED, Weights(center=10)), 10)
        self.assertEqual(evaluate(board, RED, Weights(center=0)), 0)


if __name__ == "__main__":
    unittest.main()
