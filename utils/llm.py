# ruff: noqa: E501
from __future__ import annotations

import asyncio
import re
from typing import Any, Optional, Tuple

from .errors import ProviderOperationError
from .helpers import ensure_provider, normalize_prompt
from .logging import get_logger
from .models import RECOMMENDED_MODELS
from .providers import PROVIDERS
from .settings import load_environment

logger = get_logger()


def setup_llm_client(
    model_name: str = "gpt-4o",
) -> Tuple[Any, str, str] | Tuple[None, None, None]:
    """Configure and return an LLM client based on ``model_name``."""
    load_environment()
    if model_name not in RECOMMENDED_MODELS:
        logger.error(
            "Model '%s' is not in the list of recommended models.",
            model_name,
            extra={"provider": None, "model": model_name},
        )
        return None, None, None
    config = RECOMMENDED_MODELS[model_name]
    provider_name = config["provider"]
    provider_module = PROVIDERS.get(provider_name)
    if not provider_module:
        logger.error(
            "Unsupported provider '%s'",
            provider_name,
            extra={"provider": provider_name, "model": model_name},
        )
        return None, None, None
    try:
        client = provider_module.setup_client(model_name, config)
    except Exception as e:  # pragma: no cover - network dependent
        logger.error("%s", e, extra={"provider": provider_name, "model": model_name})
        return None, None, None
    logger.info(
        "LLM Client configured", extra={"provider": provider_name, "model": model_name}
    )
    return client, model_name, provider_name


async def async_setup_llm_client(
    model_name: str = "gpt-4o",
) -> Tuple[Any, str, str] | Tuple[None, None, None]:
    """Asynchronously configure and return an LLM client based on ``model_name``."""
    load_environment()
    if model_name not in RECOMMENDED_MODELS:
        logger.error(
            "Model '%s' is not in the list of recommended models.",
            model_name,
            extra={"provider": None, "model": model_name},
        )
        return None, None, None
    config = RECOMMENDED_MODELS[model_name]
    provider_name = config["provider"]
    provider_module = PROVIDERS.get(provider_name)
    if not provider_module:
        logger.error(
            "Unsupported provider '%s'",
            provider_name,
            extra={"provider": provider_name, "model": model_name},
        )
        return None, None, None
    try:
        if hasattr(provider_module, "async_setup_client"):
            client = await provider_module.async_setup_client(model_name, config)
        else:
            client = provider_module.setup_client(model_name, config)
    except Exception as e:  # pragma: no cover - network dependent
        logger.error("%s", e, extra={"provider": provider_name, "model": model_name})
        return None, None, None
    logger.info(
        "LLM Client configured", extra={"provider": provider_name, "model": model_name}
    )
    return client, model_name, provider_name


def get_completion(
    prompt: str,
    client: Any,
    model_name: str,
    api_provider: str,
    temperature: float = 0.7,
) -> str:
    """Fetch a text completion.

    Raises
    ------
    ProviderOperationError
        If the provider call fails.

    Example
    -------
    >>> client, model, provider = setup_llm_client()
    >>> try:
    ...     get_completion("Hello", client, model, provider)
    ... except ProviderOperationError:
    ...     ...
    """
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(client, api_provider, model_name, "completion")
    return provider_module.text_completion(client, prompt, model_name, temperature)


async def async_get_completion(
    prompt: str,
    client: Any,
    model_name: str,
    api_provider: str,
    temperature: float = 0.7,
) -> str:
    """Asynchronously fetch a text completion.

    Raises
    ------
    ProviderOperationError
        If the provider call fails.

    Example
    -------
    >>> import asyncio
    >>> async def main(prompts):
    ...     client, model, provider = await async_setup_llm_client()
    ...     tasks = [
    ...         async_get_completion(p, client, model, provider)
    ...         for p in prompts
    ...     ]
    ...     return await asyncio.gather(*tasks)
    """
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(client, api_provider, model_name, "completion")
    if hasattr(provider_module, "async_text_completion"):
        return await provider_module.async_text_completion(
            client, prompt, model_name, temperature
        )
    return await asyncio.to_thread(
        provider_module.text_completion, client, prompt, model_name, temperature
    )


