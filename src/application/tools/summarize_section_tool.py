from langchain_core.tools import tool
from typing import Annotated
from langgraph.prebuilt import InjectedState

@tool
def summarize_section(text: str, state: Annotated[dict, InjectedState]) -> str:
    """Summarize a long document section. Use when retrieved text is too long."""
    llm_client = state["deps"]["llm_client"]
    messages = [
        {"role": "system", "content": "You are a banking document analyst. Summarize concisely."},
        {"role": "user", "content": f"Summarize this section:\n\n{text[:4000]}"}
    ]
    return llm_client.complete(messages)
