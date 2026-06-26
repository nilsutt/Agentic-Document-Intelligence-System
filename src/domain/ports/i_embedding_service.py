from typing import Protocol, List

class IEmbeddingService(Protocol):
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Converts a list of texts into a list of vector embeddings."""
        ...
        
    def embed_query(self, text: str) -> List[float]:
        """Converts a single query text into a vector embedding."""
        ...
