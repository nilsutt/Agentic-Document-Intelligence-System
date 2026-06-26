import pytest
from unittest.mock import create_autospec, Mock
from fastapi.testclient import TestClient

from src.domain.ports.i_document_processor import IDocumentProcessor, IDocumentChunker
from src.domain.ports.i_vector_store import IVectorStore
from src.domain.ports.i_embedding_service import IEmbeddingService
from src.domain.ports.i_llm_client import ILLMClient
from src.domain.ports.i_failure_logger import IFailureLogger
from src.domain.models.query import QueryResult

from src.presentation.api.app import app
from src.presentation.api.dependencies import (
    get_ingestion_service, get_retrieval_service, get_document_agent
)

@pytest.fixture
def mock_processor():
    return create_autospec(IDocumentProcessor)

@pytest.fixture
def mock_chunker():
    return create_autospec(IDocumentChunker)

@pytest.fixture
def mock_vector_store():
    return create_autospec(IVectorStore)

@pytest.fixture
def mock_embedding_service():
    return create_autospec(IEmbeddingService)

@pytest.fixture
def mock_llm_client():
    return create_autospec(ILLMClient)

@pytest.fixture
def mock_failure_logger():
    return create_autospec(IFailureLogger)

@pytest.fixture
def mock_retrieval_service():
    svc = Mock()
    svc.search.return_value = QueryResult(answer="", contexts=[])
    svc.search_and_format.return_value = "No results."
    return svc

@pytest.fixture
def api_client(mock_processor, mock_retrieval_service):
    mock_ingest = Mock()
    mock_ingest.ingest.return_value = "Successfully ingested 3 chunks from test.pdf"
    
    mock_agent = Mock()
    mock_agent.run.return_value = "The document discusses interest rates."

    app.dependency_overrides[get_ingestion_service] = lambda: mock_ingest
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval_service
    app.dependency_overrides[get_document_agent] = lambda: mock_agent
    yield TestClient(app)
    app.dependency_overrides.clear()
