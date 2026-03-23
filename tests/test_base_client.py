"""Tests for eko_client.client — BaseEkoClient core functionality."""

import json
import pytest
import httpx
import respx

from eko_client.client import BaseEkoClient
from eko_client.exceptions import (
    EkoClientError,
    EkoAuthenticationError,
    EkoAPIError,
    EkoRateLimitError,
    EkoNotFoundError,
)

BASE_URL = "https://test.jana.earth"
API_BASE_URL = "https://api-test.jana.earth"


# ── Initialization ───────────────────────────────────────────────────────────

class TestInit:

    def test_basic_init(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        assert client.base_url == BASE_URL
        assert client.token == "tok"
        assert client.api_base_url is None
        assert client.timeout == 120
        assert client.verify_ssl is True
        client.close()

    def test_strips_trailing_slash(self):
        client = BaseEkoClient(base_url=f"{BASE_URL}/", token="tok")
        assert client.base_url == BASE_URL
        client.close()

    def test_dual_url(self):
        client = BaseEkoClient(
            base_url=BASE_URL, api_base_url=API_BASE_URL, token="tok"
        )
        assert client.api_base_url == API_BASE_URL
        client.close()

    def test_custom_timeout_and_ssl(self):
        client = BaseEkoClient(
            base_url=BASE_URL, token="tok", timeout=30, verify_ssl=False
        )
        assert client.timeout == 30
        assert client.verify_ssl is False
        client.close()

    @respx.mock
    def test_auto_login_with_credentials(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"token": "auto-tok"})
        )
        client = BaseEkoClient(
            base_url=BASE_URL, username="user", password="pass"
        )
        assert client.token == "auto-tok"
        client.close()

    def test_no_auto_login_without_credentials(self):
        client = BaseEkoClient(base_url=BASE_URL)
        assert client.token is None
        client.close()


# ── URL Resolution ───────────────────────────────────────────────────────────

