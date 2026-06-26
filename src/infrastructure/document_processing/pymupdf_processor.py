import fitz
import statistics
from pathlib import Path
from src.domain.ports.i_document_processor import IDocumentProcessor
from src.domain.models.document import RawDocument, DocumentNode
from src.domain.exceptions import DocumentProcessingError

class PyMuPDFProcessor(IDocumentProcessor):
    def process_pdf(self, file_path: Path) -> RawDocument:
        try:
            doc = fitz.open(str(file_path))
            toc = doc.get_toc()
            
            if toc:
                nodes = self._build_from_toc(doc, toc, file_path.stem)
                return RawDocument(path=str(file_path), toc_available=True, nodes=nodes)
            else:
                nodes = self._build_from_font_heuristic(doc, file_path.stem)
                return RawDocument(path=str(file_path), toc_available=False, nodes=nodes)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process PDF {file_path}: {str(e)}") from e

    def _build_from_toc(self, doc: fitz.Document, toc: list, stem: str) -> list[DocumentNode]:
        nodes = []
        for idx, entry in enumerate(toc):
            level, title, page = entry
            next_page = toc[idx+1][2] if idx + 1 < len(toc) else len(doc) + 1
            
            raw_text = ""
            start_idx = max(0, page - 1)
            end_idx = min(len(doc), next_page - 1)
            if start_idx == end_idx:
                end_idx = start_idx + 1
                
            for p_idx in range(start_idx, end_idx):
                raw_text += doc[p_idx].get_text("text") + "\n"

            node = DocumentNode(
                id=f"{stem}_sec_{idx}",
                title=title,
                level=level,
                page_range=[page, max(page, next_page - 1)]
            )
            node.__dict__["raw_text"] = raw_text
            nodes.append(node)
        return nodes

    def _build_from_font_heuristic(self, doc: fitz.Document, stem: str) -> list[DocumentNode]:
        spans = []
        for page in doc:
            blocks = page.get_text("dict").get("blocks", [])
            for b in blocks:
                if b.get("type") == 0:
                    for l in b.get("lines", []):
                        for s in l.get("spans", []):
                            text = s.get("text", "").strip()
                            if text:
                                spans.append({"size": s["size"], "text": text, "page": page.number + 1})
        if not spans:
            return []
            
        sizes = [s["size"] for s in spans]
        median_size = statistics.median(sizes)
        
        nodes = []
        idx = 0
        current_node = None
        current_text = ""
        
        for span in spans:
            if span["size"] > median_size + 1.0:
                if current_node:
                    current_node.__dict__["raw_text"] = current_text
                    nodes.append(current_node)
                
                level = 1 if span["size"] > median_size + 4.0 else 2
                current_node = DocumentNode(
                    id=f"{stem}_sec_{idx}",
                    title=span["text"][:50],
                    level=level,
                    page_range=[span["page"], span["page"]]
                )
                current_text = span["text"] + "\n"
                idx += 1
            else:
                if current_node:
                    current_text += span["text"] + "\n"
                    current_node.page_range[1] = max(current_node.page_range[1], span["page"])
                else:
                    current_node = DocumentNode(
                        id=f"{stem}_sec_{idx}",
                        title="Introduction",
                        level=1,
                        page_range=[span["page"], span["page"]]
                    )
                    current_text = span["text"] + "\n"
                    idx += 1
                    
        if current_node:
            current_node.__dict__["raw_text"] = current_text
            nodes.append(current_node)
            
        return nodes
