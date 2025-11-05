"""PlantUML diagram helpers."""
from __future__ import annotations

import os
import ssl
import sys
from pathlib import Path
from typing import Optional, Union

from .artifacts import resolve_artifact_path
from .errors import ArtifactError
from .logging import get_logger
from .settings import PlantUML

logger = get_logger()
# Use HTTP by default to avoid SSL certificate issues in corporate environments
DEFAULT_PLANTUML_SERVER = os.getenv(
    "PLANTUML_SERVER_URL", "http://www.plantuml.com/plantuml/img/"
)


def _disable_ssl_verification():
    """Disable SSL certificate verification for corporate environments."""
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        pass
    
    # Create an unverified SSL context
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass


def _instantiate_plantuml(server_url: Optional[str]) -> PlantUML:
    """Return a PlantUML client, tolerating placeholder implementations."""

    utils_module = sys.modules.get(__package__)
    plantuml_cls = getattr(utils_module, "PlantUML", PlantUML) if utils_module else PlantUML

    url = server_url or DEFAULT_PLANTUML_SERVER
    
    # If using HTTPS, disable SSL verification for corporate environments
    if url and url.startswith("https://"):
        logger.info("Using HTTPS PlantUML server - disabling SSL verification for corporate environment")
        _disable_ssl_verification()
    
    try:
        return plantuml_cls(url=url) if url else plantuml_cls()
    except TypeError:
        # Some fallback shims may not accept named parameters; retry without.
        return plantuml_cls()


def render_plantuml_diagram(
    diagram_source: str,
    output_filename: Union[str, Path],
    *,
    server_url: Optional[str] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """Render PlantUML text into an artifact image."""

    if not isinstance(diagram_source, str) or not diagram_source.strip():
        raise ArtifactError("diagram_source must be a non-empty string.")

    destination = resolve_artifact_path(
        output_filename, base_dir=base_dir, must_exist=False
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    client = _instantiate_plantuml(server_url)

    attempts = []
    result = None

    try:
        result = client.processes(diagram_source, outfile=str(destination))
    except TypeError as exc:  # Older plantuml libraries reject the keyword.
        attempts.append(("outfile", exc))
    except Exception as exc:  # pragma: no cover - pass through diagnostics
        raise ArtifactError(f"PlantUML rendering failed: {exc}") from exc

    if result is None:
        try:
            result = client.processes(diagram_source, str(destination))
        except TypeError as exc:
            attempts.append(("outfile positional", exc))
        except Exception as exc:  # pragma: no cover - pass through diagnostics
            raise ArtifactError(f"PlantUML rendering failed: {exc}") from exc

    if result is None:
        try:
            result = client.processes(diagram_source)
        except Exception as exc:  # pragma: no cover - pass through diagnostics
            if attempts:
                detail = "; ".join(f"{label}: {err}" for label, err in attempts)
                message = f"PlantUML rendering failed after attempts [{detail}]: {exc}"
            else:
                message = f"PlantUML rendering failed: {exc}"
            raise ArtifactError(message) from exc

    if isinstance(result, (bytes, bytearray)):
        destination.write_bytes(result)
    elif hasattr(result, "read") and callable(getattr(result, "read")):
        destination.write_bytes(result.read())
    else:
        if not destination.exists():
            raise ArtifactError(
                "PlantUML client did not produce output; verify dependencies."
            )

    logger.info(
        "PlantUML diagram rendered.",
        extra={"artifacts_path": str(destination)},
    )

    return destination


__all__ = ["render_plantuml_diagram"]
