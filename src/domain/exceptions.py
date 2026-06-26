class AgenticPlatformError(Exception):
    """Base exception for all banking agentic platform errors."""
    pass

class DocumentProcessingError(AgenticPlatformError):
    """Raised when document ingestion or chunking fails."""
    pass

class LLMClientError(AgenticPlatformError):
    """Raised when LLM completion API calls fail."""
    pass

class VectorStoreError(AgenticPlatformError):
    """Raised when vector store upsert or search operations fail."""
    pass

class PIIMaskingError(AgenticPlatformError):
    """Raised when PII masking/unmasking operations fail."""
    pass
