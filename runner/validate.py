"""Validation for provider drafts and persisted meeting state."""
from __future__ import annotations
import hashlib,re
from typing import Any
from runner.state import MeetingState
EVENT_RE=re.compile(r"^R(\d+)-(GPT|Doubao)-([0-9a-f]{8})$")
REQUIRED_TEXT=("new_judgment","counterpart_response","improvement_plan","open_questions","facts_evidence")
def body_sha8(draft:Any)->str: return hashlib.sha256(draft.body().encode("utf-8")).hexdigest()[:8]
def expected_event_id(draft:Any)->str: return f"R{draft.round}-{draft.writer}-{body_sha8(draft)}"
def validate_draft(draft:Any,current:MeetingState)->None:
    if draft.writer!=current.next_writer: raise ValueError(f"wrong writer: expected {current.next_writer}, got {draft.writer}")
    if draft.round!=current.round+1: raise ValueError("draft.round must equal status.round + 1")
    if draft.writer not in ("GPT","Doubao"): raise ValueError("invalid writer")
    if draft.status not in ("proposed","confirmed","need_user_decision"): raise ValueError("invalid draft status")
    if draft.adds:
        for field in REQUIRED_TEXT:
            if not str(getattr(draft,field,"")).strip(): raise ValueError(f"adds=true requires non-empty {field}")
    if draft.event_id and draft.event_id!=expected_event_id(draft): raise ValueError("event_id does not match draft body")
def validate_event_id(event_id:str)->None:
    if not EVENT_RE.fullmatch(event_id): raise ValueError("invalid event_id")
