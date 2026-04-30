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


@pytest.fixture
def live_client(live_credentials):
    """JWT-authenticated EkoUserClient pointed at api-test.jana.earth.

    Uses the JWT auth path (auth-dev for ``/api/auth/*``, api-test for
    everything else). Each test gets a fresh client (function scope) and a
    fresh JWT login via :meth:`JwtAuthMixin.login_password`, which posts
    ``{email, password}`` to ``/api/auth/login/`` and stores
    ``access_token`` / ``refresh_token``.

    Why function scope (not session):
        ``EkoUserClient`` lazily creates an ``httpx.AsyncClient`` on first
        async use, binding it to the current event loop. pytest-asyncio
        creates a new event loop per test by default, so a session-scoped
        client breaks on the second async test with
        ``RuntimeError: Event loop is closed``. With only 4 nightly tests,
        4 fresh logins is trivial overhead.

    Why we don't pass username/password to the constructor:
        ``BaseEkoClient.__init__`` auto-login routes through the legacy
        DRF token endpoint (``{username, password}`` payload), which the
        JWT auth server rejects with HTTP 400. We construct first, then
        call ``login_password`` explicitly to use the JWT flow.
    """
    from eko_client.user_client import EkoUserClient

    email, password = live_credentials
    client = EkoUserClient(
        base_url=AUTH_BASE_URL,
        api_base_url=API_BASE_URL,
    )
    client.login_password(email=email, password=password)
    yield client
    client.close()
