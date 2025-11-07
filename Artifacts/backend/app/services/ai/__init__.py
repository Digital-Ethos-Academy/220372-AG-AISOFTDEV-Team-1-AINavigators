"""AI service utilities for StaffAlloc."""

from .gemini import (
    GeminiConfigurationError,
    GeminiInvocationError,
    generate_chat_response,
    generate_forecast_insights,
    generate_workload_balance_suggestions,
    recommend_staffing_options,
    scan_allocation_conflicts,
    suggest_header_mapping,
)
from .rag import retrieve_rag_context, reindex_rag_cache

__all__ = [
    "generate_chat_response",
    "recommend_staffing_options",
    "scan_allocation_conflicts",
    "generate_forecast_insights",
    "generate_workload_balance_suggestions",
    "retrieve_rag_context",
    "reindex_rag_cache",
    "GeminiConfigurationError",
    "GeminiInvocationError",
    "suggest_header_mapping",
]

