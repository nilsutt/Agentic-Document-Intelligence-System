from unittest.mock import Mock
import pytest
from openai import RateLimitError
from src.infrastructure.llm.resilience import with_retry, llm_circuit_breaker

def test_with_retry_retries_on_rate_limit():
    call_count = 0
    # Simulate 2 failures then success
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitError("rate limit", response=Mock(status_code=429), body={})
        return "ok"
    
    result = with_retry(flaky)()
    assert result == "ok"
    assert call_count == 3

def test_circuit_breaker_initialized():
    assert llm_circuit_breaker is not None
    assert llm_circuit_breaker.fail_max == 5
    assert llm_circuit_breaker.reset_timeout == 60
