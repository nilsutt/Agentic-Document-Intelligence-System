from typing import Any, Dict, List
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.domain.ports.i_llm_client import ILLMClient
from src.domain.exceptions import LLMClientError

class OllamaClient(ILLMClient):
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.chat_model = ChatOllama(model=model, base_url=base_url)
        self.model = model

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        try:
            lc_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=content))
            response = self.chat_model.invoke(lc_messages)
            return response.content or ""
        except Exception as e:
            raise LLMClientError(f"Ollama completion failed: {e}") from e

    def bind_tools(self, tools: List[Any]) -> Any:
        return self.chat_model.bind_tools(tools)
