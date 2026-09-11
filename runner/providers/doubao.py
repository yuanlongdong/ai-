"""Doubao / Volcano Ark Responses API provider."""
from __future__ import annotations
import hashlib, json, os, time, urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class OpinionDraft:
    round:int; writer:str; adds:bool; status:str; date:str
    facts_evidence:str=""; new_judgment:str=""; counterpart_response:str=""; improvement_plan:str=""; open_questions:str=""; event_id:str=""
    def body(self)->str:
        return "\n\n".join(f"## {t}\n\n{v}" for t,v in (("新增判断",self.new_judgment),("对对方的回应",self.counterpart_response),("改进方案",self.improvement_plan),("待确认问题",self.open_questions),("事实/证据",self.facts_evidence)))
    def front_matter(self)->str:
        return "\n".join(["---",f"round: {self.round}",f"writer: {self.writer}",f"adds: {'true' if self.adds else 'false'}",f"status: {self.status}",f"event_id: {self.event_id or '<pending>'}",f"date: {self.date}","---"])
    def to_markdown(self)->str: return f"{self.front_matter()}\n\n{self.body()}\n"

def body_sha8(body:str)->str: return hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]

def _output_text(data:Dict[str,Any])->str:
    text=data.get("output_text")
    if isinstance(text,str) and text.strip(): return text
    parts=[]
    for item in data.get("output",[]):
        for content in item.get("content",[]):
            value=content.get("text")
            if isinstance(value,str): parts.append(value)
    return "\n".join(parts)

class DoubaoProvider:
    def __init__(self,api_key:Optional[str]=None,base_url:Optional[str]=None,model:Optional[str]=None):
        self.api_key=api_key or os.getenv("DOUBAO_API_KEY") or os.getenv("ARK_API_KEY")
        self.base_url=base_url or os.getenv("DOUBAO_BASE_URL","https://ark.cn-beijing.volces.com/api/v3/responses")
        self.model=model or os.getenv("DOUBAO_MODEL","doubao-seed-2-1-260615")
    def generate_opinion(self,context:str,counterpart_view:str,status:Dict[str,Any])->OpinionDraft:
        if not self.api_key: raise RuntimeError("DOUBAO_API_KEY/ARK_API_KEY 未配置")
        round_no=int(status["round"])+1
        prompt=("你是 Doubao，参与 GitHub 黑板 AI-to-AI 会议。只输出一个合法 JSON 对象，字段：writer, adds, status, date, facts_evidence, new_judgment, counterpart_response, improvement_plan, open_questions。"
                f"writer=Doubao；round={round_no}；status 只能是 proposed/confirmed/need_user_decision。\n共享上下文：\n{context}\n\n对方最新观点：\n{counterpart_view}")
        payload={"model":self.model,"input":prompt}
        req=urllib.request.Request(self.base_url,data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=90) as response: data=json.loads(response.read().decode())
        raw=json.loads(_output_text(data))
        return OpinionDraft(round=round_no,writer="Doubao",adds=bool(raw["adds"]),status=raw["status"],date=raw.get("date",time.strftime("%Y-%m-%d")),facts_evidence=raw.get("facts_evidence",""),new_judgment=raw.get("new_judgment",""),counterpart_response=raw.get("counterpart_response",""),improvement_plan=raw.get("improvement_plan",""),open_questions=raw.get("open_questions",""))

class MockDoubaoProvider:
    def __init__(self,writer:str="Doubao"): self.writer=writer
    def generate_opinion(self,context:str,counterpart_view:str,status:Dict[str,Any])->OpinionDraft:
        n=int(status.get("round",0))+1
        return OpinionDraft(n,self.writer,True,"proposed",time.strftime("%Y-%m-%d"),"（mock）无外部证据。",f"（mock）Round {n} 新增判断：{context[:40]}",f"（mock）回应：{counterpart_view[:40]}","（mock）提出具体改进方案。","（mock）等待确认。")
