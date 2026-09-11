"""MVP 验收：双 AI 在临时 Git 仓库完成连续闭环（Doubao 交付物）。

验收标准（GPT Round 10 指定）：
- 两轮 round 连续推进；next_writer 正确交替
- event_id 可重放且不会重复执行
- 日志保持 append-only
- 失败后进入 NEED_USER_DECISION 且 round / next_writer 不推进（见 test_adversarial）
- dry-run 不产生提交（见 test_e2e）
- CI 集成测试通过
"""
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from runner.github import GitHubBlackboard
from runner.logging import load_records
from runner.main import run_turn
from runner.providers.doubao import MockDoubaoProvider, OpinionDraft
from test_e2e import make_repo, seed_status_md


class MockGPTProvider:
    """确定性 GPT Mock（无密钥，用于验收）。"""

    def __init__(self, writer: str = "GPT"):
        self.writer = writer

    def generate_opinion(self, context, counterpart_view, status):
        round_no = int(status["round"]) + 1
        return OpinionDraft(
            round=round_no,
            writer=self.writer,
            adds=True,
            status="proposed",
            date=time.strftime("%Y-%m-%d"),
            new_judgment=f"（mock）GPT 新增判断（Round {round_no}）",
            counterpart_response=f"（mock）回应 Doubao：{counterpart_view[:40]}",
            improvement_plan="（mock）GPT 改进方案。",
            open_questions="（mock）无待确认。",
            facts_evidence="（mock）无外部证据。",
        )


def remote_head(remote: Path) -> str:
    """裸远端 refs/heads/main 的提交（push 同步验证）。"""
    return subprocess.check_output(
        ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/main"], text=True
    ).strip()


def last_event(status_text: str) -> str:
    """从 status.md 文本中读取 Last event（event_id）。"""
    for line in status_text.splitlines():
        if line.startswith("- Last event: "):
            return line.split(": ", 1)[1].strip()
    raise AssertionError("status.md 缺少 Last event")


class TestTwoRoundContinuousLoop(unittest.TestCase):
    def test_gpt_doubao_gpt_three_turns_advance_and_sync(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(
                root,
                next_writer="GPT",
                round_no=7,
                last_writer="Doubao",
                last_event="R7-DOUBAO-aec4affd",
                status="WAITING_GPT",
            )
            bb = make_repo(root)
            remote = root / ".e2e-remote.git"

            # 第 1 轮：GPT 发言（run_turn 返回提交 SHA；event_id 见 status.md）
            c1 = run_turn(bb, lambda: MockGPTProvider())
            self.assertEqual(len(c1), 40)
            s = (root / "meeting/status.md").read_text(encoding="utf-8")
            e1 = last_event(s)
            self.assertTrue(e1.startswith("R8-GPT-"), e1)
            self.assertIn("- Round: 8", s)
            self.assertIn("- Next writer: Doubao", s)
            self.assertIn("- Status: WAITING_DOUBAO", s)

            # 第 2 轮：Doubao 发言
            c2 = run_turn(bb, lambda: MockDoubaoProvider())
            self.assertEqual(len(c2), 40)
            s = (root / "meeting/status.md").read_text(encoding="utf-8")
            e2 = last_event(s)
            self.assertTrue(e2.startswith("R9-Doubao-"), e2)
            self.assertIn("- Round: 9", s)
            self.assertIn("- Next writer: GPT", s)
            self.assertIn("- Status: WAITING_GPT", s)

            # 第 3 轮：GPT 再次发言（第二整轮）
            c3 = run_turn(bb, lambda: MockGPTProvider())
            self.assertEqual(len(c3), 40)
            s = (root / "meeting/status.md").read_text(encoding="utf-8")
            e3 = last_event(s)
            self.assertTrue(e3.startswith("R10-GPT-"), e3)
            self.assertIn("- Round: 10", s)
            self.assertIn("- Next writer: Doubao", s)
            self.assertIn("- Status: WAITING_DOUBAO", s)

            # 日志 append-only：3 条 ok，顺序对应轮次
            records = load_records(root / "meeting/logs/runner.jsonl")
            self.assertEqual(len(records), 3)
            self.assertTrue(all(r.result == "ok" for r in records))
            self.assertEqual([r.round for r in records], [8, 9, 10])
            self.assertEqual([r.event_id for r in records], [e1, e2, e3])

            # 共享仓库已推进：裸远端 HEAD == 本地 HEAD
            self.assertEqual(remote_head(remote), bb.head())


class TestEventReplayIdempotent(unittest.TestCase):
    def test_replay_returns_same_event_without_new_commit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_status_md(
                root,
                next_writer="GPT",
                round_no=7,
                last_writer="Doubao",
                last_event="R7-DOUBAO-aec4affd",
                status="WAITING_GPT",
            )
            bb = make_repo(root)
            status_before = (root / "meeting/status.md").read_text(encoding="utf-8")

            event1 = run_turn(bb, lambda: MockGPTProvider())
            head1 = bb.head()
            e1_id = last_event((root / "meeting/status.md").read_text(encoding="utf-8"))
            self.assertTrue(e1_id.startswith("R8-GPT-"), e1_id)

            # 模拟并发 Runner 的过期视图：恢复 turn 前状态后重放
            (root / "meeting/status.md").write_text(status_before, encoding="utf-8")
            replayed = run_turn(bb, lambda: MockGPTProvider())
            self.assertEqual(replayed, e1_id)   # 幂等：重放返回同 event_id
            self.assertEqual(bb.head(), head1)  # 无新提交


if __name__ == "__main__":
    unittest.main()
