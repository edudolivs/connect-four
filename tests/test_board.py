import unittest

from connect_four.board import COLS, EMPTY, RED, ROWS, YELLOW, Board


def board_from_moves(moves):
    """Build a board by playing 0-based columns alternately, Red first."""
    board = Board()
    for col in moves:
        board.play(col)
    return board


class TestMoves(unittest.TestCase):
    def test_new_board_is_empty_and_red_starts(self):
        board = Board()
        self.assertEqual(board.current_player, RED)
        self.assertTrue(all(board.cell(r, c) == EMPTY for r in range(ROWS) for c in range(COLS)))
        self.assertIsNone(board.winner())
        self.assertFalse(board.is_terminal())

    def test_piece_drops_to_lowest_free_row(self):
        board = board_from_moves([3, 3])
        self.assertEqual(board.cell(0, 3), RED)
        self.assertEqual(board.cell(1, 3), YELLOW)
        self.assertEqual(board.current_player, RED)

    def test_legal_moves_are_center_first(self):
        self.assertEqual(Board().legal_moves(), [3, 2, 4, 1, 5, 0, 6])

    def test_full_column_is_not_legal_and_raises(self):
        board = board_from_moves([0] * ROWS)
        self.assertNotIn(0, board.legal_moves())
        self.assertFalse(board.is_legal(0))
        with self.assertRaises(ValueError):
            board.play(0)

    def test_out_of_range_column_raises(self):
        board = Board()
        for col in (-1, COLS):
            with self.assertRaises(ValueError):
                board.play(col)

    def test_undo_restores_previous_state(self):
        board = board_from_moves([3, 4, 3])
        board.undo()
        self.assertEqual(board.cell(1, 3), EMPTY)
        self.assertEqual(board.current_player, RED)
        self.assertEqual(board, board_from_moves([3, 4]))

    def test_undo_on_empty_board_raises(self):
        with self.assertRaises(IndexError):
            Board().undo()

    def test_undo_clears_a_win(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(board.winner(), RED)
        board.undo()
        self.assertIsNone(board.winner())

    def test_cannot_play_after_game_over(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1, 0])
        with self.assertRaises(ValueError):
            board.play(2)


class TestWins(unittest.TestCase):
    def test_horizontal_win(self):
        board = board_from_moves([0, 0, 1, 1, 2, 2, 3])
        self.assertEqual(board.winner(), RED)
        self.assertTrue(board.is_terminal())

    def test_vertical_win(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(board.winner(), RED)

    def test_diagonal_up_right_win(self):
        # Red builds (0,0) (1,1) (2,2) (3,3).
        board = board_from_moves([0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])
        self.assertEqual(board.winner(), RED)

    def test_diagonal_down_right_win(self):
        # Mirror of the previous position: Red builds (0,6) (1,5) (2,4) (3,3).
        board = board_from_moves([6, 5, 5, 4, 4, 3, 4, 3, 3, 0, 3])
        self.assertEqual(board.winner(), RED)

    def test_yellow_can_win(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1, 6, 1])
        self.assertEqual(board.winner(), YELLOW)

    def test_win_detected_when_last_piece_is_in_the_middle(self):
        board = board_from_moves([0, 0, 1, 1, 3, 3, 2])
        self.assertEqual(board.winner(), RED)

    def test_three_in_a_row_is_not_a_win(self):
        board = board_from_moves([0, 0, 1, 1, 2, 2])
        self.assertIsNone(board.winner())

    def test_line_does_not_wrap_across_rows(self):
        # Red at columns 4,5,6 on row 0 and column 0 on row 1 must not count.
        board = board_from_moves([4, 0, 5, 1, 6, 2, 0])
        self.assertIsNone(board.winner())

    def test_is_winning_move(self):
        board = board_from_moves([0, 1, 0, 1, 0, 1])
        self.assertTrue(board.is_winning_move(0))
        self.assertFalse(board.is_winning_move(2))
        self.assertEqual(board, board_from_moves([0, 1, 0, 1, 0, 1]))


class TestDraw(unittest.TestCase):
    def test_full_board_without_winner_is_a_draw(self):
        # Fill columns in pairs (0,1), (2,3), (4,5), then 6.
        # Column pattern per pair: three moves in A, three in B, repeated, so no line of four forms.
        moves = []
        for a, b in ((0, 1), (2, 3), (4, 5)):
            moves += [a, b, a, b, a, b, b, a, b, a, b, a]
        moves += [6] * ROWS
        board = board_from_moves(moves)
        self.assertTrue(board.is_full())
        self.assertIsNone(board.winner())
        self.assertTrue(board.is_terminal())
        self.assertEqual(board.legal_moves(), [])


if __name__ == "__main__":
    unittest.main()
