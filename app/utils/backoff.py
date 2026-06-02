import logging
from tenacity import retry, wait_exponential, stop_after_attempt, before_sleep_log

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

retry_with_backoff = retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(4),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
