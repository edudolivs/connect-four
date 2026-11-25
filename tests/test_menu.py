import contextlib
import io
import unittest

from connect_four.__main__ import main
from connect_four.menu import Menu


def run_menu(answers, seed=0):
    out = []
    it = iter(answers)
    Menu(input_fn=lambda _prompt: next(it), print_fn=out.append, color=False, delay=0, seed=seed).run()
    return "\n".join(out)


class TestMenu(unittest.TestCase):
    def test_quit(self):
        self.assertIn("Connect Four", run_menu(["q"]))

    def test_watch_greedy_vs_greedy(self):
        out = run_menu(["1", "3", "greedy", "q"])
        self.assertTrue("wins!" in out or "draw" in out)
        self.assertIn("[Greedy] played column", out)

    def test_human_vs_greedy(self):
        # Human Red stacks column 1; greedy Yellow must block the fourth piece.
        answers = ["1", "1", "3"] + ["1"] * 3 + ["7"] * 18 + ["q"]
        out = run_menu(answers)
        self.assertIn("Yellow (O) [Greedy] played column 1", out)

    def test_batch(self):
        out = run_menu(["2", "greedy", "2", "20", "q"])
        self.assertIn("greedy vs random: 20 games", out)

    def test_batch_uses_same_numbers_as_single_game(self):
        out = run_menu(["2", "3", "3", "5", "q"])
        self.assertIn("greedy vs greedy: 5 games", out)

    def test_batch_default_game_count(self):
        out = run_menu(["2", "2", "2", "", "q"])
        self.assertIn("random vs random: 100 games", out)

    def test_invalid_input_asks_again(self):
        # Bad menu choice; then a batch where "human", "9" and "1" (human) are refused as bots,
        # and "0" / "abc" are refused as game counts.
        out = run_menu(["x", "2", "human", "9", "1", "2", "3", "0", "abc", "1", "q"])
        self.assertIn("Please choose 1, 2 or q.", out)
        self.assertEqual(out.count("Please choose one of: 2 random, 3 greedy, 4 minimax, 5 alphabeta."), 3)
        self.assertEqual(out.count("Please type a whole number of at least 1."), 2)
        self.assertIn("random vs greedy: 1 game,", out)


class TestCommandLine(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_batch_from_flags(self):
        code, out, _ = self.run_main(["--red", "greedy", "--yellow", "random", "--games", "10", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("greedy vs random: 10 games, sides alternate, seed 3", out)

    def test_batch_rejects_human(self):
        code, _, err = self.run_main(["--red", "human", "--yellow", "random", "--games", "10"])
        self.assertEqual(code, 2)
        self.assertIn("--games needs --red and --yellow set to bots", err)

    def test_batch_needs_both_players(self):
        code, _, _ = self.run_main(["--games", "10"])
        self.assertEqual(code, 2)

    def test_minimax_batch_from_flags(self):
        code, out, _ = self.run_main(
            ["--red", "minimax", "--yellow", "random", "--games", "2", "--seed", "1", "--depth", "2"]
        )
        self.assertEqual(code, 0)
        self.assertIn("minimax vs random: 2 games", out)

    def test_rejects_depth_below_one(self):
        code, _, err = self.run_main(["--red", "minimax", "--yellow", "random", "--depth", "0"])
        self.assertEqual(code, 2)
        self.assertIn("--depth must be at least 1", err)

    def test_single_bot_game_from_flags(self):
        code, out, _ = self.run_main(["--red", "greedy", "--yellow", "random", "--delay", "0", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertTrue("wins!" in out or "draw" in out)


if __name__ == "__main__":
    unittest.main()
