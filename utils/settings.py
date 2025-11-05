import os
from typing import Any

from .logging import get_logger

logger = get_logger()

# Optional dependencies: dotenv and IPython display utilities
try:
    from dotenv import load_dotenv
    from IPython.display import Image as IPyImage
    from IPython.display import Markdown, display
    from plantuml import PlantUML
except ImportError:  # pragma: no cover - graceful fallback when deps missing
    logger.warning(
        "Optional core dependencies not found. Some features will be degraded."
    )
    logger.warning(
        "To enable full functionality run: pip install python-dotenv ipython plantuml"
    )

    def load_dotenv(*args: Any, **kwargs: Any) -> None:
        logger.warning("python-dotenv not installed; .env will not be loaded.")

    def display(*args: Any, **kwargs: Any) -> None:
        return None

    def Markdown(text: str) -> str:
        return text

    class _IPyImage:
        """Minimal placeholder used in notebooks."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    IPyImage = _IPyImage  # type: ignore[assignment]

    class _PlantUML:  # pragma: no cover - diagnostic only
        def __init__(self, url: str | None = None) -> None:
            logger.warning("plantuml not installed; rendering disabled.")

        def processes(self, *args: Any, **kwargs: Any) -> None:
            logger.warning("PlantUML rendering skipped (plantuml not installed).")

    PlantUML = _PlantUML  # type: ignore[assignment]


def load_environment() -> None:
    """Load environment variables from the nearest .env file.

    The search walks up from the current working directory until a directory
    containing either a ``.env`` file or a ``.git`` folder is found.  This
    mirrors the behaviour that existed in the original ``utils.py``.
    """
    path = os.getcwd()
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, ".env")) or os.path.exists(
            os.path.join(path, ".git")
        ):
            project_root = path
            break
        path = os.path.dirname(path)
    else:
        project_root = os.getcwd()

    dotenv_path = os.path.join(project_root, ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    else:
        logger.warning(".env file not found. API keys may not be loaded.")


__all__ = [
    "load_environment",
    "load_dotenv",
    "display",
    "Markdown",
    "IPyImage",
    "PlantUML",
]
