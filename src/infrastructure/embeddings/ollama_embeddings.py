from typing import List
from langchain_ollama import OllamaEmbeddings
from src.domain.ports.i_embedding_service import IEmbeddingService
from src.domain.exceptions import AgenticPlatformError

class OllamaEmbeddingService(IEmbeddingService):
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.embeddings = OllamaEmbeddings(model=model, base_url=base_url)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise AgenticPlatformError(f"Ollama embedding failed: {e}") from e

    def embed_query(self, text: str) -> List[float]:
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise AgenticPlatformError(f"Ollama query embedding failed: {e}") from e
