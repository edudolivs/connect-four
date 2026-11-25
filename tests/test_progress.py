import io
import unittest

from connect_four.arena import run_match
from connect_four.progress import ProgressBar, format_duration, run_match_with_progress


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class TestFormatDuration(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(format_duration(7), "0:07")
        self.assertEqual(format_duration(125.4), "2:05")
        self.assertEqual(format_duration(3725), "1:02:05")


class TestProgressBar(unittest.TestCase):
    def test_render_midway(self):
        bar = ProgressBar(100, width=10, enabled=True)
        line = bar.render(40, elapsed=8.0, suffix="A 30 · B 8 · draws 2")
        self.assertTrue(line.startswith("[████░░░░░░] 40/100"))
        self.assertIn(" 40%", line)
        self.assertIn("0:08 elapsed", line)
        self.assertIn("~0:12 left", line)  # 8 s for 40 games -> 12 s for the other 60
        self.assertTrue(line.endswith("A 30 · B 8 · draws 2"))

    def test_render_start_and_end_have_no_estimate(self):
        bar = ProgressBar(10, width=10, enabled=True)
        self.assertNotIn("left", bar.render(0, 0.0))
        done = bar.render(10, 3.0)
        self.assertTrue(done.startswith("[██████████] 10/10"))
        self.assertIn("100%", done)
        self.assertNotIn("left", done)

    def test_disabled_writes_nothing(self):
        out = io.StringIO()
        bar = ProgressBar(5, stream=out, enabled=False)
        for done in range(1, 6):
            bar.update(done)
        bar.close()
        self.assertEqual(out.getvalue(), "")

    def test_disabled_by_default_when_not_a_terminal(self):
        self.assertFalse(ProgressBar(5, stream=io.StringIO()).enabled)

    def test_redraws_in_place_throttles_and_ends_line(self):
        out, clock = io.StringIO(), FakeClock()
        bar = ProgressBar(3, stream=out, enabled=True, clock=clock, min_interval=1.0)
        bar.update(1)  # drawn (first update)
        clock.now = 0.5
        bar.update(2)  # skipped: too soon
        clock.now = 0.6
        bar.update(3)  # drawn: the last update always is
        bar.close()
        text = out.getvalue()
        self.assertEqual(text.count("\r"), 2)
        self.assertNotIn(" 2/3", text)
        self.assertIn(" 3/3", text)
        self.assertTrue(text.endswith("\n"))


class TestRunMatchProgress(unittest.TestCase):
    def test_on_game_called_after_every_game(self):
        calls = []
        result = run_match("random", "random", 5, seed=2, on_game=lambda done, r: calls.append(done))
        self.assertEqual(calls, [1, 2, 3, 4, 5])
        self.assertEqual(sum(result.totals(0).values()), 5)

    def test_run_match_with_progress_matches_plain_run(self):
        out = io.StringIO()
        with_bar = run_match_with_progress("greedy", "random", 20, seed=4, stream=out)
        plain = run_match("greedy", "random", 20, seed=4)
        self.assertEqual(with_bar.stats, plain.stats)
        self.assertEqual(out.getvalue(), "")  # StringIO is not a terminal


if __name__ == "__main__":
    unittest.main()
