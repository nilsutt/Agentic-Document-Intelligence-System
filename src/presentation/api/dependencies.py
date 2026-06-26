from functools import lru_cache
from pydantic_settings import BaseSettings

from src.infrastructure.document_processing.pymupdf_processor import PyMuPDFProcessor
from src.infrastructure.document_processing.tree_chunker import TreeChunker
from src.infrastructure.vector_stores.faiss_store import FaissVectorStore
from src.infrastructure.observability.dead_letter_logger import DeadLetterLogger

from src.infrastructure.factories.llm_factory import LLMFactory
from src.infrastructure.factories.embedding_factory import EmbeddingFactory

from src.application.services.document_ingestion_service import DocumentIngestionService
from src.application.services.knowledge_retrieval_service import KnowledgeRetrievalService
from src.application.agents.document_analyst_agent import DocumentAnalystAgent

class Settings(BaseSettings):
    llm_provider: str = "ollama"           # "ollama" | "openai"
    embedding_provider: str = "ollama"     # "ollama" | "openai"
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"
    
    openai_api_key: str = ""               # Boş string; OpenAI gerektiğinde doldurulur
    openai_llm_model: str = "gpt-3.5-turbo"
    openai_embed_model: str = "text-embedding-3-small"
    
    vector_store_type: str = "faiss"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_vector_store():
    settings = get_settings()
    if settings.vector_store_type == "faiss":
        return FaissVectorStore()
    return FaissVectorStore()

@lru_cache()
def get_llm_factory() -> LLMFactory:
    s = get_settings()
    return LLMFactory(
        provider=s.llm_provider,
        ollama_model=s.ollama_llm_model, ollama_base_url=s.ollama_base_url,
        openai_api_key=s.openai_api_key, openai_model=s.openai_llm_model
    )

@lru_cache()
def get_embedding_factory() -> EmbeddingFactory:
    s = get_settings()
    return EmbeddingFactory(
        provider=s.embedding_provider,
        ollama_model=s.ollama_embed_model, ollama_base_url=s.ollama_base_url,
        openai_api_key=s.openai_api_key, openai_model=s.openai_embed_model
    )

@lru_cache()
def get_llm_client():
    return get_llm_factory().create_client()

@lru_cache()
def get_chat_model():
    return get_llm_factory().create_chat_model()

@lru_cache()
def get_embedding_service():
    return get_embedding_factory().create()

@lru_cache()
def get_document_processor():
    return PyMuPDFProcessor()

@lru_cache()
def get_document_chunker():
    return TreeChunker()

@lru_cache()
def get_failure_logger():
    return DeadLetterLogger()

def get_ingestion_service() -> DocumentIngestionService:
    return DocumentIngestionService(
        processor=get_document_processor(),
        chunker=get_document_chunker(),
        vector_store=get_vector_store(),
        embedding_service=get_embedding_service(),
        failure_logger=get_failure_logger()
    )

def get_retrieval_service() -> KnowledgeRetrievalService:
    return KnowledgeRetrievalService(
        vector_store=get_vector_store(),
        embedding_service=get_embedding_service()
    )

def get_document_agent() -> DocumentAnalystAgent:
    return DocumentAnalystAgent(
        chat_model=get_chat_model(),
        llm_client=get_llm_client()
    )
