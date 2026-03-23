"""Tests for eko_client.auth — AuthMixin (legacy, superseded by JwtAuthMixin)."""

import pytest
import httpx
import respx

from eko_client.auth import AuthMixin
from eko_client.client import BaseEkoClient

BASE_URL = "https://test.jana.earth"


class TestAuthMixin:
    """AuthMixin delegates to BaseEkoClient.login/logout. Verify the MRO works."""

    @respx.mock
    def test_login_delegates(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"token": "tok-from-mixin"})
        )

        class TestClient(AuthMixin, BaseEkoClient):
            pass

        client = TestClient(base_url=BASE_URL)
        token = client.login("u", "p")
        assert token == "tok-from-mixin"
        client.close()

    @respx.mock
    def test_logout_clears_token(self):
        respx.post(f"{BASE_URL}/api/auth/logout/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )

        class TestClient(AuthMixin, BaseEkoClient):
            pass

        client = TestClient(base_url=BASE_URL, token="tok")
        client.logout()
        assert client.token is None

    @respx.mock
    def test_get_user_info(self):
        respx.get(f"{BASE_URL}/api/auth/user/").mock(
            return_value=httpx.Response(200, json={"username": "dev-user"})
        )

        class TestClient(AuthMixin, BaseEkoClient):
            pass

        client = TestClient(base_url=BASE_URL, token="tok")
        info = client.get_user_info()
        assert info["username"] == "dev-user"
        client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_user_info_async(self):
        respx.get(f"{BASE_URL}/api/auth/user/").mock(
            return_value=httpx.Response(200, json={"username": "dev-user"})
        )

        class TestClient(AuthMixin, BaseEkoClient):
            pass

        client = TestClient(base_url=BASE_URL, token="tok")
        info = await client.get_user_info_async()
        assert info["username"] == "dev-user"
        await client.close_async()
