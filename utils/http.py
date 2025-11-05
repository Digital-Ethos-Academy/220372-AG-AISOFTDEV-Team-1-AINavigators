"""HTTP helpers with connection pooling, retries, and timeouts."""
from __future__ import annotations

import os
import random
from typing import Any

from .logging import get_logger

logger = get_logger()

try:  # pragma: no cover - exercised indirectly in environments without requests
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover - dependency optional in minimal setups
    requests = None  # type: ignore[assignment]
    HTTPAdapter = None  # type: ignore[assignment]
    Retry = None  # type: ignore[assignment]
    _REQUESTS_AVAILABLE = False
    logger.warning(
        "'requests' package not installed; HTTP helpers are disabled.",
        extra={"provider": None, "model": None, "latency_ms": None, "artifacts_path": None},
    )

CONNECT_TIMEOUT = float(os.getenv("UTILS_TIMEOUT_CONNECT", "10"))
READ_TIMEOUT = float(os.getenv("UTILS_TIMEOUT_READ", "60"))
DEFAULT_TIMEOUT: tuple[float, float] = (CONNECT_TIMEOUT, READ_TIMEOUT)
TOTAL_TIMEOUT: float = sum(DEFAULT_TIMEOUT)
MAX_RETRIES = int(os.getenv("UTILS_MAX_RETRIES", "3"))


if _REQUESTS_AVAILABLE:

    class _JitterRetry(Retry):
        """Retry class with jittered exponential backoff."""

        def get_backoff_time(self) -> float:  # pragma: no cover - deterministic
            backoff = super().get_backoff_time()
            if backoff <= 0:
                return 0
            return random.uniform(0, backoff)


    def _create_session() -> requests.Session:
        session = requests.Session()
        retry = _JitterRetry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=None,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


    _SESSION = _create_session()


    def get_session() -> requests.Session:
        """Return a module-level ``requests`` session."""

        return _SESSION


    def request(method: str, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper around ``Session.request`` applying default timeout."""

        if "timeout" not in kwargs:
            kwargs["timeout"] = DEFAULT_TIMEOUT
        return _SESSION.request(method, url, **kwargs)


else:

    def _missing_requests(*_: Any, **__: Any) -> None:
        raise RuntimeError(
            "The 'requests' dependency is required for HTTP helpers. "
            "Install it via 'pip install requests'."
        )


    def get_session() -> Any:
        """Raise an informative error when requests is unavailable."""

        _missing_requests()


    def request(method: str, url: str, **kwargs: Any) -> Any:
        """Raise an informative error when requests is unavailable."""

        _missing_requests(method, url, **kwargs)


__all__ = [
    "DEFAULT_TIMEOUT",
    "TOTAL_TIMEOUT",
    "get_session",
    "request",
]
