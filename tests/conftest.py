"""Shared fixtures for jana-eko-client tests."""

import pytest
import httpx
import respx
from unittest.mock import patch

from eko_client.client import BaseEkoClient
from eko_client.user_client import EkoUserClient


BASE_URL = "https://test.jana.earth"
API_BASE_URL = "https://api-test.jana.earth"


@pytest.fixture
def base_client():
    """BaseEkoClient with a pre-set token (skip auto-login)."""
    client = BaseEkoClient(base_url=BASE_URL, token="test-token-abc123")
    yield client
    client.close()


@pytest.fixture
def base_client_dual():
    """BaseEkoClient with separate auth and API base URLs."""
    client = BaseEkoClient(
        base_url=BASE_URL,
        api_base_url=API_BASE_URL,
        token="test-token-abc123",
    )
    yield client
    client.close()


@pytest.fixture
def user_client():
    """EkoUserClient with a pre-set DRF token (skip auto-login)."""
    client = EkoUserClient(base_url=BASE_URL, token="test-token-abc123")
    yield client
    client.close()


@pytest.fixture
def user_client_dual():
    """EkoUserClient with separate auth and API base URLs."""
    client = EkoUserClient(
        base_url=BASE_URL,
        api_base_url=API_BASE_URL,
        token="test-token-abc123",
    )
    yield client
    client.close()


@pytest.fixture
def mock_api():
    """respx mock router scoped to each test."""
    with respx.mock(assert_all_called=False) as rsps:
        yield rsps
