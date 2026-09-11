"""轮询 / 触发模块（Doubao 模块）。

职责：检测 status 是否轮到指定 AI、事件是否已处理（幂等），并触发一轮事务。
事务编排与提交逻辑在 runner/main.py（GPT 模块）；本模块只负责"何时触发"。
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

from . import logging as runner_logging

DEFAULT_INTERVAL_SEC = 60
TARGET_WRITER = "Doubao"


def should_run(status: Dict[str, Any], log_path, writer: str = TARGET_WRITER):
    """判断是否需要执行一轮，返回 (是否执行, 原因)。

    幂等依据：status 的 last_event 已在执行日志中成功处理过。
    """
    state = status.get("status", "")
    if state == "DONE":
        return False, "会议已结束（DONE）"
    if state == "NEED_USER_DECISION":
        return False, "等待用户决策（NEED_USER_DECISION）"
    if status.get("next_writer", "") != writer:
        return False, f"当前轮到 {status.get('next_writer')}，不是 {writer}"
    last_event = status.get("last_event", "")
    if last_event and runner_logging.is_processed(log_path, last_event):
        return False, f"事件 {last_event} 已处理（幂等跳过）"
    return True, "轮到本 AI 且事件未处理"


def poll_once(
    status_reader: Callable[[], Dict[str, Any]],
    turn_runner: Callable[[Dict[str, Any]], Any],
    log_path,
    writer: str = TARGET_WRITER,
) -> str:
    """执行一次轮询：读取状态 -> 判断 -> 触发事务。返回结果描述。"""
    status = status_reader()
    run, reason = should_run(status, log_path, writer)
    if not run:
        return f"SKIP: {reason}"
    return f"RUN: {turn_runner(status)}"


def poll_loop(
    status_reader: Callable[[], Dict[str, Any]],
    turn_runner: Callable[[Dict[str, Any]], Any],
    log_path,
    interval_sec: int = DEFAULT_INTERVAL_SEC,
    writer: str = TARGET_WRITER,
    max_loops: Optional[int] = None,
) -> None:
    """持续轮询；max_loops 供测试 / 演示限制次数。"""
    loops = 0
    while max_loops is None or loops < max_loops:
        loops += 1
        outcome = poll_once(status_reader, turn_runner, log_path, writer)
        print(f"[trigger] {outcome}")
        if outcome.startswith("SKIP") and "DONE" in outcome:
            break
        time.sleep(interval_sec)
