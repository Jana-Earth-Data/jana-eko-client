"""
Custom exception classes for the Eko Client library.
"""


class EkoClientError(Exception):
    """Base exception for all Eko Client errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class EkoAuthenticationError(EkoClientError):
    """Raised when authentication fails."""
    pass


class EkoAPIError(EkoClientError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int, response_data: dict = None):
        super().__init__(message, status_code, response_data)
        self.status_code = status_code


class EkoRateLimitError(EkoAPIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, response_data: dict = None):
        super().__init__(message, 429, response_data)
        self.retry_after = retry_after


class EkoSessionExpiredError(EkoAuthenticationError):
    """Raised when both access and refresh tokens have expired.

    The caller should re-authenticate (e.g. ``client.login_device()``).
    Subclasses ``EkoAuthenticationError`` so existing ``except
    EkoAuthenticationError`` handlers still catch it, but callers that
    want to distinguish "re-login needed" from other auth errors can
    catch this specifically.
    """

    def __init__(
        self,
        message: str = (
            "Session expired (refresh token is invalid or expired). "
            "Please re-authenticate with login_device() or login_password()."
        ),
        status_code: int = None,
        response_data: dict = None,
    ):
        super().__init__(message, status_code, response_data)


class EkoNotFoundError(EkoAPIError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", response_data: dict = None):
        super().__init__(message, 404, response_data)