class TestResolveBaseUrl:

    def test_single_url_always_returns_base(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        assert client._resolve_base_url("/api/v1/esg/data/") == BASE_URL
        assert client._resolve_base_url("/api/auth/login/") == BASE_URL
        client.close()

    def test_dual_url_routes_auth_to_base(self):
        client = BaseEkoClient(
            base_url=BASE_URL, api_base_url=API_BASE_URL, token="tok"
        )
        assert client._resolve_base_url("/api/auth/login/") == BASE_URL
        assert client._resolve_base_url("/api/auth/user/") == BASE_URL
        client.close()

    def test_dual_url_routes_data_to_api(self):
        client = BaseEkoClient(
            base_url=BASE_URL, api_base_url=API_BASE_URL, token="tok"
        )
        assert client._resolve_base_url("/api/v1/esg/data/") == API_BASE_URL
        assert client._resolve_base_url("/api/v1/management/jobs/") == API_BASE_URL
        client.close()


# ── Headers ──────────────────────────────────────────────────────────────────

class TestHeaders:

    def test_headers_with_token(self):
        client = BaseEkoClient(base_url=BASE_URL, token="my-token")
        headers = client._get_headers()
        assert headers["Authorization"] == "Token my-token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        client.close()

    def test_headers_without_token(self):
        client = BaseEkoClient(base_url=BASE_URL)
        headers = client._get_headers()
        assert "Authorization" not in headers
        client.close()


# ── Response Handling ────────────────────────────────────────────────────────

class TestHandleResponse:

    def _make_response(self, status_code, body=None, text=""):
        """Build a minimal httpx.Response for testing."""
        if body is not None:
            return httpx.Response(status_code, json=body)
        return httpx.Response(status_code, text=text)

    def test_success_json(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(200, {"results": [1, 2]})
        assert client._handle_response(resp) == {"results": [1, 2]}
        client.close()

    def test_success_non_json(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = httpx.Response(200, text="plain text", headers={"content-type": "text/plain"})
        result = client._handle_response(resp)
        assert result == {"content": "plain text"}
        client.close()

    def test_401_raises_auth_error(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(401, {"error": "Invalid token"})
        with pytest.raises(EkoAuthenticationError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.status_code == 401
        client.close()

    def test_404_raises_not_found(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(404, {"error": "Not found"})
        with pytest.raises(EkoNotFoundError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.status_code == 404
        client.close()

    def test_429_raises_rate_limit(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(429, {"error": "Too many", "retry_after": "60"})
        with pytest.raises(EkoRateLimitError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.retry_after == 60
        client.close()

    def test_429_without_retry_after(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(429, {"error": "Too many"})
        with pytest.raises(EkoRateLimitError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.retry_after is None
        client.close()

    def test_500_raises_api_error(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = self._make_response(500, {"error": "Internal"})
        with pytest.raises(EkoAPIError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.status_code == 500
        client.close()

    def test_error_with_non_json_body(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        resp = httpx.Response(500, text="Server Error", headers={"content-type": "text/plain"})
        with pytest.raises(EkoAPIError):
            client._handle_response(resp)
        client.close()


# ── Sync Request ─────────────────────────────────────────────────────────────

class TestRequestSync:

    @respx.mock
    def test_get_request(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        result = client._request_sync("GET", "/api/v1/esg/health/")
        assert result == {"status": "ok"}
        client.close()

    @respx.mock
    def test_post_request_with_json(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"token": "abc"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        result = client._request_sync(
            "POST", "/api/auth/login/",
            json_data={"username": "u", "password": "p"},
        )
        assert result == {"token": "abc"}
        client.close()

    @respx.mock
    def test_get_with_params(self):
        route = respx.get(f"{BASE_URL}/api/v1/esg/data/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client._request_sync("GET", "/api/v1/esg/data/", params={"limit": 10})
        assert route.called
        client.close()

    @respx.mock
    def test_http_error_raises_client_error(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        with pytest.raises(EkoClientError, match="HTTP request failed"):
            client._request_sync("GET", "/api/v1/esg/health/")
        client.close()


# ── Async Request ────────────────────────────────────────────────────────────

class TestRequestAsync:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_request(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        result = await client._request_async("GET", "/api/v1/esg/health/")
        assert result == {"status": "ok"}
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_post_request(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"token": "abc"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        result = await client._request_async(
            "POST", "/api/auth/login/",
            json_data={"username": "u", "password": "p"},
        )
        assert result == {"token": "abc"}
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_http_error_raises_client_error(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            side_effect=httpx.ConnectError("refused")
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        with pytest.raises(EkoClientError, match="HTTP request failed"):
            await client._request_async("GET", "/api/v1/esg/health/")
        await client.close_async()


# ── Login / Logout ───────────────────────────────────────────────────────────

class TestLogin:

    @respx.mock
    def test_login_success(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"token": "new-tok"})
        )
        client = BaseEkoClient(base_url=BASE_URL)
        token = client.login("user", "pass")
        assert token == "new-tok"
        assert client.token == "new-tok"
        client.close()

    @respx.mock
    def test_login_no_token_in_response(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"message": "ok"})
        )
        client = BaseEkoClient(base_url=BASE_URL)
        with pytest.raises(EkoAuthenticationError, match="No token received"):
            client.login("user", "pass")
        client.close()

    @respx.mock
    def test_login_api_error(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(400, json={"error": "bad creds"})
        )
        client = BaseEkoClient(base_url=BASE_URL)
        with pytest.raises(EkoAuthenticationError, match="Login failed"):
            client.login("user", "wrong")
        client.close()


class TestLogout:

    @respx.mock
    def test_logout_clears_token(self):
        respx.post(f"{BASE_URL}/api/auth/logout/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.logout()
        assert client.token is None

    def test_logout_no_token_is_noop(self):
        client = BaseEkoClient(base_url=BASE_URL)
        client.logout()  # should not raise
        assert client.token is None

    @respx.mock
    def test_logout_ignores_errors(self):
        respx.post(f"{BASE_URL}/api/auth/logout/").mock(
            return_value=httpx.Response(500, json={"error": "fail"})
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.logout()  # should not raise
        assert client.token is None


# ── Close / Context Manager ──────────────────────────────────────────────────

class TestClose:

    def test_close_sync(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        # Force creation of sync client
        _ = client._get_sync_client()
        assert client._sync_client is not None
        client.close_sync()
        assert client._sync_client is None

    @pytest.mark.asyncio
    async def test_close_async(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        _ = client._get_async_client()
        assert client._async_client is not None
        await client.close_async()
        assert client._async_client is None

    def test_close_calls_close_sync(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        _ = client._get_sync_client()
        client.close()
        assert client._sync_client is None

    def test_context_manager(self):
        with BaseEkoClient(base_url=BASE_URL, token="tok") as client:
            _ = client._get_sync_client()
            assert client._sync_client is not None
        assert client._sync_client is None


# ── Client Lazy Creation ─────────────────────────────────────────────────────

class TestClientCreation:

    def test_sync_client_created_lazily(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        assert client._sync_client is None
        sc = client._get_sync_client()
        assert sc is not None
        assert isinstance(sc, httpx.Client)
        # Same instance on second call
        assert client._get_sync_client() is sc
        client.close()

    def test_async_client_created_lazily(self):
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        assert client._async_client is None
        ac = client._get_async_client()
        assert ac is not None
        assert isinstance(ac, httpx.AsyncClient)
        assert client._get_async_client() is ac
        client.close()
