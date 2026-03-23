"""Tests for eko_client.jwt_auth — JwtAuthMixin."""

import pytest
import httpx
import respx
from unittest.mock import patch

from eko_client.user_client import EkoUserClient
from eko_client.exceptions import (
    EkoAuthenticationError,
    EkoAPIError,
    EkoSessionExpiredError,
)

BASE_URL = "https://test.jana.earth"


# ── Header Override ──────────────────────────────────────────────────────────

class TestJwtHeaders:

    def test_bearer_token_used_when_access_token_set(self):
        client = EkoUserClient(base_url=BASE_URL, token="drf-tok")
        client.access_token = "jwt-access-tok"
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer jwt-access-tok"
        client.close()

    def test_drf_token_fallback(self):
        client = EkoUserClient(base_url=BASE_URL, token="drf-tok")
        headers = client._get_headers()
        assert headers["Authorization"] == "Token drf-tok"
        client.close()

    def test_no_auth_header_when_no_tokens(self):
        client = EkoUserClient(base_url=BASE_URL)
        # Manually clear to avoid auto-login path
        client.token = None
        client.access_token = None
        headers = client._get_headers()
        assert "Authorization" not in headers
        client.close()


# ── login_password ───────────────────────────────────────────────────────────

class TestLoginPassword:

    @respx.mock
    def test_success(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={
                "data": {
                    "access_token": "jwt-access",
                    "refresh_token": "jwt-refresh",
                }
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_password("user@test.com", "pass123")
        assert client.access_token == "jwt-access"
        assert client.refresh_token == "jwt-refresh"
        client.close()

    @respx.mock
    def test_flat_response_no_data_wrapper(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={
                "access_token": "jwt-flat",
                "refresh_token": "jwt-flat-r",
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_password("user@test.com", "pass123")
        assert client.access_token == "jwt-flat"
        client.close()

    @respx.mock
    def test_no_access_token_raises(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"data": {"message": "ok"}})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="No access_token"):
            client.login_password("user@test.com", "pass123")
        client.close()

    @respx.mock
    def test_api_error_wrapped(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(400, json={"error": "bad request"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Login failed"):
            client.login_password("user@test.com", "wrong")
        client.close()


# ── login_password_async ─────────────────────────────────────────────────────

class TestLoginPasswordAsync:

    @respx.mock
    @pytest.mark.asyncio
    async def test_success(self):
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "jwt-a", "refresh_token": "jwt-r"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        await client.login_password_async("u@t.com", "p")
        assert client.access_token == "jwt-a"
        assert client.refresh_token == "jwt-r"
        await client.close_async()


# ── refresh_jwt ──────────────────────────────────────────────────────────────

class TestRefreshJwt:

    @respx.mock
    def test_success(self):
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "new-access", "refresh_token": "new-refresh"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "old-refresh"
        client.refresh_jwt()
        assert client.access_token == "new-access"
        assert client.refresh_token == "new-refresh"
        client.close()

    @respx.mock
    def test_no_rotated_refresh(self):
        """Server doesn't rotate refresh token — old one kept."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "new-access"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "old-refresh"
        client.refresh_jwt()
        assert client.access_token == "new-access"
        assert client.refresh_token == "old-refresh"
        client.close()

    def test_no_refresh_token_raises(self):
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = None
        with pytest.raises(EkoAuthenticationError, match="No refresh token"):
            client.refresh_jwt()
        client.close()

    @respx.mock
    def test_api_error_wrapped(self):
        """refresh_jwt via JwtAuthMixin._request_sync auto-refresh path
        converts the 401 into EkoSessionExpiredError."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(401, json={"error": "invalid"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "bad-refresh"
        with pytest.raises(EkoSessionExpiredError):
            client.refresh_jwt()
        client.close()

    @respx.mock
    def test_non_auth_error_wrapped(self):
        """refresh_jwt wraps non-auth API errors (e.g. 400) into
        EkoAuthenticationError — covers jwt_auth.py line 337."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(400, json={"error": "Bad payload"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "some-refresh"
        with pytest.raises(EkoAuthenticationError, match="Token refresh failed"):
            client.refresh_jwt()
        client.close()


# ── refresh_jwt_async ────────────────────────────────────────────────────────

class TestRefreshJwtAsync:

    @respx.mock
    @pytest.mark.asyncio
    async def test_success(self):
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "new-a"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "r"
        await client.refresh_jwt_async()
        assert client.access_token == "new-a"
        await client.close_async()

    @pytest.mark.asyncio
    async def test_no_refresh_token_raises(self):
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = None
        with pytest.raises(EkoAuthenticationError, match="No refresh token"):
            await client.refresh_jwt_async()
        await client.close_async()


# ── _is_auth_failure ─────────────────────────────────────────────────────────

class TestIsAuthFailure:

    def test_authentication_error_is_auth_failure(self):
        exc = EkoAuthenticationError("bad")
        assert EkoUserClient._is_auth_failure(exc) is True

    def test_403_with_token_keyword(self):
        exc = EkoAPIError("Forbidden", status_code=403, response_data={"detail": "Token expired"})
        assert EkoUserClient._is_auth_failure(exc) is True

    def test_403_with_jwt_keyword(self):
        exc = EkoAPIError("Forbidden", status_code=403, response_data={"detail": "Invalid JWT"})
        assert EkoUserClient._is_auth_failure(exc) is True

    def test_403_with_credentials_keyword(self):
        exc = EkoAPIError("Forbidden", status_code=403, response_data={"detail": "Invalid credentials"})
        assert EkoUserClient._is_auth_failure(exc) is True

    def test_403_without_jwt_keywords(self):
        exc = EkoAPIError("Forbidden", status_code=403, response_data={"detail": "Permission denied"})
        assert EkoUserClient._is_auth_failure(exc) is False

    def test_500_is_not_auth_failure(self):
        exc = EkoAPIError("Server error", status_code=500)
        assert EkoUserClient._is_auth_failure(exc) is False

    def test_generic_exception_is_not_auth_failure(self):
        exc = ValueError("unrelated")
        assert EkoUserClient._is_auth_failure(exc) is False


# ── Auto-refresh on 401/403 ─────────────────────────────────────────────────

class TestAutoRefresh:

    @respx.mock
    def test_sync_auto_refresh_on_401(self):
        """First request gets 401, refresh succeeds, retry succeeds."""
        call_count = {"n": 0}

        def health_handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(401, json={"error": "Invalid token"})
            return httpx.Response(200, json={"status": "ok"})

        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(side_effect=health_handler)
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "refreshed-tok"}
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired-tok"
        client.refresh_token = "valid-refresh"
        result = client._request_sync("GET", "/api/v1/esg/health/")
        assert result == {"status": "ok"}
        assert client.access_token == "refreshed-tok"
        client.close()

    @respx.mock
    def test_sync_session_expired_when_refresh_fails(self):
        """401 + refresh fails = EkoSessionExpiredError."""
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(401, json={"error": "Invalid token"})
        )
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(401, json={"error": "Refresh invalid"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired"
        client.refresh_token = "also-expired"
        with pytest.raises(EkoSessionExpiredError):
            client._request_sync("GET", "/api/v1/esg/health/")
        assert client.access_token is None
        assert client.refresh_token is None
        client.close()

    @respx.mock
    def test_sync_session_expired_when_no_refresh_token(self):
        """401 with no refresh token = EkoSessionExpiredError."""
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(401, json={"error": "Invalid token"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired"
        client.refresh_token = None
        with pytest.raises(EkoSessionExpiredError):
            client._request_sync("GET", "/api/v1/esg/health/")
        client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_auto_refresh_on_401(self):
        call_count = {"n": 0}

        def health_handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(401, json={"error": "Invalid token"})
            return httpx.Response(200, json={"status": "ok"})

        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(side_effect=health_handler)
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "refreshed"}
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired"
        client.refresh_token = "valid"
        result = await client._request_async("GET", "/api/v1/esg/health/")
        assert result == {"status": "ok"}
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_session_expired(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(401, json={"error": "Invalid"})
        )
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(401, json={"error": "Bad refresh"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired"
        client.refresh_token = "bad"
        with pytest.raises(EkoSessionExpiredError):
            await client._request_async("GET", "/api/v1/esg/health/")
        await client.close_async()

    @respx.mock
    def test_non_auth_error_not_retried(self):
        """A 500 error is not retried."""
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(500, json={"error": "Internal"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "tok"
        client.refresh_token = "ref"
        with pytest.raises(EkoAPIError) as exc_info:
            client._request_sync("GET", "/api/v1/esg/health/")
        assert exc_info.value.status_code == 500
        client.close()


# ── get_user_info ────────────────────────────────────────────────────────────

class TestGetUserInfo:

    @respx.mock
    def test_sync_unwraps_data(self):
        respx.get(f"{BASE_URL}/api/auth/user/").mock(
            return_value=httpx.Response(200, json={
                "data": {"username": "dev-user", "email": "dev@test.com"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tok")
        info = client.get_user_info()
        assert info["username"] == "dev-user"
        client.close()

    @respx.mock
    def test_sync_flat_response(self):
        respx.get(f"{BASE_URL}/api/auth/user/").mock(
            return_value=httpx.Response(200, json={
                "username": "dev-user", "email": "dev@test.com"
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tok")
        info = client.get_user_info()
        assert info["username"] == "dev-user"
        client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_unwraps_data(self):
        respx.get(f"{BASE_URL}/api/auth/user/").mock(
            return_value=httpx.Response(200, json={
                "data": {"username": "u"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tok")
        info = await client.get_user_info_async()
        assert info["username"] == "u"
        await client.close_async()


# ── is_authenticated ─────────────────────────────────────────────────────────

class TestIsAuthenticated:

    def test_true_when_access_token(self):
        client = EkoUserClient(base_url=BASE_URL, token="tok")
        client.access_token = "jwt-tok"
        assert client.is_authenticated() is True
        client.close()

    def test_false_when_no_access_token(self):
        client = EkoUserClient(base_url=BASE_URL, token="tok")
        client.access_token = None
        assert client.is_authenticated() is False
        client.close()


# ── login_password_async error paths ────────────────────────────────────────

class TestLoginPasswordAsyncErrors:

    @respx.mock
    @pytest.mark.asyncio
    async def test_api_error_wrapped(self):
        """Async login_password wraps API errors."""
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(400, json={"error": "bad"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Login failed"):
            await client.login_password_async("u@t.com", "wrong")
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_no_access_token_raises(self):
        """Async login_password raises when no access_token in response."""
        respx.post(f"{BASE_URL}/api/auth/login/").mock(
            return_value=httpx.Response(200, json={"data": {"message": "ok"}})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="No access_token"):
            await client.login_password_async("u@t.com", "p")
        await client.close_async()


# ── refresh_jwt_async error paths ───────────────────────────────────────────

class TestRefreshJwtAsyncErrors:

    @respx.mock
    @pytest.mark.asyncio
    async def test_api_error_wrapped(self):
        """Async refresh_jwt wraps API error into EkoSessionExpiredError
        (goes through auto-refresh wrapper)."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(401, json={"error": "invalid"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "bad"
        with pytest.raises(EkoSessionExpiredError):
            await client.refresh_jwt_async()
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_non_auth_error_wrapped(self):
        """Async: non-auth API error (400) wraps into EkoAuthenticationError
        — covers jwt_auth.py line 365."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(400, json={"error": "Bad payload"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "some-refresh"
        with pytest.raises(EkoAuthenticationError, match="Token refresh failed"):
            await client.refresh_jwt_async()
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_rotated_refresh_token(self):
        """Async refresh_jwt picks up rotated refresh token."""
        respx.post(f"{BASE_URL}/api/auth/refresh/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "new-a", "refresh_token": "new-r"}
            })
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.refresh_token = "old"
        await client.refresh_jwt_async()
        assert client.access_token == "new-a"
        assert client.refresh_token == "new-r"
        await client.close_async()


# ── Async auto-refresh: no refresh token ────────────────────────────────────

class TestAutoRefreshAsyncNoRefreshToken:

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_session_expired_when_no_refresh_token(self):
        """Async: 401 with no refresh token = EkoSessionExpiredError."""
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(401, json={"error": "Invalid token"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.access_token = "expired"
        client.refresh_token = None
        with pytest.raises(EkoSessionExpiredError):
            await client._request_async("GET", "/api/v1/esg/health/")
        await client.close_async()


# ── login_device (sync) ─────────────────────────────────────────────────────

class TestLoginDevice:

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.time.sleep")
    def test_success_immediate_approval(self, mock_sleep, mock_browser):
        """Device code issued, first poll returns tokens."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "data": {
                    "device_code": "dev-123",
                    "user_code": "ABCD-1234",
                    "verification_uri_complete": "https://auth.jana.earth/verify?code=ABCD-1234",
                    "interval": 1,
                }
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(200, json={
                "data": {
                    "access_token": "device-access",
                    "refresh_token": "device-refresh",
                }
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_device()
        assert client.access_token == "device-access"
        assert client.refresh_token == "device-refresh"
        mock_browser.assert_called_once()
        mock_sleep.assert_called_once_with(1)
        client.close()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.time.sleep")
    def test_pending_then_approved(self, mock_sleep, mock_browser):
        """Two polls: first pending, second approved."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "dev-456",
                "user_code": "XYZ",
                "verification_uri": "https://auth.jana.earth/verify",
                "interval": 2,
            })
        )
        call_count = {"n": 0}

        def token_handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(400, json={"error": "authorization_pending"})
            return httpx.Response(200, json={
                "access_token": "dev-tok", "refresh_token": "dev-ref",
            })

        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(side_effect=token_handler)

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_device()
        assert client.access_token == "dev-tok"
        assert mock_sleep.call_count == 2
        client.close()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.time.sleep")
    def test_slow_down_increases_interval(self, mock_sleep, mock_browser):
        """slow_down response increases the polling interval."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "dev-789",
                "verification_uri": "https://auth.jana.earth/verify",
                "interval": 3,
            })
        )
        call_count = {"n": 0}

        def token_handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(400, json={
                    "error": "slow_down", "interval": 10,
                })
            return httpx.Response(200, json={
                "access_token": "tok", "refresh_token": "ref",
            })

        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(side_effect=token_handler)

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_device()
        # First sleep(3), then slow_down sets interval=10, second sleep(10)
        assert mock_sleep.call_args_list[0][0][0] == 3
        assert mock_sleep.call_args_list[1][0][0] == 10
        client.close()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.time.sleep")
    def test_terminal_error(self, mock_sleep, mock_browser):
        """Terminal error (e.g. access_denied) raises EkoAuthenticationError."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "dev-err",
                "verification_uri": "https://auth.jana.earth/verify",
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(400, json={"error": "access_denied"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Device login failed"):
            client.login_device()
        client.close()

    @respx.mock
    def test_device_code_request_failure(self):
        """API error on device-code step raises EkoAuthenticationError."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(500, json={"error": "Internal"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Failed to request device code"):
            client.login_device()
        client.close()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open", side_effect=OSError("no browser"))
    @patch("eko_client.jwt_auth.time.sleep")
    def test_browser_open_failure_non_fatal(self, mock_sleep, mock_browser):
        """webbrowser.open failure is non-fatal — login continues."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "dev-nobrowser",
                "verification_uri": "https://auth.jana.earth/verify",
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(200, json={
                "access_token": "tok", "refresh_token": "ref",
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        client.login_device()
        assert client.access_token == "tok"
        client.close()


# ── login_device_async ──────────────────────────────────────────────────────

class TestLoginDeviceAsync:

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.asyncio.sleep")
    @pytest.mark.asyncio
    async def test_success_immediate(self, mock_sleep, mock_browser):
        """Async device login: immediate approval."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "data": {
                    "device_code": "adev-123",
                    "verification_uri_complete": "https://auth.jana.earth/verify?code=X",
                    "interval": 1,
                }
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(200, json={
                "data": {"access_token": "async-tok", "refresh_token": "async-ref"}
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        await client.login_device_async()
        assert client.access_token == "async-tok"
        assert client.refresh_token == "async-ref"
        await client.close_async()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.asyncio.sleep")
    @pytest.mark.asyncio
    async def test_pending_then_approved(self, mock_sleep, mock_browser):
        """Async: authorization_pending then success."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "adev-456",
                "verification_uri": "https://auth.jana.earth/verify",
                "interval": 2,
            })
        )
        call_count = {"n": 0}

        def handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(400, json={"error": "authorization_pending"})
            return httpx.Response(200, json={
                "access_token": "async-ok", "refresh_token": "async-r",
            })

        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(side_effect=handler)

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        await client.login_device_async()
        assert client.access_token == "async-ok"
        await client.close_async()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.asyncio.sleep")
    @pytest.mark.asyncio
    async def test_slow_down(self, mock_sleep, mock_browser):
        """Async: slow_down increases interval."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "adev-slow",
                "verification_uri": "https://auth.jana.earth/verify",
                "interval": 2,
            })
        )
        call_count = {"n": 0}

        def handler(request):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(400, json={"error": "slow_down", "interval": 15})
            return httpx.Response(200, json={
                "access_token": "tok", "refresh_token": "ref",
            })

        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(side_effect=handler)

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        await client.login_device_async()
        assert mock_sleep.call_args_list[0][0][0] == 2
        assert mock_sleep.call_args_list[1][0][0] == 15
        await client.close_async()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open")
    @patch("eko_client.jwt_auth.asyncio.sleep")
    @pytest.mark.asyncio
    async def test_terminal_error(self, mock_sleep, mock_browser):
        """Async: terminal error raises EkoAuthenticationError."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "adev-err",
                "verification_uri": "https://auth.jana.earth/verify",
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(400, json={"error": "expired_token"})
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Device login failed"):
            await client.login_device_async()
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_device_code_request_failure(self):
        """Async: API error on device-code step."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(500, json={"error": "Internal"})
        )
        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        with pytest.raises(EkoAuthenticationError, match="Failed to request device code"):
            await client.login_device_async()
        await client.close_async()

    @respx.mock
    @patch("eko_client.jwt_auth.webbrowser.open", side_effect=OSError("no browser"))
    @patch("eko_client.jwt_auth.asyncio.sleep")
    @pytest.mark.asyncio
    async def test_browser_open_failure_non_fatal(self, mock_sleep, mock_browser):
        """Async: browser failure is non-fatal."""
        respx.post(f"{BASE_URL}/api/auth/device-code/").mock(
            return_value=httpx.Response(200, json={
                "device_code": "adev-nobr",
                "verification_uri": "https://auth.jana.earth/verify",
            })
        )
        respx.post(f"{BASE_URL}/api/auth/device-token/").mock(
            return_value=httpx.Response(200, json={
                "access_token": "tok", "refresh_token": "ref",
            })
        )

        client = EkoUserClient(base_url=BASE_URL, token="tmp")
        await client.login_device_async()
        assert client.access_token == "tok"
        await client.close_async()
