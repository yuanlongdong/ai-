"""Doubao Provider（Doubao 模块）。

契约见 runner/interfaces.md：
    generate_opinion(context, counterpart_view, status) -> OpinionDraft

Provider 只调用模型并返回标准化草稿，不读写任何会议状态文件；
event_id 由 Runner 计算并回填（interfaces.md §3 step 5）。
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OpinionDraft:
    """与 interfaces.md §2 对齐的标准化意见草稿。"""

    round: int
    writer: str
    adds: bool
    status: str
    date: str
    facts_evidence: str = ""
    new_judgment: str = ""
    counterpart_response: str = ""
    improvement_plan: str = ""
    open_questions: str = ""
    event_id: str = ""  # 由 Runner 计算并回填

    def body(self) -> str:
        sections = (
            ("新增判断", self.new_judgment),
            ("对对方的回应", self.counterpart_response),
            ("改进方案", self.improvement_plan),
            ("待确认问题", self.open_questions),
            ("事实/证据", self.facts_evidence),
        )
        return "\n\n".join(f"## {title}\n\n{content}" for title, content in sections)

    def front_matter(self) -> str:
        lines = [
            "---",
            f"round: {self.round}",
            f"writer: {self.writer}",
            f"adds: {'true' if self.adds else 'false'}",
            f"status: {self.status}",
            f"event_id: {self.event_id or '<pending>'}",
            f"date: {self.date}",
            "---",
        ]
        return "\n".join(lines)

    def to_markdown(self) -> str:
        return f"{self.front_matter()}\n\n{self.body()}\n"


def body_sha8(body: str) -> str:
    """正文 SHA-256 前 8 位，用于 event_id（interfaces.md §2）。"""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]


class DoubaoProvider:
    """真实 Doubao API 适配器骨架。

    密钥只经构造参数注入（生产环境来自环境变量 / Secrets），不写入仓库；
    未配置密钥时给出明确错误，避免静默降级。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "doubao-lite",
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def generate_opinion(self, context: str, counterpart_view: str, status: Dict[str, Any]) -> OpinionDraft:
        if not self.api_key:
            raise RuntimeError(
                "DOUBAO_API_KEY 未配置；请通过环境变量 / Secrets 注入，"
                "或在测试与演示中使用 MockDoubaoProvider"
            )
        # TODO: 接入 Doubao 对话 API，将模型输出解析为 OpinionDraft 字段。
        # 骨架保持契约完整；真实接入待 API key 与端点文档就绪后实现。
        raise NotImplementedError("Doubao API 接入待实现（需要 API key 与端点文档）")


class MockDoubaoProvider:
    """无密钥可运行的确定性 Provider，用于单测、E2E 与演示。

    生成基于模板的意见草稿，所有必填字段非空以满足 adds=true 校验。
    """

    def __init__(self, writer: str = "Doubao"):
        self.writer = writer

    def generate_opinion(self, context: str, counterpart_view: str, status: Dict[str, Any]) -> OpinionDraft:
        round_no = int(status.get("round", 0)) + 1  # 语义：round = status.round + 1
        return OpinionDraft(
            round=round_no,
            writer=self.writer,
            adds=True,
            status="proposed",
            date=time.strftime("%Y-%m-%d"),
            new_judgment=f"（mock）基于共享上下文与对方观点，形成 Round {round_no} 新增判断：{context[:40]}",
            counterpart_response=f"（mock）回应对方观点摘要：{counterpart_view[:40]}",
            improvement_plan="（mock）提出一个具体改进方案，等待对方确认。",
            open_questions="（mock）待确认问题：方案是否通过。",
            facts_evidence="（mock）无外部证据，纯模板输出。",
        )
