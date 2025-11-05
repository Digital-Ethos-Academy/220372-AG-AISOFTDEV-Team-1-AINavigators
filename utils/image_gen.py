from __future__ import annotations

import asyncio
import base64
import mimetypes
import time
from typing import Any, Optional, Tuple

from .artifacts import save_artifact
from .errors import ProviderOperationError
from .helpers import ensure_provider
from .logging import get_logger

logger = get_logger()


def _save_image(image_data_base64: str, image_mime: str) -> Tuple[str, str]:
    ext = mimetypes.guess_extension(image_mime) or ".png"
    filename = f"image_{int(time.time())}{ext}"
    file_path = save_artifact(
        base64.b64decode(image_data_base64), filename, subdir="screens"
    )
    image_url = f"data:{image_mime};base64,{image_data_base64}"
    return str(file_path), image_url


def get_image_generation_completion(
    prompt: str, client: Any, model_name: str, api_provider: str
) -> Tuple[str, str]:
    provider_module = ensure_provider(
        client, api_provider, model_name, "image generation"
    )
    image_data_base64, image_mime = provider_module.image_generation(
        client, prompt, model_name
    )
    return _save_image(image_data_base64, image_mime)


async def async_get_image_generation_completion(
    prompt: str, client: Any, model_name: str, api_provider: str
) -> Tuple[str, str]:
    provider_module = ensure_provider(
        client, api_provider, model_name, "image generation"
    )
    if hasattr(provider_module, "async_image_generation"):
        image_data_base64, image_mime = await provider_module.async_image_generation(
            client, prompt, model_name
        )
    else:
        image_data_base64, image_mime = await asyncio.to_thread(
            provider_module.image_generation, client, prompt, model_name
        )
    return _save_image(image_data_base64, image_mime)


def get_image_generation_completion_compat(
    prompt: str, client: Any, model_name: str, api_provider: str
) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    try:
        return (
            get_image_generation_completion(prompt, client, model_name, api_provider),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


async def async_get_image_generation_completion_compat(
    prompt: str, client: Any, model_name: str, api_provider: str
) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    try:
        return (
            await async_get_image_generation_completion(
                prompt, client, model_name, api_provider
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


def get_image_edit_completion(
    prompt: str,
    image_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    **edit_params: Any,
) -> Tuple[str, str]:
    provider_module = ensure_provider(client, api_provider, model_name, "image edit")
    image_data_base64, image_mime = provider_module.image_edit(
        client, prompt, image_path, model_name, **edit_params
    )
    return _save_image(image_data_base64, image_mime)


async def async_get_image_edit_completion(
    prompt: str,
    image_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    **edit_params: Any,
) -> Tuple[str, str]:
    provider_module = ensure_provider(client, api_provider, model_name, "image edit")
    if hasattr(provider_module, "async_image_edit"):
        image_data_base64, image_mime = await provider_module.async_image_edit(
            client, prompt, image_path, model_name, **edit_params
        )
    else:
        image_data_base64, image_mime = await asyncio.to_thread(
            provider_module.image_edit,
            client,
            prompt,
            image_path,
            model_name,
            **edit_params,
        )
    return _save_image(image_data_base64, image_mime)


def get_image_edit_completion_compat(
    prompt: str,
    image_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    **edit_params: Any,
) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    try:
        return (
            get_image_edit_completion(
                prompt, image_path, client, model_name, api_provider, **edit_params
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


async def async_get_image_edit_completion_compat(
    prompt: str,
    image_path: str,
    client: Any,
    model_name: str,
    api_provider: str,
    **edit_params: Any,
) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    try:
        return (
            await async_get_image_edit_completion(
                prompt, image_path, client, model_name, api_provider, **edit_params
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


__all__ = [
    "get_image_generation_completion",
    "get_image_generation_completion_compat",
    "async_get_image_generation_completion",
    "async_get_image_generation_completion_compat",
    "get_image_edit_completion",
    "get_image_edit_completion_compat",
    "async_get_image_edit_completion",
    "async_get_image_edit_completion_compat",
]
