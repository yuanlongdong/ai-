"""OpenAI provider adapter."""
from __future__ import annotations
import json,os,urllib.request
from datetime import date
from typing import Any,Dict,Optional
from runner.providers.doubao import OpinionDraft
class OpenAIProvider:
    def __init__(self,api_key:Optional[str]=None,base_url:str="https://api.openai.com/v1/responses",model:Optional[str]=None): self.api_key=api_key or os.getenv("OPENAI_API_KEY"); self.base_url=base_url; self.model=model or os.getenv("OPENAI_MODEL","gpt-5.6")
    def generate_opinion(self,context:str,counterpart_view:str,status:Dict[str,Any])->OpinionDraft:
        if not self.api_key: raise RuntimeError("OPENAI_API_KEY 未配置")
        round_no=int(status["round"])+1
        prompt=f"你是 GPT，参与 GitHub 黑板 AI-to-AI 会议。只输出 JSON，字段：writer, adds, status, date, facts_evidence, new_judgment, counterpart_response, improvement_plan, open_questions。writer=GPT；round={round_no}。共享上下文：\n{context}\n\n对方观点：\n{counterpart_view}"
        payload={"model":self.model,"input":prompt}; req=urllib.request.Request(self.base_url,data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=60) as response: data=json.loads(response.read().decode())
        raw=json.loads(data.get("output_text", "")); return OpinionDraft(round=round_no,writer="GPT",adds=bool(raw["adds"]),status=raw["status"],date=raw.get("date",str(date.today())),facts_evidence=raw.get("facts_evidence",""),new_judgment=raw.get("new_judgment",""),counterpart_response=raw.get("counterpart_response",""),improvement_plan=raw.get("improvement_plan",""),open_questions=raw.get("open_questions",""))
