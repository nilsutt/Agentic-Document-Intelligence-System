import logging
from pathlib import Path
from src.domain.ports.i_document_processor import IDocumentProcessor, IDocumentChunker
from src.domain.ports.i_vector_store import IVectorStore
from src.domain.ports.i_embedding_service import IEmbeddingService
from src.domain.ports.i_failure_logger import IFailureLogger
from src.domain.models.document import DocumentNode, DocumentChunk

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    def __init__(
        self,
        processor: IDocumentProcessor,
        chunker: IDocumentChunker,
        vector_store: IVectorStore,
        embedding_service: IEmbeddingService,
        failure_logger: IFailureLogger
    ):
        self.processor = processor
        self.chunker = chunker
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.failure_logger = failure_logger

    def ingest(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            logger.info(f"Starting ingestion for {file_path}")
            
            doc = self.processor.process_pdf(path)
            nodes = self.chunker.chunk(doc)
            
            all_chunks = []
            for node in nodes:
                all_chunks.extend(self._collect_chunks(node))
                
            if not all_chunks:
                logger.warning(f"No chunks generated for {file_path}")
                return "No content to ingest."
                
            texts = [chunk.text for chunk in all_chunks]
            embeddings = self.embedding_service.embed_texts(texts)
            
            self.vector_store.upsert(all_chunks, embeddings)
            
            logger.info(f"Ingestion complete for {file_path}, num_chunks={len(all_chunks)}")
            return f"Successfully ingested {len(all_chunks)} chunks from {path.name}"
            
        except Exception as e:
            logger.error(f"Ingestion failed for {file_path}: {str(e)}")
            self.failure_logger.log_failed_document(file_path, e)
            raise

    def _collect_chunks(self, node: DocumentNode) -> list[DocumentChunk]:
        """Recursively gathers chunks from node and all its children."""
        chunks = list(node.chunks)
        for child in node.children:
            chunks.extend(self._collect_chunks(child))
        return chunks
