from __future__ import annotations

import asyncio
import os
from typing import Any, Tuple

from ..errors import ProviderOperationError
from ..http import TOTAL_TIMEOUT
from ..rate_limit import rate_limit


def setup_client(model_name: str, config: dict[str, Any]) -> Any:
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file.")
    return Anthropic(api_key=api_key)


async def async_setup_client(model_name: str, config: dict[str, Any]) -> Any:
    return await asyncio.to_thread(setup_client, model_name, config)


def text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        rate_limit("anthropic", api_key, model_name)
        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            timeout=TOTAL_TIMEOUT,
        )
        return response.content[0].text
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("anthropic", model_name, "completion", str(e))


async def async_text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    return await asyncio.to_thread(
        text_completion, client, prompt, model_name, temperature
    )


def vision_completion(
    client: Any, prompt: str, image_path_or_url: str, model_name: str
) -> str:
    """Process vision inputs with Anthropic Claude models.
    
    Claude models support vision through multimodal messages.
    """
    import base64
    import requests
    import mimetypes
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        rate_limit("anthropic", api_key, model_name)
        
        # Load image data
        image_data = None
        mime_type = "image/png"
        
        if image_path_or_url.startswith(('http://', 'https://')):
            # Download from URL
            import urllib3
            # Disable SSL warnings when verify=False is used
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(image_path_or_url, timeout=30, verify=False)
            response.raise_for_status()
            image_data = response.content
            # Try to detect mime type from headers
            content_type = response.headers.get('content-type', '')
            if 'image/' in content_type:
                mime_type = content_type.split(';')[0]
        else:
            # Read from local file
            with open(image_path_or_url, 'rb') as f:
                image_data = f.read()
            # Detect mime type from extension
            detected_type = mimetypes.guess_type(image_path_or_url)[0]
            if detected_type and detected_type.startswith('image/'):
                mime_type = detected_type
        
        if not image_data:
            raise ProviderOperationError(
                "anthropic",
                model_name,
                "vision_completion",
                f"Could not load image from {image_path_or_url}"
            )
        
        # Encode image as base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Build the message with image
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
        
        # Make the API call
        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            messages=messages,
            timeout=TOTAL_TIMEOUT,
        )
        
        # Extract text from response
        return response.content[0].text
        
    except ProviderOperationError:
        raise
    except Exception as e:
        raise ProviderOperationError(
            "anthropic", model_name, "vision_completion", str(e)
        )


async def async_vision_completion(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    return await asyncio.to_thread(vision_completion, *args, **kwargs)


def image_generation(*args: Any, **kwargs: Any) -> Tuple[str, str]:  # pragma: no cover
    raise ProviderOperationError(
        "anthropic", kwargs.get("model_name", ""), "image generation", "Not implemented"
    )


async def async_image_generation(
    *args: Any, **kwargs: Any
) -> Tuple[str, str]:  # pragma: no cover
    return await asyncio.to_thread(image_generation, *args, **kwargs)


def image_edit(*args: Any, **kwargs: Any) -> Tuple[str, str]:  # pragma: no cover
    raise ProviderOperationError(
        "anthropic", kwargs.get("model_name", ""), "image edit", "Not implemented"
    )


async def async_image_edit(
    *args: Any, **kwargs: Any
) -> Tuple[str, str]:  # pragma: no cover
    return await asyncio.to_thread(image_edit, *args, **kwargs)


def transcribe_audio(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    raise ProviderOperationError(
        "anthropic",
        kwargs.get("model_name", ""),
        "audio transcription",
        "Not implemented",
    )


async def async_transcribe_audio(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    return await asyncio.to_thread(transcribe_audio, *args, **kwargs)
