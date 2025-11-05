"""Google AI (Gemini) Provider Implementation.

This module implements support for Google's Gemini models through the new
google.genai client API. It handles text generation, vision (multimodal),
and image generation tasks.

API Documentation: https://ai.google.dev/gemini-api/docs

Key Changes (2025):
- Uses google.genai.Client instead of google.generativeai.GenerativeModel
- All content generation goes through client.models.generate_content()
- Supports response_modalities for controlling output types
"""
from __future__ import annotations

import asyncio
import base64
import os
import random
import time
from typing import Any, Tuple

from ..errors import ProviderOperationError
from ..http import TOTAL_TIMEOUT
from ..rate_limit import rate_limit


def _is_image_model(model_name: str) -> bool:
    """Return ``True`` if ``model_name`` uses Google's image generation stack."""
    lowered = model_name.lower()
    return "imagen" in lowered or "image" in lowered


def _extract_generated_image(response: Any, model_name: str) -> Tuple[str, str]:
    """Normalize Google image responses to ``(base64, mime_type)``."""
    generated = getattr(response, "generated_images", None) or []
    if not generated:
        raise ProviderOperationError(
            "google", model_name, "image generation", "No image data returned by API"
        )

    for candidate in generated:
        image_obj = getattr(candidate, "image", None)
        if not image_obj:
            continue
        mime_type = getattr(image_obj, "mime_type", None) or "image/png"
        image_bytes = getattr(image_obj, "image_bytes", None)
        if isinstance(image_bytes, bytes) and image_bytes:
            return base64.b64encode(image_bytes).decode("utf-8"), mime_type
        inline_b64 = getattr(image_obj, "bytes_base64", None)
        if isinstance(inline_b64, str) and inline_b64:
            return inline_b64, mime_type

    raise ProviderOperationError(
        "google",
        model_name,
        "image generation",
        "Google response did not include image bytes",
    )


_GENAI_IMPORTS: tuple[Any, Any] | None = None


def _get_google_genai_imports() -> tuple[Any, Any]:
    """Lazily import google.genai helpers so tests can stub behavior."""
    global _GENAI_IMPORTS
    if _GENAI_IMPORTS is None:
        try:
            from google.genai import errors as genai_errors  # type: ignore
            from google.genai import types as genai_types  # type: ignore
        except ImportError:  # pragma: no cover - optional dependency
            _GENAI_IMPORTS = (None, None)
        else:
            _GENAI_IMPORTS = (genai_errors, genai_types)
    return _GENAI_IMPORTS


def _should_retry_with_v1(error: Exception) -> bool:
    genai_errors, _ = _get_google_genai_imports()
    if not genai_errors or not isinstance(error, genai_errors.ClientError):
        return False
    if getattr(error, "code", None) == 404:
        return True
    message = (getattr(error, "message", "") or str(error) or "").lower()
    return "api version" in message or "predict" in message


def _is_client_not_found(error: Exception) -> bool:
    genai_errors, _ = _get_google_genai_imports()
    return bool(
        genai_errors
        and isinstance(error, genai_errors.ClientError)
        and getattr(error, "code", None) == 404
    )


def image_generation(
    client: Any, prompt: str, model_name: str
) -> tuple[str, str]:
    """
    Generate an image using a Google image generation model.

    Args:
        client: The google.genai.Client object.
        prompt (str): The text prompt for image generation.
        model_name (str): The name of the image generation model.

    Returns:
        A tuple containing the base64-encoded image data and its MIME type.
    """
    _, genai_types = _get_google_genai_imports()
    if not genai_types:
        raise ProviderOperationError(
            "google",
            model_name,
            "image_generation",
            "google.genai is not installed",
        )

    try:
        # Generate the image content
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        # Extract the image data from the response
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        # Check for inline_data with image content
                        blob = getattr(part, "inline_data", None)
                        if blob:
                            data = getattr(blob, "data", None)
                            mime_type = getattr(blob, "mime_type", "image/png")
                            if data:
                                # Return base64-encoded string
                                if isinstance(data, bytes):
                                    return base64.b64encode(data).decode("utf-8"), mime_type
                                elif isinstance(data, str):
                                    # Already base64 encoded
                                    return data, mime_type

        raise ProviderOperationError(
            "google", model_name, "image_generation", "No image data found in response"
        )

    except ProviderOperationError:
        raise
    except Exception as e:
        # Wrap exceptions in ProviderOperationError for consistent error handling
        raise ProviderOperationError(
            "google", model_name, "image_generation", f"API call failed: {e}"
        )


def setup_client(model_name: str, config: dict[str, Any]) -> Any:
    """Set up the appropriate Google client based on the model's task.
    
    Returns a genai.Client for text/vision/image generation tasks,
    or a SpeechClient for audio transcription.
    """
    if config.get("audio_transcription"):
        from google.cloud import speech

        return speech.SpeechClient()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")

    from google import genai

    # Return a Client instance for all text/vision/image models
    # The client.models.generate_content API will be used for all content generation
    return genai.Client(api_key=api_key)


async def async_setup_client(model_name: str, config: dict[str, Any]) -> Any:
    return await asyncio.to_thread(setup_client, model_name, config)


