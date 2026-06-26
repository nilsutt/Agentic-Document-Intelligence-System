from typing import Any, Dict, List
import openai
from src.domain.ports.i_llm_client import ILLMClient
from src.domain.exceptions import LLMClientError
from src.infrastructure.llm.resilience import with_retry, llm_circuit_breaker
import pybreaker

class OpenAIClient(ILLMClient):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        @with_retry
        def _call():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content or ""
            
        try:
            return llm_circuit_breaker.call(_call)
        except pybreaker.CircuitBreakerError as e:
            raise LLMClientError("Circuit breaker open: LLM service is temporarily unavailable.") from e
        except Exception as e:
            raise LLMClientError(f"Failed to generate LLM completion: {str(e)}") from e

    def bind_tools(self, tools: List[Any]) -> Any:
        return tools
