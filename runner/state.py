"""Meeting state machine and transaction helpers."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
WRITERS=("GPT","Doubao")
STATUSES=("WAITING_GPT","WAITING_DOUBAO","NEED_USER_DECISION","DONE")
COMPLETIONS=("IN_PROGRESS","DONE")
@dataclass(frozen=True)
class MeetingState:
    round:int; last_writer:str; next_writer:str; status:str; completion:str; last_event:str
    @classmethod
    def from_dict(cls,data:Dict[str,Any])->"MeetingState": return cls(*(data[k] for k in ("round","last_writer","next_writer","status","completion","last_event")))
    def validate(self)->None:
        if not isinstance(self.round,int) or self.round<0: raise ValueError("round must be a non-negative integer")
        if self.last_writer not in WRITERS or self.next_writer not in WRITERS: raise ValueError("invalid writer")
        if self.status not in STATUSES: raise ValueError("invalid status")
        if self.completion not in COMPLETIONS: raise ValueError("invalid completion")
        if not self.last_event: raise ValueError("last_event is required")
        if self.status=="WAITING_GPT" and self.next_writer!="GPT": raise ValueError("WAITING_GPT requires next_writer=GPT")
        if self.status=="WAITING_DOUBAO" and self.next_writer!="Doubao": raise ValueError("WAITING_DOUBAO requires next_writer=Doubao")
        if self.status=="NEED_USER_DECISION" and self.round < 0: raise ValueError("invalid decision state")
def next_state(current:MeetingState,writer:str,event_id:str,status:str="proposed")->MeetingState:
    if writer!=current.next_writer: raise ValueError(f"wrong turn: expected {current.next_writer}, got {writer}")
    if status=="need_user_decision": state=MeetingState(current.round, current.last_writer, current.next_writer, "NEED_USER_DECISION", "IN_PROGRESS", event_id)
    else:
        other="Doubao" if writer=="GPT" else "GPT"; state=MeetingState(current.round+1,writer,other,f"WAITING_{other.upper()}","IN_PROGRESS",event_id)
    state.validate(); return state
def failure_state(current:MeetingState,event_id:str)->MeetingState:
    state=MeetingState(current.round,current.last_writer,current.next_writer,"NEED_USER_DECISION","IN_PROGRESS",event_id); state.validate(); return state
