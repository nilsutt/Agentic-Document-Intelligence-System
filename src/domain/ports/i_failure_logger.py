from typing import Protocol, Optional

class IFailureLogger(Protocol):
    def log_failed_document(self, file_path: str, error: Exception, context: Optional[dict] = None) -> None:
        """Logs documents that failed to process."""
        ...
