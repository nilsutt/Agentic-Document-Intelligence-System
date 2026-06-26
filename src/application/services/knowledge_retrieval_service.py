from typing import List
from src.domain.ports.i_vector_store import IVectorStore
from src.domain.ports.i_embedding_service import IEmbeddingService
from src.domain.models.query import QueryRequest, QueryResult, RetrievedContext

class KnowledgeRetrievalService:
    def __init__(self, vector_store: IVectorStore, embedding_service: IEmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        
    def search(self, request: QueryRequest) -> QueryResult:
        query_emb = self.embedding_service.embed_query(request.question)
        contexts = self.vector_store.search(query_emb, request.top_k)
        
        return QueryResult(
            answer="",
            contexts=contexts
        )
        
    def search_and_format(self, question: str, top_k: int = 5) -> str:
        """Performs search and returns LLM-ready context string."""
        query_emb = self.embedding_service.embed_query(question)
        contexts = self.vector_store.search(query_emb, top_k)
        return self._format_context(contexts)

    def _format_context(self, contexts: List[RetrievedContext]) -> str:
        if not contexts:
            return "No relevant information found in the indexed documents."
        parts = [
            f"[Source: {ctx.section_title} | Page {ctx.page} | Score: {ctx.score:.3f}]\n{ctx.text}"
            for ctx in contexts
        ]
        return "\n\n---\n\n".join(parts)
