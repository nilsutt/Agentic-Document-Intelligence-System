from src.infrastructure.vector_stores.faiss_store import FaissVectorStore
from src.domain.models.document import DocumentChunk

def test_faiss_store_upsert_and_search(tmp_path):
    store = FaissVectorStore(dimension=2, persist_path=str(tmp_path / "faiss.bin"))
    chunks = [DocumentChunk(id="1", text="test", level=1, page=1)]
    embeddings = [[0.5, 0.5]]
    
    store.upsert(chunks, embeddings)
    results = store.search([0.5, 0.5], top_k=1)
    
    assert len(results) == 1
    assert results[0].chunk_id == "1"
