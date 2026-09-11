"""OpenAI Responses API provider."""
from __future__ import annotations
import json, os, urllib.request
from datetime import date
from typing import Any, Dict, Optional
from runner.providers.doubao import OpinionDraft


def _output_text(data: Dict[str, Any]) -> str:
    text = data.get("output_text")
    if isinstance(text, str) and text.strip():
        return text
    parts=[]
    for item in data.get("output", []):
        for content in item.get("content", []):
            value=content.get("text")
            if isinstance(value,str): parts.append(value)
    return "\n".join(parts)


class OpenAIProvider:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1/responses", model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GPT_API_KEY")
        self.base_url = base_url
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")

    def generate_opinion(self, context: str, counterpart_view: str, status: Dict[str, Any]) -> OpinionDraft:
        if not self.api_key: raise RuntimeError("OPENAI_API_KEY/GPT_API_KEY 未配置")
        round_no=int(status["round"])+1
        prompt=("你是 GPT，参与 GitHub 黑板 AI-to-AI 会议。只输出一个合法 JSON 对象，字段："
                "writer, adds, status, date, facts_evidence, new_judgment, counterpart_response, improvement_plan, open_questions。"
                f"writer=GPT；round={round_no}；status 只能是 proposed/confirmed/need_user_decision。\n"
                f"共享上下文：\n{context}\n\n对方最新观点：\n{counterpart_view}")
        payload={"model":self.model,"input":prompt}
        req=urllib.request.Request(self.base_url,data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=90) as response: data=json.loads(response.read().decode())
        raw=json.loads(_output_text(data))
        return OpinionDraft(round=round_no,writer="GPT",adds=bool(raw["adds"]),status=raw["status"],date=raw.get("date",str(date.today())),facts_evidence=raw.get("facts_evidence",""),new_judgment=raw.get("new_judgment",""),counterpart_response=raw.get("counterpart_response",""),improvement_plan=raw.get("improvement_plan",""),open_questions=raw.get("open_questions",""))
