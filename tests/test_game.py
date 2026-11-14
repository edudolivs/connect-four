import unittest

from connect_four.agents import HumanAgent
from connect_four.board import RED, ROWS, YELLOW, Board
from connect_four.game import play_game


def scripted_input(answers):
    it = iter(answers)
    return lambda _prompt: next(it)


class TestHumanAgent(unittest.TestCase):
    def test_reprompts_until_valid_column(self):
        messages = []
        board = Board()
        for _ in range(ROWS):
            board.play(0)  # column 1 full (Red and Yellow alternate, no win)
        agent = HumanAgent("Red", scripted_input(["abc", "0", "8", "1", " 3 "]), messages.append)
        self.assertEqual(agent.choose_move(board), 2)
        self.assertEqual(len(messages), 4)
        self.assertIn("full", messages[-1])


class TestPlayGame(unittest.TestCase):
    def test_scripted_game_reports_winner(self):
        out = []
        red = HumanAgent("Red", scripted_input(["1", "1", "1", "1"]), out.append)
        yellow = HumanAgent("Yellow", scripted_input(["2", "2", "2"]), out.append)
        winner = play_game(red, yellow, color=False, print_fn=out.append)
        self.assertEqual(winner, RED)
        self.assertEqual(out[-1], "Red (X) wins!")

    def test_yellow_win(self):
        out = []
        red = HumanAgent("Red", scripted_input(["1", "1", "1", "7"]), out.append)
        yellow = HumanAgent("Yellow", scripted_input(["2", "2", "2", "2"]), out.append)
        self.assertEqual(play_game(red, yellow, color=False, print_fn=out.append), YELLOW)


if __name__ == "__main__":
    unittest.main()
