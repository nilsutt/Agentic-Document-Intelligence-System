# Placeholder for ChromaStore implementation (alternative to FAISS)
from typing import List
from src.domain.ports.i_vector_store import IVectorStore
from src.domain.models.document import DocumentChunk
from src.domain.models.query import RetrievedContext

class ChromaVectorStore(IVectorStore):
    def upsert(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        pass
        
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[RetrievedContext]:
        return []
        
    def delete(self, document_id: str) -> None:
        pass
