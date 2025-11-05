import logging
import os


class _ContextFilter(logging.Filter):
    """Ensure log records always have provider, model, latency_ms, artifacts_path."""

    def filter(self, record: logging.LogRecord) -> bool:
        for attr in ("provider", "model", "latency_ms", "artifacts_path"):
            if not hasattr(record, attr):
                setattr(record, attr, None)
        return True


def get_logger() -> logging.Logger:
    """Configure and return a logger for ag_aisoftdev utils."""
    log_level = os.getenv("UTILS_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger("ag_aisoftdev.utils")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s "
            "provider=%(provider)s model=%(model)s latency_ms=%(latency_ms)s "
            "artifacts_path=%(artifacts_path)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.addFilter(_ContextFilter())

        # Set a safe default formatter for the root logger to avoid KeyError for third-party logs
        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            h.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        root_logger.setLevel(level)
    return logger
