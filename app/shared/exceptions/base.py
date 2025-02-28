from typing import Any, Dict, Optional

class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(self.message)

class ValidationError(AppException):
    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, extra=extra)

class AuthenticationError(AppException):
    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, extra=extra)

class AuthorizationError(AppException):
    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, extra=extra)

class NotFoundError(AppException):
    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, extra=extra)
