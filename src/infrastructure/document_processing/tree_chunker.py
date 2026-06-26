from typing import List
import uuid
from src.domain.ports.i_document_processor import IDocumentChunker
from src.domain.models.document import RawDocument, DocumentNode, DocumentChunk

class TreeChunker(IDocumentChunker):
    def __init__(self, max_chunk_chars: int = 1500):
        self.max_chunk_chars = max_chunk_chars

    def chunk(self, doc: RawDocument) -> List[DocumentNode]:
        if not doc.nodes:
            return []
            
        # Build tree using stack
        stack = []
        root_nodes = []
        
        for node in doc.nodes:
            while stack and stack[-1].level >= node.level:
                stack.pop()
            if stack:
                stack[-1].children.append(node)
            else:
                root_nodes.append(node)
            stack.append(node)
            
        # Generate chunks for each node
        for node in doc.nodes:
            raw_text = node.__dict__.get("raw_text", "")
            node.chunks = self._split_text_to_chunks(raw_text, node)
            
        return root_nodes

    def _split_text_to_chunks(self, text: str, node: DocumentNode) -> List[DocumentChunk]:
        if not text.strip():
            return []
            
        chunks = []
        words = text.split()
        current_chunk_words = []
        current_length = 0
        
        for word in words:
            word_len = len(word) + 1
            if current_length + word_len > self.max_chunk_chars and current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                chunks.append(DocumentChunk(
                    id=str(uuid.uuid4()),
                    text=chunk_text,
                    level=node.level,
                    page=node.page_range[0],
                    parent_id=node.id,
                    metadata={"section_title": node.title}
                ))
                current_chunk_words = [word]
                current_length = len(word)
            else:
                current_chunk_words.append(word)
                current_length += word_len
                
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append(DocumentChunk(
                id=str(uuid.uuid4()),
                text=chunk_text,
                level=node.level,
                page=node.page_range[0],
                parent_id=node.id,
                metadata={"section_title": node.title}
            ))
            
        return chunks
