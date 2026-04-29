"""Conftest for live-API integration tests.

These fixtures perform a real JWT login against ``auth-dev.jana.earth``
and yield an ``EkoUserClient`` configured for ``api-test.jana.earth``.
They are gated behind environment variables so that running

    pytest tests/

without the env vars set will NOT accidentally hit the live API.
"""

from __future__ import annotations

import os

import pytest

# auth-dev/api-test ALB pair — see repos/CLAUDE.md "Public DNS"
AUTH_BASE_URL = os.environ.get("EKO_AUTH_BASE_URL", "https://auth-dev.jana.earth")
API_BASE_URL = os.environ.get("EKO_API_BASE_URL", "https://api-test.jana.earth")


@pytest.fixture(scope="session")
def live_credentials():
    """Return ``(email, password)`` from env, skipping when missing."""
    email = os.environ.get("EKO_TEST_USER")
    password = os.environ.get("EKO_TEST_PASSWORD")
    if not email or not password:
        pytest.skip(
            "Live integration tests skipped: EKO_TEST_USER and "
            "EKO_TEST_PASSWORD must be set in the environment."
        )
    return email, password


@pytest.fixture(scope="session")
def live_client(live_credentials):
    """JWT-authenticated EkoUserClient pointed at api-test.jana.earth.

    Uses the JWT auth path (auth-dev for ``/api/auth/*``, api-test for
    everything else). The client logs in once per test session.
    """
    from eko_client.user_client import EkoUserClient

    email, password = live_credentials
    client = EkoUserClient(
        base_url=AUTH_BASE_URL,
        api_base_url=API_BASE_URL,
        # JWT login uses email/password kwargs on EkoUserClient. The
        # constructor handles the login and stores the access token.
        username=email,
        password=password,
    )
    yield client
    client.close()
