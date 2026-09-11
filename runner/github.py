"""Small git-backed blackboard abstraction used by Runner."""
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Dict,Iterable
class GitHubBlackboard:
    def __init__(self,root:str|Path):
        self.root=Path(root).resolve()
        if not (self.root/".git").exists(): raise ValueError(f"not a git checkout: {self.root}")
    def read(self,relative_path:str)->str: return (self.root/relative_path).read_text(encoding="utf-8")
    def write_many(self,files:Dict[str,str])->None:
        for path,content in files.items():
            target=self.root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(content,encoding="utf-8")
    def commit(self,files:Iterable[str],message:str)->str:
        paths=list(files); subprocess.run(["git","add",*paths],cwd=self.root,check=True)
        result=subprocess.run(["git","diff","--cached","--quiet"],cwd=self.root)
        if result.returncode==0: return self.head()
        subprocess.run(["git","commit","-m",message],cwd=self.root,check=True); return self.head()
    def head(self)->str: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=self.root,text=True).strip()
    def push(self,remote:str="origin",branch:str="main")->None: subprocess.run(["git","push",remote,branch],cwd=self.root,check=True)
