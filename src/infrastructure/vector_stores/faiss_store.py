import faiss
import pickle
import numpy as np
import logging
from typing import List
from pathlib import Path
from src.domain.ports.i_vector_store import IVectorStore
from src.domain.models.document import DocumentChunk
from src.domain.models.query import RetrievedContext
from src.domain.exceptions import VectorStoreError

logger = logging.getLogger(__name__)

class FaissVectorStore(IVectorStore):
    def __init__(self, dimension: int = 0, persist_path: str = "faiss_index.bin"):
        self.dimension = dimension
        self.persist_path = Path(persist_path)
        self.chunks: List[DocumentChunk] = []
        self.index = None
        self._try_load_from_disk()

    def _try_load_from_disk(self) -> None:
        if not self.persist_path.exists():
            return
        try:
            with open(f"{self.persist_path}_meta.pkl", "rb") as f:
                self.chunks = pickle.load(f)
            self.index = faiss.read_index(str(self.persist_path))
            self.dimension = self.index.d
        except Exception:
            logger.warning("Stale or corrupt FAISS index detected — resetting to empty.")
            self.index = None
            self.chunks = []
            self.dimension = 0

    def upsert(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        try:
            if not chunks:
                return
            
            actual_dim = len(embeddings[0])
            
            if self.index is None or self.index.d != actual_dim:
                if self.index is not None:
                    logger.warning(
                        f"FAISS dimension mismatch: index={self.index.d}, "
                        f"embeddings={actual_dim}. Recreating index."
                    )
                self.index = faiss.IndexFlatL2(actual_dim)
                self.dimension = actual_dim
                self.chunks = []  # Clear old incompatible chunks
                
            vectors = np.array(embeddings, dtype=np.float32)
            self.index.add(vectors)
            self.chunks.extend(chunks)
            self._save()
        except Exception as e:
            raise VectorStoreError(f"Failed to upsert to FAISS: {str(e)}") from e
            
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[RetrievedContext]:
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
                
            actual_dim = len(query_embedding)
            if self.index.d != actual_dim:
                logger.warning(f"Search query dimension mismatch: index={self.index.d}, query={actual_dim}")
                return []
                
            vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(vector, min(top_k, len(self.chunks)))
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    section_title = chunk.metadata.get("section_title", f"Level {chunk.level}")
                    results.append(
                        RetrievedContext(
                            chunk_id=chunk.id,
                            text=chunk.text,
                            score=float(dist),
                            page=chunk.page,
                            section_title=section_title
                        )
                    )
            return results
        except Exception as e:
            raise VectorStoreError(f"Failed to search in FAISS: {str(e)}") from e
            
    def delete(self, document_id: str) -> None:
        try:
            if self.index is None:
                return
                
            indices_to_keep = [
                i for i, c in enumerate(self.chunks) 
                if not (c.id.startswith(document_id) or (c.parent_id and c.parent_id.startswith(document_id)))
            ]
            
            if len(indices_to_keep) == len(self.chunks):
                return
                
            new_chunks = [self.chunks[i] for i in indices_to_keep]
            
            if self.index.ntotal > 0 and len(indices_to_keep) > 0:
                vectors = np.array([self.index.reconstruct(i) for i in indices_to_keep], dtype=np.float32)
            else:
                vectors = np.array([], dtype=np.float32)
                
            self.index = faiss.IndexFlatL2(self.dimension)
            if vectors.size > 0:
                self.index.add(vectors)
            self.chunks = new_chunks
            self._save()
        except Exception as e:
            raise VectorStoreError(f"Failed to delete from FAISS: {str(e)}") from e
            
    def _save(self) -> None:
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.persist_path))
                with open(f"{self.persist_path}_meta.pkl", "wb") as f:
                    pickle.dump(self.chunks, f)
        except Exception as e:
            logger.error(f"Failed to persist FAISS index: {str(e)}")
