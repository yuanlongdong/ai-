import tempfile
import unittest
from pathlib import Path

from runner.logging import LogRecord, append_record
from runner.trigger import poll_once, should_run


def make_status(**kw):
    base = {
        "round": 6,
        "last_writer": "GPT",
        "next_writer": "Doubao",
        "status": "WAITING_DOUBAO",
        "completion": "IN_PROGRESS",
        "last_event": "R6-GPT-4f0c9a21",
    }
    base.update(kw)
    return base


class TestShouldRun(unittest.TestCase):
    def test_run_when_my_turn_and_unprocessed(self):
        with tempfile.TemporaryDirectory() as d:
            run, reason = should_run(make_status(), Path(d) / "r.jsonl")
            self.assertTrue(run)

    def test_skip_when_not_my_turn(self):
        with tempfile.TemporaryDirectory() as d:
            run, reason = should_run(make_status(next_writer="GPT"), Path(d) / "r.jsonl")
            self.assertFalse(run)
            self.assertIn("GPT", reason)

    def test_skip_when_done(self):
        with tempfile.TemporaryDirectory() as d:
            run, _ = should_run(make_status(status="DONE"), Path(d) / "r.jsonl")
            self.assertFalse(run)

    def test_skip_when_need_user_decision(self):
        with tempfile.TemporaryDirectory() as d:
            run, reason = should_run(make_status(status="NEED_USER_DECISION"), Path(d) / "r.jsonl")
            self.assertFalse(run)
            self.assertIn("用户", reason)

    def test_idempotent_skip_when_last_event_processed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.jsonl"
            append_record(p, LogRecord.now("R6-GPT-4f0c9a21", 6, "GPT", "ok"))
            run, reason = should_run(make_status(), p)
            self.assertFalse(run)
            self.assertIn("幂等", reason)


class TestPollOnce(unittest.TestCase):
    def test_runs_turn(self):
        with tempfile.TemporaryDirectory() as d:
            out = poll_once(lambda: make_status(), lambda s: "turn executed", Path(d) / "r.jsonl")
            self.assertTrue(out.startswith("RUN"))

    def test_skips_when_done(self):
        with tempfile.TemporaryDirectory() as d:
            out = poll_once(lambda: make_status(status="DONE"), lambda s: "x", Path(d) / "r.jsonl")
            self.assertTrue(out.startswith("SKIP"))


if __name__ == "__main__":
    unittest.main()
