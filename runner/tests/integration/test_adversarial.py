"""对抗测试：失败路径、非法草稿、错误轮次（Doubao 交付物）。

验证 interfaces.md §3.1 失败路径：重试仍失败 -> NEED_USER_DECISION，
round / next_writer 不推进，且不写入半成品观点文件。
"""
import tempfile
import time
import unittest
from pathlib import Path

from runner.github import GitHubBlackboard
from runner.main import run_turn
from runner.providers.doubao import OpinionDraft
from test_e2e import make_repo, seed_status_md


class FailingProvider:
    def generate_opinion(self, context, counterpart_view, status):
        raise RuntimeError("provider down")


class WrongWriterProvider:
    def generate_opinion(self, context, counterpart_view, status):
        return OpinionDraft(
            round=int(status["round"]) + 1,
            writer="GPT",  # 预期 Doubao，故意写错
            adds=True,
            status="proposed",
            date=time.strftime("%Y-%m-%d"),
            new_judgment="x",
            counterpart_response="x",
            improvement_plan="x",
            open_questions="x",
            facts_evidence="x",
        )


class WrongRoundProvider:
    def generate_opinion(self, context, counterpart_view, status):
        return OpinionDraft(
            round=int(status["round"]),  # 应为 +1，故意写错
            writer="Doubao",
            adds=True,
            status="proposed",
            date=time.strftime("%Y-%m-%d"),
            new_judgment="x",
            counterpart_response="x",
            improvement_plan="x",
            open_questions="x",
            facts_evidence="x",
        )


def assert_failed_status(test, root, round_no=7, next_writer="Doubao"):
    status = (root / "meeting/status.md").read_text(encoding="utf-8")
    test.assertIn("- Status: NEED_USER_DECISION", status)
    test.assertIn(f"- Round: {round_no}", status)  # 不推进
    test.assertIn(f"- Next writer: {next_writer}", status)  # 不推进
    log = (root / "meeting/logs/runner.jsonl").read_text(encoding="utf-8")
    test.assertIn('"event": "failed"', log)


class TestFailurePath(unittest.TestCase):
    def test_provider_failure_enters_need_user_decision_without_advancing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(root, next_writer="Doubao", round_no=7)
            bb = make_repo(root)
            run_turn(bb, lambda: FailingProvider(), retries=1)
            assert_failed_status(self, root)

    def test_wrong_writer_draft_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(root, next_writer="Doubao", round_no=7)
            bb = make_repo(root)
            run_turn(bb, lambda: WrongWriterProvider(), retries=1)
            assert_failed_status(self, root)
            # 未写入半成品观点文件
            self.assertIn("（上一轮观点）", (root / "meeting/doubao.md").read_text(encoding="utf-8"))

    def test_wrong_round_draft_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(root, next_writer="Doubao", round_no=7)
            bb = make_repo(root)
            run_turn(bb, lambda: WrongRoundProvider(), retries=1)
            assert_failed_status(self, root)


if __name__ == "__main__":
    unittest.main()