def get_completion_compat(
    prompt: str,
    client: Any,
    model_name: str,
    api_provider: str,
    temperature: float = 0.7,
) -> Tuple[Optional[str], Optional[str]]:
    """Compatibility wrapper returning ``(result, error_str)``.

    .. deprecated:: 1.0
       Use :func:`get_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        return (
            get_completion(prompt, client, model_name, api_provider, temperature),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


async def async_get_completion_compat(
    prompt: str,
    client: Any,
    model_name: str,
    api_provider: str,
    temperature: float = 0.7,
) -> Tuple[Optional[str], Optional[str]]:
    """Async compatibility wrapper returning ``(result, error_str)``.

    .. deprecated:: 1.0
       Use :func:`async_get_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        return (
            await async_get_completion(
                prompt, client, model_name, api_provider, temperature
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


def get_vision_completion(
    prompt: str, image_path_or_url: str, client: Any, model_name: str, api_provider: str
) -> str:
    """Fetch a vision completion for ``image_path_or_url``.

    Raises
    ------
    ProviderOperationError
        If the provider call fails.

    Example
    -------
    >>> client, model, provider = setup_llm_client()
    >>> get_vision_completion("Describe", "image.png", client, model, provider)
    """
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(
        client, api_provider, model_name, "vision completion"
    )
    return provider_module.vision_completion(
        client, prompt, image_path_or_url, model_name
    )


async def async_get_vision_completion(
    prompt: str,
    image_path_or_url: str,
    client: Any,
    model_name: str,
    api_provider: str,
) -> str:
    """Asynchronously fetch a vision completion for an image.

    Raises
    ------
    ProviderOperationError
        If the provider call fails.

    Example
    -------
    >>> client, model, provider = await async_setup_llm_client()
    >>> await async_get_vision_completion(
    ...     "Describe", "image.png", client, model, provider
    ... )
    """
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(
        client, api_provider, model_name, "vision completion"
    )
    if hasattr(provider_module, "async_vision_completion"):
        return await provider_module.async_vision_completion(
            client, prompt, image_path_or_url, model_name
        )
    return await asyncio.to_thread(
        provider_module.vision_completion,
        client,
        prompt,
        image_path_or_url,
        model_name,
    )


def get_vision_completion_compat(
    prompt: str,
    image_path_or_url: str,
    client: Any,
    model_name: str,
    api_provider: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Compatibility wrapper returning ``(result, error_str)``.

    .. deprecated:: 1.0
       Use :func:`get_vision_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        return (
            get_vision_completion(
                prompt, image_path_or_url, client, model_name, api_provider
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


async def async_get_vision_completion_compat(
    prompt: str,
    image_path_or_url: str,
    client: Any,
    model_name: str,
    api_provider: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Async compatibility wrapper returning ``(result, error_str)``.

    .. deprecated:: 1.0
       Use :func:`async_get_vision_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        return (
            await async_get_vision_completion(
                prompt, image_path_or_url, client, model_name, api_provider
            ),
            None,
        )
    except ProviderOperationError as e:
        return None, str(e)


def get_image_generation_completion(
    client: Any, prompt: str, model_name: str, api_provider: str
) -> Tuple[str, str]:
    """
    Generates an image based on a prompt using the specified API provider.

    Args:
        client: The API client.
        prompt (str): The text prompt for image generation.
        model_name (str): The name of the model to use.
        api_provider (str): The API provider ('google', 'openai', etc.).

    Returns:
        A tuple containing the base64-encoded image and the MIME type.
    """
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(
        client, api_provider, model_name, "image generation"
    )
    
    return provider_module.image_generation(client, prompt, model_name)


async def async_get_image_generation_completion(
    client: Any, prompt: str, model_name: str, api_provider: str
) -> Tuple[str, str]:
    """Asynchronously fetch an image generation completion."""
    prompt = normalize_prompt(prompt)
    provider_module = ensure_provider(
        client, api_provider, model_name, "image generation"
    )
    if hasattr(provider_module, "async_image_generation"):
        if api_provider == "google":
            return await provider_module.async_image_generation(client, prompt, model_name)
        return await provider_module.async_image_generation(
            client, prompt, model_name
        )
    if api_provider == "google":
        return await asyncio.to_thread(
            provider_module.image_generation, client, prompt, model_name
        )
    return await asyncio.to_thread(
        provider_module.image_generation, client, prompt, model_name
    )


def get_image_generation_completion_compat(
    client: Any, prompt: str, model_name: str, api_provider: str
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Compatibility wrapper returning ``(base64_str, mime_type, error_str)``.

    .. deprecated:: 1.0
       Use :func:`get_image_generation_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        b64, mime = get_image_generation_completion(
            client, prompt, model_name, api_provider
        )
        return b64, mime, None
    except ProviderOperationError as e:
        return None, None, str(e)


async def async_get_image_generation_completion_compat(
    client: Any, prompt: str, model_name: str, api_provider: str
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Async compatibility wrapper for image generation.

    .. deprecated:: 1.0
       Use :func:`async_get_image_generation_completion` and catch :class:`ProviderOperationError`.
    """
    try:
        b64, mime = await async_get_image_generation_completion(
            client, prompt, model_name, api_provider
        )
        return b64, mime, None
    except ProviderOperationError as e:
        return None, None, str(e)


def clean_llm_output(output_str: str, language: str = "json") -> str:
    """Cleans markdown code fences from LLM output."""
    if "```" in output_str:
        pattern = re.compile(
            r"```(?:" + re.escape(language) + r")?\s*\n(.*?)\n```",
            re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(output_str)
        if match:
            return match.group(1).strip()
        parts = output_str.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
        return output_str.strip()
    return output_str.strip()


def prompt_enhancer(
    user_input: str,
    model_name: str = "o3",
    client: Any | None = None,
    api_provider: str | None = None,
) -> str:
    """Enhance a raw user prompt using a meta-prompt optimization system.

    Raises
    ------
    ProviderOperationError
        If prompt enhancement fails.

    Example
    -------
    >>> client, model, provider = setup_llm_client("o3")
    >>> prompt_enhancer("write a poem", model, client, provider)
    """
    user_input = normalize_prompt(user_input)
    if not user_input:
        prov = api_provider or RECOMMENDED_MODELS.get(model_name, {}).get(
            "provider", "unknown"
        )
        raise ProviderOperationError(
            prov,
            model_name,
            "prompt enhancement",
            "No user input provided for enhancement.",
        )

    if model_name not in RECOMMENDED_MODELS:
        prov = api_provider or "unknown"
        raise ProviderOperationError(
            prov,
            model_name,
            "prompt enhancement",
            f"Model '{model_name}' not found in RECOMMENDED_MODELS. Original input: {user_input}",
        )

    optimization_prompt = f"""You are an elite Prompt Optimization Engine. Your design is based on the understanding that prompt engineering is a rigorous technical discipline, essential for maximizing LLM efficacy and reliability. Your function is to analyze raw user inputs and systematically compile them into optimized, high-quality prompts.

**User Input:**
<user_input>
{user_input}
</user_input>

**Optimization Protocol:**
Follow this systematic protocol to analyze the user input and construct the optimized prompt.

### Phase 1: Analysis and Strategy Determination
1.  **Analyze Intent and Complexity:** Deconstruct the user's input to identify the core objective. Assess the complexity: Does it require simple retrieval, creative generation, or complex, multi-step reasoning?
2.  **Determine Strategic Enhancements:**
    *   **Chain-of-Thought (CoT):** If the task involves complex reasoning, analysis, or multi-step problem-solving, you must incorporate CoT prompting (e.g., instructing the model to "think step by step").
    *   **In-Context Learning (ICL):** If the task requires a highly specific output format (e.g., structured data) or involves nuanced pattern recognition, generate 1-2 relevant input/output examples (Few-Shot prompting) to guide the model.

### Phase 2: Prompt Construction and Enhancement
Construct the optimized prompt by ensuring the following components are explicitly defined and integrated:

1.  **Role Assignment (Persona):**
    *   Define the most authoritative expert persona for the LLM to adopt (e.g., "You are a Senior Cybersecurity Analyst," "Act as an expert Python developer"). This constrains the knowledge space for improved accuracy and focus.

2.  **Context Provision and Grounding:**
    *   Provide comprehensive background information, define key terms unambiguously, and state all constraints or rules. Ensure the model has sufficient information to ground its response in a relevant factual basis.

3.  **Task Definition and Clarity:**
    *   Use precise, unambiguous instructions and assertive action verbs (e.g., "Analyze," "Synthesize," "Generate").
    *   Decompose the main objective into a clear sequence of steps if necessary.

4.  **Expectation Setting (Output Specification):**
    *   Explicitly define the desired output format (e.g., Markdown report, JSON object, bulleted list), length constraints, style, and target audience.

### Phase 3: Structural Integrity
Organize the entire prompt using clear structural delimiters to ensure optimal parsing
by the target LLM. Clearly differentiate between instructions, context, examples,
and the core task (e.g., using XML tags such as `<persona>`, `<context>`,
`<instructions>`, `<examples>`, `<output_format>`).

### Output
Generate only the final, optimized prompt."""

    try:
        actual_model: str | None
        provider: str | None
        if client and api_provider:
            actual_model = model_name
            provider = api_provider
        else:
            client, actual_model, provider = setup_llm_client(model_name)
            if not client:
                raise ProviderOperationError(
                    provider or "unknown",
                    model_name,
                    "prompt enhancement",
                    (
                        f"Failed to initialize LLM client for model '{model_name}'. "
                        f"Original input: {user_input}"
                    ),
                )

        if actual_model is None or provider is None:
            raise ProviderOperationError(
                provider or "unknown",
                model_name,
                "prompt enhancement",
                (
                    f"LLM client setup returned None for model or provider. "
                    f"actual_model: {actual_model}, provider: {provider}. "
                    f"Original input: {user_input}"
                ),
            )
        enhanced_prompt = get_completion(
            optimization_prompt,
            client,
            actual_model,
            provider,
            temperature=0.3,
        )
        return enhanced_prompt.strip()
    except ProviderOperationError as e:
        raise ProviderOperationError(e.provider, e.model, "prompt enhancement", str(e))
    except Exception as e:
        prov = api_provider or locals().get("provider", "unknown")
        raise ProviderOperationError(
            prov,
            model_name,
            "prompt enhancement",
            f"{e}. Original input: {user_input}",
        )


def prompt_enhancer_compat(
    user_input: str,
    model_name: str = "o3",
    client: Any | None = None,
    api_provider: str | None = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Compatibility wrapper returning ``(result, error_str)``.

    .. deprecated:: 1.0
       Use :func:`prompt_enhancer` and catch :class:`ProviderOperationError`.
    """
    try:
        return prompt_enhancer(user_input, model_name, client, api_provider), None
    except ProviderOperationError as e:
        return None, str(e)


__all__ = [
    "setup_llm_client",
    "async_setup_llm_client",
    "get_completion",
    "get_completion_compat",
    "async_get_completion",
    "async_get_completion_compat",
    "get_vision_completion",
    "get_vision_completion_compat",
    "async_get_vision_completion",
    "async_get_vision_completion_compat",
    "get_image_generation_completion",
    "get_image_generation_completion_compat",
    "async_get_image_generation_completion",
    "async_get_image_generation_completion_compat",
    "clean_llm_output",
    "prompt_enhancer",
    "prompt_enhancer_compat",
]
