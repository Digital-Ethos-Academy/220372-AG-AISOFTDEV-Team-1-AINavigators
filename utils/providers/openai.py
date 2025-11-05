from __future__ import annotations

import asyncio
import base64
import os
from typing import Any, Tuple

from ..errors import ProviderOperationError
from ..http import TOTAL_TIMEOUT, request
from ..rate_limit import rate_limit


def setup_client(model_name: str, config: dict[str, Any]) -> Any:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    return OpenAI(api_key=api_key)


async def async_setup_client(model_name: str, config: dict[str, Any]) -> Any:
    from openai import AsyncOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    return AsyncOpenAI(api_key=api_key)


def _supports_temperature(model_name: str) -> bool:
    """Return True if we should attempt to set temperature for the model."""
    # Reasoning models (o*) have never supported temperature overrides, so skip
    # them up front. Other families are probed optimistically and retried below
    # if the API rejects the value.
    return not model_name.lower().startswith("o")


def _temperature_unsupported(error: Exception) -> bool:
    """Detect "temperature" unsupported errors from the OpenAI client."""

    # Prefer structured attributes when available.
    for attr in ("error", "body"):
        payload = getattr(error, attr, None)
        if isinstance(payload, dict):
            details = payload.get("error") if attr == "body" else payload
            if isinstance(details, dict):
                if (
                    details.get("param") == "temperature"
                    and details.get("code") == "unsupported_value"
                ):
                    return True

    # Fall back to string matching to handle SDK variations.
    message = str(error).lower()
    if "temperature" not in message:
        return False
    keywords = (
        "unsupported value",
        "does not support",
        "only the default (1) value is supported",
    )
    return any(keyword in message for keyword in keywords)


def _call_with_temperature_retry(
    operation: Any, params: dict[str, Any]
) -> Any:
    try:
        return operation(**params)
    except Exception as error:
        if "temperature" in params and _temperature_unsupported(error):
            retry_params = dict(params)
            retry_params.pop("temperature", None)
            return operation(**retry_params)
        raise


async def _async_call_with_temperature_retry(
    operation: Any, params: dict[str, Any]
) -> Any:
    try:
        return await operation(**params)
    except Exception as error:
        if "temperature" in params and _temperature_unsupported(error):
            retry_params = dict(params)
            retry_params.pop("temperature", None)
            return await operation(**retry_params)
        raise


def text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    try:
        api_key = os.getenv("OPENAI_API_KEY", "")
        rate_limit("openai", api_key, model_name)
        try:
            chat_params: dict[str, Any] = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "timeout": TOTAL_TIMEOUT,
            }
            if _supports_temperature(model_name):
                chat_params["temperature"] = temperature
            response = _call_with_temperature_retry(
                client.chat.completions.create, chat_params
            )
            return response.choices[0].message.content
        except Exception as api_error:
            if "v1/responses" in str(api_error):
                resp_params: dict[str, Any] = {
                    "model": model_name,
                    "input": prompt,
                    "timeout": TOTAL_TIMEOUT,
                }
                if _supports_temperature(model_name):
                    resp_params["temperature"] = temperature
                response = _call_with_temperature_retry(
                    client.responses.create, resp_params
                )
                if hasattr(response, "text"):
                    return response.text
                return response.choices[0].text
            raise api_error
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("openai", model_name, "completion", str(e))


async def async_text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    try:
        api_key = os.getenv("OPENAI_API_KEY", "")
        rate_limit("openai", api_key, model_name)
        try:
            chat_params: dict[str, Any] = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "timeout": TOTAL_TIMEOUT,
            }
            if _supports_temperature(model_name):
                chat_params["temperature"] = temperature
            response = await _async_call_with_temperature_retry(
                client.chat.completions.create, chat_params
            )
            return response.choices[0].message.content
        except Exception as api_error:
            if "v1/responses" in str(api_error):
                resp_params: dict[str, Any] = {
                    "model": model_name,
                    "input": prompt,
                    "timeout": TOTAL_TIMEOUT,
                }
                if _supports_temperature(model_name):
                    resp_params["temperature"] = temperature
                response = await _async_call_with_temperature_retry(
                    client.responses.create, resp_params
                )
                if hasattr(response, "text"):
                    return response.text
                return response.choices[0].text
            raise api_error
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("openai", model_name, "completion", str(e))


