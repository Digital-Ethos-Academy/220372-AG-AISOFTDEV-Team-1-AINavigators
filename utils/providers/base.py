"""Protocol defining the provider interface."""
from __future__ import annotations

from typing import Any, Protocol


class Provider(Protocol):  # pragma: no cover - structural typing only
    """Minimal protocol all provider implementations follow."""

    def setup_client(self, model_name: str, config: dict[str, Any]) -> Any:
        ...

    def text_completion(
        self, client: Any, prompt: str, model_name: str, temperature: float = 0.7
    ) -> str:
        ...

    def vision_completion(
        self, client: Any, prompt: str, image_path_or_url: str, model_name: str
    ) -> str:
        ...

    def image_generation(
        self, client: Any, prompt: str, model_name: str
    ) -> tuple[str, str]:
        ...

    def image_edit(
        self,
        client: Any,
        prompt: str,
        image_path: str,
        model_name: str,
        **edit_params: Any,
    ) -> tuple[str, str]:
        ...

    def transcribe_audio(
        self,
        client: Any,
        audio_path: str,
        model_name: str,
        language_code: str = "en-US",
    ) -> str:
        ...
