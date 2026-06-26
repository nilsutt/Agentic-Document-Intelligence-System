from typing import Protocol

class IPIIMasker(Protocol):
    def mask(self, text: str) -> str:
        """Masks PII in the given text."""
        ...
        
    def unmask(self, masked_text: str) -> str:
        """Reverts masking for a given masked text."""
        ...
