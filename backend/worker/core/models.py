# app/models.py
from typing import List, Dict, Optional
from pydantic import BaseModel

class ScanRequest(BaseModel):
    filename: str
    content: str
    use_llm_centric: bool = False  # Enable LLM-centric detection (smarter, more expensive)

class FileData(BaseModel):
    filename: str
    content: str
    sha1: Optional[str] = None

class IndexRequest(BaseModel):
    files: List[FileData]
    project_key: Optional[str] = None

class AnalyzeRequest(BaseModel):
    project_structure: str
    system_prompt: str

class PocRequest(BaseModel):
    filename: str
    content: str
    findings: List[Dict]
    max_pocs: int = 2

class DeepWikiIndexRequest(IndexRequest):
    pass


class CrossFileConsistencyRequest(BaseModel):
    scan_id: str
    vulnerabilities: List[Dict]
