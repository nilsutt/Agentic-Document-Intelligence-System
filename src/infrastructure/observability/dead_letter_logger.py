import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

class DeadLetterLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "dead_letter.jsonl"
        
    def log_failed_document(self, file_path: str, error: Exception, context: Optional[dict] = None) -> None:
        """Logs documents that failed to process."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": file_path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as write_err:
            import logging
            logging.getLogger(__name__).error(f"Failed to write to dead letter queue: {write_err}")
