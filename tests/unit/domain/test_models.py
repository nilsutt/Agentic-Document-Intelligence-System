from src.domain.models.document import DocumentChunk, DocumentNode, RawDocument
from src.domain.models.query import QueryRequest
from pydantic import ValidationError
import pytest

def test_document_chunk_validation():
    chunk = DocumentChunk(id="1", text="hello", level=1, page=1)
    assert chunk.id == "1"
    
    with pytest.raises(ValidationError):
        DocumentChunk(id="1", text="hello")  # Missing required fields

def test_document_node_tree_structure():
    parent = DocumentNode(id="p1", title="Chapter 1", level=1, page_range=[1, 5])
    child = DocumentNode(id="c1", title="Section 1.1", level=2, page_range=[2, 3])
    parent.children.append(child)
    assert len(parent.children) == 1
    assert parent.children[0].id == "c1"

def test_query_request_default_top_k():
    req = QueryRequest(question="test")
    assert req.top_k == 5

def test_raw_document_toc_available():
    doc = RawDocument(path="test.pdf", toc_available=True, nodes=[])
    assert doc.toc_available is True
