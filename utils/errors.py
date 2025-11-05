class UtilsError(Exception):
    """Base exception for utils module."""

    pass


class ArtifactError(UtilsError, ValueError):
    """Generic artifact operation error."""

    pass


class ArtifactSecurityError(ArtifactError):
    """Raised when a path escapes the artifacts directory."""

    pass


class ArtifactNotFoundError(ArtifactError):
    """Raised when an expected artifact is missing."""

    pass


# Shared error messages
CLIENT_NOT_INITIALIZED = "API client not initialized."
UNSUPPORTED_PROVIDER = "Unsupported provider"


class ProviderOperationError(UtilsError):
    """Error raised for provider/model operation failures."""

    def __init__(self, provider: str, model: str, operation: str, message: str):
        self.provider = provider
        self.model = model
        self.operation = operation
        super().__init__(f"[{provider}:{model}] {operation} error: {message}")
