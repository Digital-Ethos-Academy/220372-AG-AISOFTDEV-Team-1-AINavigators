"""Provider specific implementations."""
from . import openai, anthropic, huggingface, google

PROVIDERS = {
    'openai': openai,
    'anthropic': anthropic,
    'huggingface': huggingface,
    'google': google,
    'gemini': google,  # alias
}

__all__ = ['PROVIDERS']
