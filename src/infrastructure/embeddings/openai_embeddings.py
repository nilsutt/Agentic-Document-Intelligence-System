from typing import List
import openai
from src.domain.ports.i_embedding_service import IEmbeddingService
from src.domain.exceptions import AgenticPlatformError
from src.infrastructure.llm.resilience import with_retry, llm_circuit_breaker
import pybreaker

class OpenAIEmbeddingService(IEmbeddingService):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        @with_retry
        def _call():
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
            
        try:
            return llm_circuit_breaker.call(_call)
        except pybreaker.CircuitBreakerError as e:
            raise AgenticPlatformError("Circuit breaker open: Embedding service is temporarily unavailable.") from e
        except Exception as e:
            raise AgenticPlatformError(f"Failed to generate embeddings: {str(e)}") from e

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
