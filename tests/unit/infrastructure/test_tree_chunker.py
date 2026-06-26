from src.infrastructure.document_processing.tree_chunker import TreeChunker
from src.domain.models.document import RawDocument, DocumentNode

def make_node(id, title, level, page=1, raw_text=""):
    n = DocumentNode(id=id, title=title, level=level, page_range=[page, page])
    n.__dict__["raw_text"] = raw_text
    return n

def test_single_node_produces_chunk():
    chunker = TreeChunker()
    n = make_node("n1", "Introduction", 1, raw_text="Hello world content.")
    doc = RawDocument(path="test.pdf", toc_available=True, nodes=[n])
    roots = chunker.chunk(doc)
    
    assert len(roots) == 1
    assert len(roots[0].chunks) == 1
    assert roots[0].chunks[0].metadata["section_title"] == "Introduction"
    assert roots[0].chunks[0].parent_id == "n1"

def test_hierarchy_h1_h2():
    chunker = TreeChunker()
    h1 = make_node("h1", "Chapter", 1, raw_text="Chapter content.")
    h2 = make_node("h2", "Section", 2, raw_text="Section content.")
    doc = RawDocument(path="test.pdf", toc_available=True, nodes=[h1, h2])
    roots = chunker.chunk(doc)
    
    assert len(roots) == 1  # only h1 is root
    assert len(roots[0].children) == 1  # h2 is child of h1
    assert roots[0].children[0].id == "h2"

def test_text_split_at_max_chars():
    chunker = TreeChunker(max_chunk_chars=20)
    long_text = "word " * 20   # 100 chars
    n = make_node("n1", "Long", 1, raw_text=long_text)
    doc = RawDocument(path="test.pdf", toc_available=True, nodes=[n])
    roots = chunker.chunk(doc)
    
    assert len(roots[0].chunks) > 1
