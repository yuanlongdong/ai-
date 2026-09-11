"""Runner orchestration: provider -> validation -> atomic blackboard commit."""
from __future__ import annotations
import argparse, os, time
from typing import Callable, Optional
from runner.github import GitHubBlackboard
from runner.logging import LogRecord, append_record, is_processed
from runner.validate import expected_event_id, validate_draft
from runner.state import MeetingState, failure_state, next_state
from runner.providers.openai import OpenAIProvider
from runner.providers.doubao import DoubaoProvider

def parse_status(text:str)->MeetingState:
    values={}
    for line in text.splitlines():
        if line.startswith("- ") and ": " in line:
            key,value=line[2:].split(": ",1); values[key.strip()]=value.strip()
    return MeetingState.from_dict({"round":int(values["Round"]),"last_writer":values["Last writer"],"next_writer":values["Next writer"],"status":values["Status"],"completion":values["Completion"],"last_event":values["Last event"]})

def render_status(state:MeetingState,topic:str="真实 API 自动闭环")->str:
    return ("# Meeting Status\n\n"+f"- Round: {state.round}\n- Last writer: {state.last_writer}\n- Next writer: {state.next_writer}\n- Status: {state.status}\n- Completion: {state.completion}\n- Last event: {state.last_event}\n\n## Turn Rule\n\n下一位 AI 必须先读取 `context.md`、双方最新观点和本文件，再写入自己的观点，并更新状态。\n\n## Current Topic\n\n{topic}\n")

def production_provider_factory(status:MeetingState):
    if status.next_writer=="GPT": return OpenAIProvider()
    if status.next_writer=="Doubao": return DoubaoProvider()
    raise RuntimeError(f"没有可执行的 next_writer: {status.next_writer}")

def run_turn(blackboard:GitHubBlackboard,provider_factory:Callable[[],object],dry_run:bool=False,retries:int=3)->str:
    current=parse_status(blackboard.read("meeting/status.md"))
    if current.status in {"DONE","NEED_USER_DECISION"} or current.next_writer=="NONE": return current.last_event
    context=blackboard.read("meeting/context.md")
    counterpart=blackboard.read("meeting/doubao.md" if current.next_writer=="GPT" else "meeting/gpt.md")
    last_error=None
    for attempt in range(retries):
        try:
            draft=provider_factory().generate_opinion(context,counterpart,current.__dict__)
            validate_draft(draft,current); draft.event_id=expected_event_id(draft)
            if is_processed(blackboard.root/"meeting/logs/runner.jsonl",draft.event_id): return draft.event_id
            break
        except Exception as exc:
            last_error=exc
            if attempt+1<retries: time.sleep(2**attempt)
    else:
        event_id=f"R{current.round+1}-{current.next_writer}-00000000"; failed=failure_state(current,event_id)
        if dry_run: return event_id
        log_path=blackboard.root/"meeting/logs/runner.jsonl"
        append_record(log_path,LogRecord.now(event_id,current.round,current.next_writer,"failed",str(last_error)))
        blackboard.write_many({"meeting/status.md":render_status(failed,"Runner 失败：等待用户决策。"),"meeting/logs/runner.jsonl":blackboard.read("meeting/logs/runner.jsonl")})
        blackboard.commit(["meeting/status.md","meeting/logs/runner.jsonl"],f"Runner failure: {event_id}")
        blackboard.push_with_retry()
        return event_id
    if dry_run: return draft.event_id
    new_state=next_state(current,draft.writer,draft.event_id,draft.status)
    writer_file="meeting/gpt.md" if draft.writer=="GPT" else "meeting/doubao.md"
    append_record(blackboard.root/"meeting/logs/runner.jsonl",LogRecord.now(draft.event_id,draft.round,draft.writer,"ok"))
    blackboard.write_many({writer_file:draft.to_markdown(),"meeting/status.md":render_status(new_state),"meeting/logs/runner.jsonl":blackboard.read("meeting/logs/runner.jsonl")})
    commit=blackboard.commit([writer_file,"meeting/status.md","meeting/logs/runner.jsonl"],f"Runner: {draft.event_id}")
    blackboard.push_with_retry()
    return commit

def main(argv:Optional[list[str]]=None,provider_factory:Optional[Callable[[],object]]=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--target-dir",default="."); parser.add_argument("--dry-run",action="store_true"); parser.add_argument("--once",action="store_true"); args=parser.parse_args(argv)
    bb=GitHubBlackboard(args.target_dir); status=parse_status(bb.read("meeting/status.md"))
    factory=provider_factory or (lambda: production_provider_factory(status))
    run_turn(bb,factory,args.dry_run); return 0
if __name__=="__main__": raise SystemExit(main())
