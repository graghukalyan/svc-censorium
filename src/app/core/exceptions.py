"""Custom exceptions."""


class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(BaseAPIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)
