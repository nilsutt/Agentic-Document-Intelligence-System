from src.domain.ports.i_embedding_service import IEmbeddingService

class EmbeddingFactory:
    def __init__(self, provider: str, ollama_model: str, ollama_base_url: str,
                 openai_api_key: str, openai_model: str):
        self.provider = provider.lower()
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

    def create(self) -> IEmbeddingService:
        if self.provider == "openai":
            from src.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService
            return OpenAIEmbeddingService(api_key=self.openai_api_key, model=self.openai_model)
        # Default: ollama
        from src.infrastructure.embeddings.ollama_embeddings import OllamaEmbeddingService
        return OllamaEmbeddingService(model=self.ollama_model, base_url=self.ollama_base_url)
