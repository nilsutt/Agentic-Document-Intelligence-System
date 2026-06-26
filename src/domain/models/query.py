from pydantic import BaseModel, Field
from typing import List

class RetrievedContext(BaseModel):
    chunk_id: str
    text: str
    score: float
    page: int
    section_title: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResult(BaseModel):
    answer: str
    contexts: List[RetrievedContext] = Field(default_factory=list)
