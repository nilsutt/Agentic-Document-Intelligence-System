from pydantic import BaseModel, Field
from typing import List, Optional

class ConfidenceScore(BaseModel):
    score: float
    reasoning: str

class ExtractionResult(BaseModel):
    extracted_text: str
    source_chunks: List[str] = Field(default_factory=list)
    confidence: ConfidenceScore

class ExtractionRequest(BaseModel):
    section_title: str
    target_fields: List[str] = Field(default_factory=list)
