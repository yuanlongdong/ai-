"""E2E 测试：Runner 在临时 Git 仓库中完成一轮完整闭环（Doubao 交付物）。

覆盖链路：状态读取 -> Provider 调用 -> 草稿校验 -> event_id -> 原子提交 -> 状态推进。
"""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from runner.github import GitHubBlackboard
from runner.main import run_turn
from runner.providers.doubao import MockDoubaoProvider
from runner.validate import expected_event_id

SEED_CONTEXT = "# Context\n\n共享上下文"
SEED_GPT = "# GPT\n\n（上一轮观点）"
SEED_DOUBAO = "# Doubao\n\n（上一轮观点）"


def seed_status_md(
    root: Path,
    next_writer="Doubao",
    round_no=7,
    last_event="R7-DOUBAO-aec4affd",
    status="WAITING_DOUBAO",
    completion="IN_PROGRESS",
    last_writer=None,
):
    meeting = root / "meeting"
    meeting.mkdir(parents=True, exist_ok=True)
    (meeting / "context.md").write_text(SEED_CONTEXT, encoding="utf-8")
    (meeting / "gpt.md").write_text(SEED_GPT, encoding="utf-8")
    (meeting / "doubao.md").write_text(SEED_DOUBAO, encoding="utf-8")
    last_writer = last_writer or ("GPT" if next_writer == "Doubao" else "Doubao")
    (meeting / "status.md").write_text(
        f"# Meeting Status\n\n"
        f"- Round: {round_no}\n"
        f"- Last writer: {last_writer}\n"
        f"- Next writer: {next_writer}\n"
        f"- Status: {status}\n"
        f"- Completion: {completion}\n"
        f"- Last event: {last_event}\n",
        encoding="utf-8",
    )


def make_repo(root: Path) -> GitHubBlackboard:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "E2E"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "e2e@test.local"], cwd=root, check=True)
    bb = GitHubBlackboard(root)
    bb.commit(
        ["meeting/context.md", "meeting/gpt.md", "meeting/doubao.md", "meeting/status.md"],
        "seed",
    )
    return bb


class TestRunnerFullRoundE2E(unittest.TestCase):
    def test_doubao_round_completes_and_advances_state(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(root, next_writer="Doubao", round_no=7)
            bb = make_repo(root)
            head = run_turn(bb, lambda: MockDoubaoProvider())
            self.assertTrue(head)

            status = (root / "meeting/status.md").read_text(encoding="utf-8")
            self.assertIn("- Round: 8", status)
            self.assertIn("- Last writer: Doubao", status)
            self.assertIn("- Next writer: GPT", status)
            self.assertIn("- Status: WAITING_GPT", status)

            opinion = (root / "meeting/doubao.md").read_text(encoding="utf-8")
            self.assertIn("round: 8", opinion)
            match = re.search(r"event_id: (R8-Doubao-[0-9a-f]{8})", opinion)
            self.assertIsNotNone(match)
            # event_id 与确定性草稿一致：Provider -> 校验 -> 提交 全链路一致
            original_status = {
                "round": 7,
                "last_writer": "GPT",
                "next_writer": "Doubao",
                "status": "WAITING_DOUBAO",
                "completion": "IN_PROGRESS",
                "last_event": "R7-DOUBAO-aec4affd",
            }
            expected = expected_event_id(
                MockDoubaoProvider().generate_opinion(SEED_CONTEXT, SEED_GPT, original_status)
            )
            self.assertEqual(match.group(1), expected)

            # 执行日志包含该事件（当前 main.py 为原始 JSON 行格式）
            log = (root / "meeting/logs/runner.jsonl").read_text(encoding="utf-8")
            self.assertIn(expected, log)
            # 已生成新提交
            self.assertEqual(bb.head(), head)


class TestRunnerDryRunE2E(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(root, next_writer="Doubao", round_no=7)
            bb = make_repo(root)
            head_before = bb.head()
            event_id = run_turn(bb, lambda: MockDoubaoProvider(), dry_run=True)
            self.assertTrue(event_id.startswith("R8-Doubao-"))
            # 无新提交、状态不变、无日志文件
            self.assertEqual(bb.head(), head_before)
            self.assertIn("- Round: 7", (root / "meeting/status.md").read_text(encoding="utf-8"))
            self.assertFalse((root / "meeting/logs/runner.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
