import unittest

from connect_four.board import Board
from connect_four.render import render


class TestRender(unittest.TestCase):
    def test_plain_render(self):
        board = Board()
        for col in (3, 3, 2):
            board.play(col)
        expected = "\n".join(
            [
                "| . | . | . | . | . | . | . |",
                "| . | . | . | . | . | . | . |",
                "| . | . | . | . | . | . | . |",
                "| . | . | . | . | . | . | . |",
                "| . | . | . | O | . | . | . |",
                "| . | . | X | X | . | . | . |",
                "  1   2   3   4   5   6   7",
            ]
        )
        self.assertEqual(render(board, color=False), expected)

    def test_color_render_uses_ansi_codes(self):
        board = Board()
        board.play(0)
        board.play(1)
        text = render(board, color=True)
        self.assertIn("\x1b[", text)
        self.assertNotIn("X", text)
        self.assertNotIn("O", text)


if __name__ == "__main__":
    unittest.main()