def vision_completion(
    client: Any, prompt: str, image_path_or_url: str, model_name: str
) -> str:
    """Process vision inputs with OpenAI's multimodal models (GPT-4o, GPT-4 Vision, etc.).
    
    OpenAI vision models accept images as base64-encoded data URLs in the message content.
    """
    import mimetypes
    import requests
    
    try:
        api_key = os.getenv("OPENAI_API_KEY", "")
        rate_limit("openai", api_key, model_name)
        
        # Load image data
        image_data = None
        mime_type = "image/png"
        
        if image_path_or_url.startswith(('http://', 'https://')):
            # For URLs, OpenAI can handle them directly
            image_url = image_path_or_url
        else:
            # For local files, convert to base64 data URL
            with open(image_path_or_url, 'rb') as f:
                image_data = f.read()
            
            # Detect mime type
            detected_type = mimetypes.guess_type(image_path_or_url)[0]
            if detected_type and detected_type.startswith('image/'):
                mime_type = detected_type
            
            # Create base64 data URL
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:{mime_type};base64,{image_base64}"
        
        # Build the message with image
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }]
        
        # Make the API call
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=4096,
            timeout=TOTAL_TIMEOUT,
        )
        
        # Extract text from response
        return response.choices[0].message.content
        
    except Exception as e:
        raise ProviderOperationError(
            "openai", model_name, "vision_completion", str(e)
        )


async def async_vision_completion(
    client: Any, prompt: str, image_path_or_url: str, model_name: str
) -> str:
    """Async version of vision_completion for OpenAI models."""
    import mimetypes
    import aiofiles
    
    try:
        api_key = os.getenv("OPENAI_API_KEY", "")
        rate_limit("openai", api_key, model_name)
        
        # Load image data
        image_data = None
        mime_type = "image/png"
        
        if image_path_or_url.startswith(('http://', 'https://')):
            # For URLs, OpenAI can handle them directly
            image_url = image_path_or_url
        else:
            # For local files, convert to base64 data URL
            # Use sync file reading in thread for simplicity
            with open(image_path_or_url, 'rb') as f:
                image_data = f.read()
            
            # Detect mime type
            detected_type = mimetypes.guess_type(image_path_or_url)[0]
            if detected_type and detected_type.startswith('image/'):
                mime_type = detected_type
            
            # Create base64 data URL
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:{mime_type};base64,{image_base64}"
        
        # Build the message with image
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }]
        
        # Make the API call
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=4096,
            timeout=TOTAL_TIMEOUT,
        )
        
        # Extract text from response
        return response.choices[0].message.content
        
    except Exception as e:
        raise ProviderOperationError(
            "openai", model_name, "vision_completion", str(e)
        )


def image_generation(client: Any, prompt: str, model_name: str) -> Tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    params = {"model": model_name, "prompt": prompt, "n": 1, "size": "1024x1024"}
    if model_name != "gpt-image-1":
        params["response_format"] = "b64_json"
    response = client.images.generate(timeout=TOTAL_TIMEOUT, **params)
    if model_name == "gpt-image-1" and response.data[0].url:
        img_resp = request("GET", response.data[0].url)
        img_resp.raise_for_status()
        image_data_base64 = base64.b64encode(img_resp.content).decode("utf-8")
    else:
        image_data_base64 = response.data[0].b64_json
    return image_data_base64, "image/png"


async def async_image_generation(
    client: Any, prompt: str, model_name: str
) -> Tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    params = {"model": model_name, "prompt": prompt, "n": 1, "size": "1024x1024"}
    if model_name != "gpt-image-1":
        params["response_format"] = "b64_json"
    response = await client.images.generate(timeout=TOTAL_TIMEOUT, **params)
    if model_name == "gpt-image-1" and response.data[0].url:
        img_resp = await asyncio.to_thread(request, "GET", response.data[0].url)
        img_resp.raise_for_status()
        image_data_base64 = base64.b64encode(img_resp.content).decode("utf-8")
    else:
        image_data_base64 = response.data[0].b64_json
    return image_data_base64, "image/png"


def image_edit(
    client: Any, prompt: str, image_path: str, model_name: str, **edit_params: Any
) -> Tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    with open(image_path, "rb") as image_file:
        response = client.images.edit(
            model=model_name,
            image=image_file,
            prompt=prompt,
            timeout=TOTAL_TIMEOUT,
            **edit_params,
        )
    return response.data[0].b64_json, "image/png"


async def async_image_edit(
    client: Any, prompt: str, image_path: str, model_name: str, **edit_params: Any
) -> Tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    with open(image_path, "rb") as image_file:
        response = await client.images.edit(
            model=model_name,
            image=image_file,
            prompt=prompt,
            timeout=TOTAL_TIMEOUT,
            **edit_params,
        )
    return response.data[0].b64_json, "image/png"


def transcribe_audio(
    client: Any, audio_path: str, model_name: str, language_code: str = "en-US"
) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model_name,
            file=audio_file,
            timeout=TOTAL_TIMEOUT,
        )
    return transcription.text


async def async_transcribe_audio(
    client: Any, audio_path: str, model_name: str, language_code: str = "en-US"
) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    rate_limit("openai", api_key, model_name)
    with open(audio_path, "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            model=model_name,
            file=audio_file,
            timeout=TOTAL_TIMEOUT,
        )
    return transcription.text
