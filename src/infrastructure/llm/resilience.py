from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type, before_sleep_log
import pybreaker
import logging
from openai import RateLimitError, APIConnectionError, APITimeoutError, InternalServerError, AuthenticationError, BadRequestError

RETRYABLE = (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError)

logger = logging.getLogger(__name__)

def with_retry(func):
    """Tenacity retry decorator — wrap callable directly."""
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential_jitter(initial=1, max=60),
        retry=retry_if_exception_type(RETRYABLE),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )(func)

# Circuit breaker for sustained failures
llm_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    exclude=[AuthenticationError, BadRequestError]
)
