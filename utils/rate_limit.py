"""Simple token bucket rate limiter keyed by provider, API key, and model."""
from __future__ import annotations

import logging
import os
import threading
import time

logger = logging.getLogger(__name__)


class _TokenBucket:
    def __init__(self, rate: float):
        self.rate = rate
        self.capacity = max(rate, 1.0)
        self.tokens = self.capacity
        self.timestamp = time.monotonic()
        self.lock = threading.Lock()

    def consume(self, amount: float = 1.0) -> float:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.timestamp
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.timestamp = now
            if self.tokens >= amount:
                self.tokens -= amount
                return 0.0
            needed = amount - self.tokens
            self.tokens = 0.0
            return needed / self.rate


_BUCKETS: dict[str, _TokenBucket] = {}


def _get_rate(provider: str) -> float | None:
    env = f"UTILS_RATE_LIMIT_QPS_{provider.upper()}"
    value = os.getenv(env)
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def rate_limit(provider: str, api_key: str, model_name: str) -> None:
    """Enforce token-bucket rate limiting for a provider/model/API key."""

    rate = _get_rate(provider)
    if not rate:
        return
    key = f"{provider}:{api_key}:{model_name}"
    bucket = _BUCKETS.get(key)
    if not bucket:
        bucket = _TokenBucket(rate)
        _BUCKETS[key] = bucket
    wait = bucket.consume()
    if wait > 0:
        logger.warning(
            "Rate limit exceeded for %s %s, sleeping %.2fs", provider, model_name, wait
        )
        time.sleep(wait)


__all__ = ["rate_limit"]
