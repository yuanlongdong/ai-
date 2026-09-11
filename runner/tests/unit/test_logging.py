import tempfile
import unittest
from pathlib import Path

from runner.logging import LogRecord, append_record, is_processed, load_records


class TestLogging(unittest.TestCase):
    def test_append_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "runner.jsonl"
            append_record(p, LogRecord.now("R7-DOUBAO-abc123", 7, "Doubao", "ok"))
            records = load_records(p)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].event_id, "R7-DOUBAO-abc123")
            self.assertEqual(records[0].round, 7)
            self.assertEqual(records[0].result, "ok")

    def test_is_processed_only_counts_ok(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "runner.jsonl"
            append_record(p, LogRecord.now("E1", 1, "Doubao", "failed"))
            self.assertFalse(is_processed(p, "E1"))
            append_record(p, LogRecord.now("E1", 1, "Doubao", "ok"))
            self.assertTrue(is_processed(p, "E1"))

    def test_corrupt_line_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "runner.jsonl"
            p.write_text("{bad json}\n", encoding="utf-8")
            append_record(p, LogRecord.now("E2", 1, "Doubao", "ok"))
            self.assertEqual(len(load_records(p)), 1)

    def test_missing_log_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_records(Path(d) / "nope.jsonl"), [])
            self.assertFalse(is_processed(Path(d) / "nope.jsonl", "X"))


if __name__ == "__main__":
    unittest.main()
