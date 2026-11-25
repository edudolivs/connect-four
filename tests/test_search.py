import unittest

from connect_four.board import COLS, RED, YELLOW, Board
from connect_four.search import WIN_SCORE, minimax


def board_from_moves(moves):
    """Play 0-based columns alternately, Red first. Cells are (row, col), row 0 = bottom."""
    board = Board()
    for col in moves:
        board.play(col)
    return board


class TestMinimax(unittest.TestCase):
    def test_finds_win_in_one(self):
        # Red: (0,0) (1,0) (2,0). Red to move.
        board = board_from_moves([0, 1, 0, 1, 0, 1])
        result = minimax(board, 1, RED)
        self.assertEqual(result.move, 0)
        self.assertGreaterEqual(result.score, WIN_SCORE)

    def test_faster_win_scores_higher(self):
        # Same position searched deeper: the win comes with 2 plies to spare.
        board = board_from_moves([0, 1, 0, 1, 0, 1])
        result = minimax(board, 3, RED)
        self.assertEqual(result.move, 0)
        self.assertEqual(result.score, WIN_SCORE + 2)

    def test_blocks_immediate_threat(self):
        # Red: (0,0) (1,0) (2,0). Yellow to move must block column 0.
        board = board_from_moves([0, 1, 0, 2, 0])
        self.assertEqual(minimax(board, 2, YELLOW).move, 0)

    def test_sets_up_double_threat(self):
        # Red: (0,1) (0,2). Playing column 3 threatens both (0,0) and (0,4): a forced win in 3 plies.
        board = board_from_moves([1, 6, 2, 6])
        result = minimax(board, 3, RED)
        self.assertEqual(result.move, 3)
        self.assertGreaterEqual(result.score, WIN_SCORE)

    def test_leaves_board_unchanged(self):
        moves = [3, 3, 2, 4, 2]
        board = board_from_moves(moves)
        minimax(board, 3, board.current_player)
        self.assertEqual(board, board_from_moves(moves))
        self.assertEqual(board.moves_played, len(moves))

    def test_node_count_includes_root(self):
        self.assertEqual(minimax(Board(), 1, RED).nodes, 1 + COLS)
        self.assertEqual(minimax(Board(), 2, RED).nodes, 1 + COLS + COLS**2)

    def test_finished_game_has_no_move(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1, 0])  # Red already won
        result = minimax(board, 3, YELLOW)
        self.assertIsNone(result.move)
        self.assertLessEqual(result.score, -WIN_SCORE)

    def test_depth_zero_is_the_heuristic(self):
        result = minimax(board_from_moves([3]), 0, RED, evaluate_fn=lambda b, p: 42)
        self.assertEqual((result.move, result.score, result.nodes), (None, 42, 1))

    def test_negative_depth_raises(self):
        with self.assertRaises(ValueError):
            minimax(Board(), -1, RED)


if __name__ == "__main__":
    unittest.main()
