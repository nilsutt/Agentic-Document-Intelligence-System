from typing import Protocol, Any, Dict, List

class ILLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Generates a completion from the LLM based on input messages."""
        ...
        
    def bind_tools(self, tools: List[Any]) -> Any:
        """Binds tools to the LLM client (used in agentic workflows)."""
        ...
