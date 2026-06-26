from langchain_core.language_models.chat_models import BaseChatModel
from src.domain.ports.i_llm_client import ILLMClient

class LLMFactory:
    def __init__(self, provider: str, ollama_model: str, ollama_base_url: str,
                 openai_api_key: str, openai_model: str):
        self.provider = provider.lower()
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

    def create_client(self) -> ILLMClient:
        if self.provider == "openai":
            from src.infrastructure.llm.openai_client import OpenAIClient
            return OpenAIClient(api_key=self.openai_api_key, model=self.openai_model)
        # Default: ollama
        from src.infrastructure.llm.ollama_client import OllamaClient
        return OllamaClient(model=self.ollama_model, base_url=self.ollama_base_url)

    def create_chat_model(self) -> BaseChatModel:
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=self.openai_model, api_key=self.openai_api_key)
        # Default: ollama
        from langchain_ollama import ChatOllama
        return ChatOllama(model=self.ollama_model, base_url=self.ollama_base_url)
