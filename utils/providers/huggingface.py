from __future__ import annotations

import asyncio
import base64
import os
from io import BytesIO
from typing import Any, Tuple

from ..errors import ProviderOperationError
from ..http import TOTAL_TIMEOUT
from ..rate_limit import rate_limit


def setup_client(model_name: str, config: dict[str, Any]) -> Any:
    from huggingface_hub import InferenceClient

    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY not found in .env file.")
    return InferenceClient(model=model_name, token=api_key)


async def async_setup_client(model_name: str, config: dict[str, Any]) -> Any:
    return await asyncio.to_thread(setup_client, model_name, config)


def text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        rate_limit("huggingface", api_key, model_name)
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=max(0.1, temperature),
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("huggingface", model_name, "completion", str(e))


async def async_text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    return await asyncio.to_thread(
        text_completion, client, prompt, model_name, temperature
    )


def vision_completion(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    raise ProviderOperationError(
        "huggingface", kwargs.get("model_name", ""), "vision", "Not implemented"
    )


async def async_vision_completion(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    return await asyncio.to_thread(vision_completion, *args, **kwargs)


def image_generation(client: Any, prompt: str, model_name: str) -> Tuple[str, str]:
    api_key = os.getenv("HUGGINGFACE_API_KEY", "")
    rate_limit("huggingface", api_key, model_name)
    # Some versions of huggingface_hub do not support a per-call `timeout` kwarg.
    # Prefer using it when available, but gracefully fall back if not.
    try:
        pil_image = client.text_to_image(prompt, timeout=TOTAL_TIMEOUT)
    except TypeError:
        pil_image = client.text_to_image(prompt)
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8"), "image/png"


async def async_image_generation(
    client: Any, prompt: str, model_name: str
) -> Tuple[str, str]:
    return await asyncio.to_thread(image_generation, client, prompt, model_name)


def image_edit(*args: Any, **kwargs: Any) -> Tuple[str, str]:  # pragma: no cover
    try:
        client = args[0] if args else kwargs.get("client")
        prompt = args[1] if len(args) > 1 else kwargs.get("prompt", "")
        image_path = args[2] if len(args) > 2 else kwargs.get("image_path")
        model_name = args[3] if len(args) > 3 else kwargs.get("model_name", "")
        # Remaining kwargs are edit params (guidance_scale, strength, num_inference_steps, seed, etc.)
        edit_params = dict(kwargs)
        for k in ("client", "prompt", "image_path", "model_name"):
            edit_params.pop(k, None)

        api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        rate_limit("huggingface", api_key, model_name)

        # Load image as PIL if possible; otherwise pass raw bytes (InferenceClient accepts both)
        src_image: Any
        try:
            from PIL import Image  # type: ignore

            with open(image_path, "rb") as f:
                src_image = Image.open(f)
                # Ensure the image is loaded before file closes
                src_image.load()
        except Exception:
            with open(image_path, "rb") as f:
                src_image = f.read()

        # Some versions support timeout kwarg; fall back if not
        try:
            pil_image = client.image_to_image(
                prompt=prompt, image=src_image, timeout=TOTAL_TIMEOUT, **edit_params
            )
        except TypeError:
            pil_image = client.image_to_image(prompt=prompt, image=src_image, **edit_params)

        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8"), "image/png"
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("huggingface", kwargs.get("model_name", ""), "image edit", str(e))


async def async_image_edit(
    *args: Any, **kwargs: Any
) -> Tuple[str, str]:  # pragma: no cover
    return await asyncio.to_thread(image_edit, *args, **kwargs)


def transcribe_audio(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    raise ProviderOperationError(
        "huggingface",
        kwargs.get("model_name", ""),
        "audio transcription",
        "Not implemented",
    )


async def async_transcribe_audio(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    return await asyncio.to_thread(transcribe_audio, *args, **kwargs)
