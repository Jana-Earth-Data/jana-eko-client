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
from .jwt_auth import JwtAuthMixin

__version__ = "0.3.0"
__all__ = [
    "EkoUserClient",
    "JwtAuthMixin",
    "EkoClientError",
    "EkoAuthenticationError",
    "EkoSessionExpiredError",
    "EkoAPIError",
    "EkoRateLimitError",
    "EkoNotFoundError",
]

