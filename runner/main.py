"""Runner orchestration: read -> provider -> validate -> atomic blackboard commit."""
from __future__ import annotations
import argparse,json,time
from typing import Callable,Optional
from runner.github import GitHubBlackboard
from runner.validate import expected_event_id,validate_draft
from runner.state import MeetingState,failure_state,next_state
def parse_status(text:str)->MeetingState:
    values={}
    for line in text.splitlines():
        if line.startswith("- ") and ": " in line:
            key,value=line[2:].split(": ",1); values[key.strip()]=value.strip()
    return MeetingState.from_dict({"round":int(values["Round"]),"last_writer":values["Last writer"],"next_writer":values["Next writer"],"status":values["Status"],"completion":values["Completion"],"last_event":values["Last event"]})
def render_status(state:MeetingState)->str:
    return ("# Meeting Status\n\n"+f"- Round: {state.round}\n- Last writer: {state.last_writer}\n- Next writer: {state.next_writer}\n- Status: {state.status}\n- Completion: {state.completion}\n- Last event: {state.last_event}\n\n## Turn Rule\n\n下一位 AI 必须先读取 `context.md`、双方最新观点和本文件，再写入自己的观点，并更新状态。\n\n## Current Topic\n\nRunner MVP 正在实现：状态机、Provider、GitHub 黑板提交与可测试性。\n")
def run_turn(blackboard:GitHubBlackboard,provider_factory:Callable[[],object],dry_run:bool=False,retries:int=3)->str:
    current=parse_status(blackboard.read("meeting/status.md")); context=blackboard.read("meeting/context.md"); counterpart=blackboard.read("meeting/doubao.md" if current.next_writer=="GPT" else "meeting/gpt.md"); last_error=None
    for attempt in range(retries):
        try:
            draft=provider_factory().generate_opinion(context,counterpart,current.__dict__); validate_draft(draft,current); draft.event_id=expected_event_id(draft); break
        except Exception as exc:
            last_error=exc
            if attempt+1<retries: time.sleep(2**attempt)
    else:
        event_id=f"R{current.round}-{current.next_writer}-00000000"; failed=failure_state(current,event_id)
        if dry_run: return event_id
        log=json.dumps({"event":"failed","event_id":event_id,"error":str(last_error)},ensure_ascii=False)+"\n"
        blackboard.write_many({"meeting/status.md":render_status(failed),"meeting/logs/runner.jsonl":log}); blackboard.commit(["meeting/status.md","meeting/logs/runner.jsonl"],f"Runner failure: {event_id}"); return event_id
    new_state=next_state(current,draft.writer,draft.event_id,draft.status)
    if dry_run: return draft.event_id
    writer_file="meeting/gpt.md" if draft.writer=="GPT" else "meeting/doubao.md"; log=json.dumps({"event":"turn","event_id":draft.event_id,"writer":draft.writer,"round":draft.round},ensure_ascii=False)+"\n"
    blackboard.write_many({writer_file:draft.to_markdown(),"meeting/status.md":render_status(new_state),"meeting/logs/runner.jsonl":log}); return blackboard.commit([writer_file,"meeting/status.md","meeting/logs/runner.jsonl"],f"Runner: {draft.event_id}")
def main(argv:Optional[list[str]]=None,provider_factory:Optional[Callable[[],object]]=None)->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--target-dir",default="."); parser.add_argument("--dry-run",action="store_true"); args=parser.parse_args(argv)
    if provider_factory is None: raise RuntimeError("production provider factory must be supplied by the entrypoint")
    run_turn(GitHubBlackboard(args.target_dir),provider_factory,args.dry_run); return 0
if __name__=="__main__": raise SystemExit(main())
