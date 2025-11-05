from __future__ import annotations

import asyncio
import os
from typing import Any, Optional, Tuple

from .errors import ProviderOperationError
from .helpers import ensure_provider
from .models import RECOMMENDED_MODELS


def transcribe_audio(
    audio_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    language_code: str = "en-US",
) -> str:
    provider_module = ensure_provider(
        client, api_provider, model_name, "audio transcription"
    )
    if not RECOMMENDED_MODELS.get(model_name, {}).get("audio_transcription"):
        raise ProviderOperationError(
            api_provider,
            model_name,
            "audio transcription",
            f"Model '{model_name}' does not support audio transcription.",
        )
    if not os.path.exists(audio_path):
        raise ProviderOperationError(
            api_provider,
            model_name,
            "audio transcription",
            f"Audio file not found at {audio_path}",
        )
    return provider_module.transcribe_audio(
        client, audio_path, model_name, language_code
    )


async def async_transcribe_audio(
    audio_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    language_code: str = "en-US",
) -> str:
    provider_module = ensure_provider(
        client, api_provider, model_name, "audio transcription"
    )
    if not RECOMMENDED_MODELS.get(model_name, {}).get("audio_transcription"):
        raise ProviderOperationError(
            api_provider,
            model_name,
            "audio transcription",
            f"Model '{model_name}' does not support audio transcription.",
        )
    if not os.path.exists(audio_path):
        raise ProviderOperationError(
            api_provider,
            model_name,
            "audio transcription",
            f"Audio file not found at {audio_path}",
        )
    if hasattr(provider_module, "async_transcribe_audio"):
        return await provider_module.async_transcribe_audio(
            client, audio_path, model_name, language_code
        )
    return await asyncio.to_thread(
        provider_module.transcribe_audio, client, audio_path, model_name, language_code
    )


def transcribe_audio_compat(
    audio_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    language_code: str = "en-US",
) -> Tuple[Optional[str], Optional[str]]:
    try:
        return (
            transcribe_audio(
                audio_path, client, model_name, api_provider, language_code
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


async def async_transcribe_audio_compat(
    audio_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    language_code: str = "en-US",
) -> Tuple[Optional[str], Optional[str]]:
    try:
        return (
            await async_transcribe_audio(
                audio_path, client, model_name, api_provider, language_code
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


__all__ = [
    "transcribe_audio",
    "transcribe_audio_compat",
    "async_transcribe_audio",
    "async_transcribe_audio_compat",
]
