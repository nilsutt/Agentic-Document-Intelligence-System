from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentChunk(BaseModel):
    id: str
    text: str
    parent_id: Optional[str] = None
    level: int
    page: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentNode(BaseModel):
    id: str
    title: str
    level: int
    page_range: List[int]
    chunks: List[DocumentChunk] = Field(default_factory=list)
    children: List['DocumentNode'] = Field(default_factory=list)

class RawDocument(BaseModel):
    path: str
    toc_available: bool
    nodes: List[DocumentNode] = Field(default_factory=list)
