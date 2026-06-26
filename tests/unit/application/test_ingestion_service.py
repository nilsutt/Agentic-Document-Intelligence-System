from src.application.services.document_ingestion_service import DocumentIngestionService
from src.domain.models.document import RawDocument, DocumentNode, DocumentChunk
import pytest

def test_ingestion_service(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger):
    svc = DocumentIngestionService(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger)
    
    node = DocumentNode(id="n1", title="Title", level=1, page_range=[1,1])
    node.chunks.append(DocumentChunk(id="c1", text="Content", level=1, page=1))
    
    mock_processor.process_pdf.return_value = RawDocument(path="test.pdf", toc_available=True, nodes=[node])
    mock_chunker.chunk.return_value = [node]
    mock_embedding_service.embed_texts.return_value = [[0.1, 0.2]]
    
    result = svc.ingest("test.pdf")
    assert "Successfully ingested" in result
    mock_vector_store.upsert.assert_called_once()

def test_ingestion_empty_doc(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger):
    svc = DocumentIngestionService(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger)
    
    mock_processor.process_pdf.return_value = RawDocument(path="empty.pdf", toc_available=False, nodes=[])
    mock_chunker.chunk.return_value = []
    
    result = svc.ingest("empty.pdf")
    assert result == "No content to ingest."

def test_ingestion_logs_failure(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger):
    svc = DocumentIngestionService(mock_processor, mock_chunker, mock_vector_store, mock_embedding_service, mock_failure_logger)
    
    mock_processor.process_pdf.side_effect = RuntimeError("corrupt pdf")
    
    with pytest.raises(RuntimeError):
        svc.ingest("bad.pdf")
        
    mock_failure_logger.log_failed_document.assert_called_once()