def text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    try:
        api_key = os.getenv("GOOGLE_API_KEY", "")
        rate_limit("google", api_key, model_name)
        
        _, genai_types = _get_google_genai_imports()
        if not genai_types:
            raise ProviderOperationError(
                "google",
                model_name,
                "text_completion",
                "google.genai is not installed",
            )
        
        # Use the client.models.generate_content API
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
                response_modalities=["TEXT"],
            ),
        )
        
        # Extract text from the response
        if hasattr(response, 'text'):
            return response.text
        elif response.candidates:
            # Fallback to extracting from parts
            text_parts = []
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            text_parts.append(part.text)
            return ''.join(text_parts)
        else:
            return ""
    except Exception as e:  # pragma: no cover - network dependent
        raise ProviderOperationError("google", model_name, "completion", str(e))


async def async_text_completion(
    client: Any, prompt: str, model_name: str, temperature: float = 0.7
) -> str:
    return await asyncio.to_thread(
        text_completion, client, prompt, model_name, temperature
    )


def vision_completion(
    client: Any, prompt: str, image_path_or_url: str, model_name: str
) -> str:
    """Process vision inputs with Google's multimodal models.
    
    Args:
        client: The google.genai.Client object.
        prompt: Text prompt describing what to analyze.
        image_path_or_url: Path to local image file or URL.
        model_name: The name of the vision model.
    
    Returns:
        Text response from the model.
    """
    _, genai_types = _get_google_genai_imports()
    if not genai_types:
        raise ProviderOperationError(
            "google",
            model_name,
            "vision_completion",
            "google.genai is not installed",
        )
    
    try:
        # Load image data
        image_data = None
        mime_type = "image/png"
        
        if image_path_or_url.startswith(('http://', 'https://')):
            # Download from URL
            import requests
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
            import mimetypes
            detected_type = mimetypes.guess_type(image_path_or_url)[0]
            if detected_type and detected_type.startswith('image/'):
                mime_type = detected_type
        
        if not image_data:
            raise ProviderOperationError(
                "google",
                model_name,
                "vision_completion",
                f"Could not load image from {image_path_or_url}"
            )
        
        # Build the content with text and image parts
        # Google's API expects contents to be a single structured object, not a list
        image_part = genai_types.Part(
            inline_data=genai_types.Blob(
                mime_type=mime_type,
                data=image_data  # Pass raw bytes, not base64
            )
        )
        
        contents = [prompt, image_part]
        
        # Generate response
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        
        # Extract text from response
        if hasattr(response, 'text'):
            return response.text
        elif response.candidates:
            text_parts = []
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            text_parts.append(part.text)
            return ''.join(text_parts)
        else:
            return ""
            
    except ProviderOperationError:
        raise
    except Exception as e:
        raise ProviderOperationError(
            "google", model_name, "vision_completion", f"API call failed: {e}"
        )


async def async_vision_completion(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
    return await asyncio.to_thread(vision_completion, *args, **kwargs)


async def async_image_generation(
    client: Any, prompt: str, model_name: str
) -> Tuple[str, str]:
    return await asyncio.to_thread(image_generation, client, prompt, model_name)


def image_edit(
    client: Any, prompt: str, image_path: str, model_name: str, **edit_params: Any
) -> Tuple[str, str]:
    """Edit an image using Google's Gemini image models.
    
    Gemini models support image editing through text+image prompts.
    """
    _, genai_types = _get_google_genai_imports()
    if not genai_types:
        raise ProviderOperationError(
            "google",
            model_name,
            "image_edit",
            "google.genai is not installed",
        )
    
    try:
        # Load the image to edit
        import mimetypes
        from PIL import Image as PILImage
        
        # Read the original image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Detect mime type
        mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
        
        # Create image part
        image_part = genai_types.Part(
            inline_data=genai_types.Blob(
                mime_type=mime_type,
                data=image_data
            )
        )
        
        # Build contents with edit instruction and image
        contents = [image_part, prompt]
        
        # Generate edited image
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        
        # Extract the edited image from response
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        # Check for inline_data with image content
                        blob = getattr(part, "inline_data", None)
                        if blob:
                            data = getattr(blob, "data", None)
                            result_mime_type = getattr(blob, "mime_type", "image/png")
                            if data:
                                # Return base64-encoded string
                                if isinstance(data, bytes):
                                    return base64.b64encode(data).decode("utf-8"), result_mime_type
                                elif isinstance(data, str):
                                    # Already base64 encoded
                                    return data, result_mime_type
        
        raise ProviderOperationError(
            "google", model_name, "image_edit", "No edited image in response"
        )
        
    except ProviderOperationError:
        raise
    except Exception as e:
        raise ProviderOperationError(
            "google", model_name, "image_edit", f"Edit failed: {e}"
        )


async def async_image_edit(
    *args: Any, **kwargs: Any
) -> Tuple[str, str]:  # pragma: no cover
    return await asyncio.to_thread(image_edit, *args, **kwargs)


def transcribe_audio(
    client: Any, audio_path: str, model_name: str, language_code: str = "en-US"
) -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "")
    rate_limit("google", api_key, model_name)
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()
    audio = {"content": content}
    config = {"language_code": language_code}
    response = client.recognize(config=config, audio=audio, timeout=TOTAL_TIMEOUT)
    if response.results:
        return response.results[0].alternatives[0].transcript
    raise ProviderOperationError(
        "google",
        model_name,
        "audio transcription",
        "No transcription result from Google Speech-to-Text.",
    )


async def async_transcribe_audio(
    client: Any, audio_path: str, model_name: str, language_code: str = "en-US"
) -> str:
    return await asyncio.to_thread(
        transcribe_audio, client, audio_path, model_name, language_code
    )
