"""
Custom exception classes for the StaffAlloc application.

These exceptions provide a consistent way to handle and report errors
throughout the application, with appropriate HTTP status codes.
"""
from typing import Any, Optional


class AppException(Exception):
    """
    Base exception class for all application-specific exceptions.
    
    This exception is designed to be caught by FastAPI's exception handler
    and converted into a proper HTTP response with the specified status code.
    """
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        headers: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the application exception.
        
        Args:
            detail: A human-readable description of the error
            status_code: HTTP status code to return (default: 500)
            headers: Optional HTTP headers to include in the response
        """
        self.detail = detail
        self.status_code = status_code
        self.headers = headers
        super().__init__(detail)


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class BadRequestException(AppException):
    """Exception raised when a request is malformed or invalid."""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400)


class UnauthorizedException(AppException):
    """Exception raised when authentication is required but not provided."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, status_code=401)


class ForbiddenException(AppException):
    """Exception raised when the user doesn't have permission for the action."""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail=detail, status_code=403)


class ConflictException(AppException):
    """Exception raised when a request conflicts with the current state."""
    
    def __init__(self, detail: str = "Conflict"):
        super().__init__(detail=detail, status_code=409)


class ValidationException(AppException):
    """Exception raised when data validation fails."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=422)

