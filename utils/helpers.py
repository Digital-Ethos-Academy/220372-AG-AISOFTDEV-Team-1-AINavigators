from __future__ import annotations

from typing import Any

from .errors import CLIENT_NOT_INITIALIZED, UNSUPPORTED_PROVIDER, ProviderOperationError
from .providers import PROVIDERS


def ensure_provider(
    client: Any, api_provider: str, model_name: str, operation: str
) -> Any:
    """Validate client and provider and return the provider module."""
    if not client:
        raise ProviderOperationError(
            api_provider, model_name, operation, CLIENT_NOT_INITIALIZED
        )
    provider_module = PROVIDERS.get(api_provider)
    if not provider_module:
        raise ProviderOperationError(
            api_provider, model_name, operation, UNSUPPORTED_PROVIDER
        )
    return provider_module


def normalize_prompt(prompt: str) -> str:
    """Normalize user prompt by stripping whitespace."""
    return prompt.strip()


__all__ = ["ensure_provider", "normalize_prompt"]
