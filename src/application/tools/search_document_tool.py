from langchain_core.tools import tool
from typing import Annotated
from langgraph.prebuilt import InjectedState

@tool
def search_document(
    query: str,
    state: Annotated[dict, InjectedState],
    top_k: int = 5
) -> str:
    """Search indexed documents for relevant information. Use when the user asks about the document content."""
    retrieval_service = state["deps"]["retrieval_service"]
    return retrieval_service.search_and_format(query, top_k)
