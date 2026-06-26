from typing import Protocol, List
from src.domain.models.document import DocumentChunk
from src.domain.models.query import RetrievedContext

class IVectorStore(Protocol):
    def upsert(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Inserts or updates chunks and their embeddings in the vector store."""
        ...
        
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[RetrievedContext]:
        """Performs a similarity search using the query embedding."""
        ...
        
    def delete(self, document_id: str) -> None:
        """Removes all chunks associated with a document_id."""
        ...
