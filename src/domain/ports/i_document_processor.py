from typing import Protocol
from pathlib import Path
from src.domain.models.document import RawDocument, DocumentNode

class IDocumentProcessor(Protocol):
    def process_pdf(self, file_path: Path) -> RawDocument:
        """Parses the PDF and returns a raw document with TOC/headings structure."""
        ...

class IDocumentChunker(Protocol):
    def chunk(self, doc: RawDocument) -> list[DocumentNode]:
        """Converts a RawDocument into a hierarchical tree of DocumentNodes."""
        ...
