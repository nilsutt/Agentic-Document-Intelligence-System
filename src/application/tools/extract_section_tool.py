from langchain_core.tools import tool
from typing import Annotated
from langgraph.prebuilt import InjectedState
from src.domain.models.query import QueryRequest

@tool
def extract_section(section_title: str, state: Annotated[dict, InjectedState]) -> str:
    """Extract all content from a specific named section. Use when you need the full text of a particular heading."""
    retrieval_service = state["deps"]["retrieval_service"]
    raw_contexts = retrieval_service.search(
        QueryRequest(question=f'"{section_title}" section content', top_k=10)
    ).contexts

    # Prioritize exact section_title matches
    exact = [c for c in raw_contexts if section_title.lower() in c.section_title.lower()]
    fallback = [c for c in raw_contexts if c not in exact]
    ordered = exact + fallback

    if not ordered:
        return f"Section '{section_title}' not found in indexed documents."
    return "\n\n".join(f"[Page {c.page}]\n{c.text}" for c in ordered)
