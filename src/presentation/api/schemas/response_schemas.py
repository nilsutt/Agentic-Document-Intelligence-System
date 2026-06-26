from pydantic import BaseModel
from typing import List

class SourceReference(BaseModel):
    section_title: str
    page: int
    score: float
    chunk_id: str

class IngestResponse(BaseModel):
    message: str
    
class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceReference] = []
    conversation_id: str = ""

class ErrorResponse(BaseModel):
    error: str
    detail: str
