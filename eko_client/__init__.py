"""
Eko Client - Python client library for FinRocket Unified Environmental Data API.

This package provides a clean, Pythonic interface to access environmental data
from OpenAQ, Climate TRACE, and EDGAR sources through the unified API.
"""

from .exceptions import (
    EkoClientError,
    EkoAuthenticationError,
    EkoSessionExpiredError,
    EkoAPIError,
    EkoRateLimitError,
    EkoNotFoundError,
)

from .user_client import EkoUserClient
from .admin_client import EkoAdminClient
from .jwt_auth import JwtAuthMixin

__version__ = "0.1.0"
__all__ = [
    "EkoUserClient",
    "EkoAdminClient",
    "JwtAuthMixin",
    "EkoClientError",
    "EkoAuthenticationError",
    "EkoSessionExpiredError",
    "EkoAPIError",
    "EkoRateLimitError",
    "EkoNotFoundError",
]

