"""执行日志与可观测性（Doubao 模块）。

契约：Runner 在每次事务开始 / 结束各记一条 JSONL 记录；
幂等判断依赖 event_id（interfaces.md §3 step 5）。
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

DEFAULT_LOG_PATH = Path("meeting/logs/runner.jsonl")


@dataclass
class LogRecord:
    ts: str            # ISO8601 时间戳
    event_id: str
    round: int
    writer: str
    result: str        # started | ok | failed | skipped
    message: str = ""

    @classmethod
    def now(cls, event_id: str, round_no: int, writer: str, result: str, message: str = "") -> "LogRecord":
        return cls(
            ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            event_id=event_id,
            round=round_no,
            writer=writer,
            result=result,
            message=message,
        )


def append_record(log_path: Path, record: LogRecord) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def load_records(log_path: Path) -> List[LogRecord]:
    if not log_path.exists():
        return []
    records: List[LogRecord] = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(LogRecord(**json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                continue  # 跳过损坏行，日志不阻塞流程
    return records


def is_processed(log_path: Path, event_id: str) -> bool:
    """幂等判断：该 event_id 是否已成功处理过（result == ok）。"""
    return any(r.event_id == event_id and r.result == "ok" for r in load_records(log_path))
