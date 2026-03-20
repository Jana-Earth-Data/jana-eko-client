"""
JWT-based authentication for the Eko Client.

Supports two login flows:
  - Password:    login_password(email, password)
  - Device Code: login_device()  (OAuth 2.0 RFC 8628 — like `aws sso login`)

After a successful login, `access_token` and `refresh_token` are stored on the
instance.  `_get_headers()` is overridden so every subsequent request sends
`Authorization: Bearer <access_token>` instead of the DRF `Token` scheme used
by the base client.
"""

import asyncio
import logging
import time
from typing import Optional

from .exceptions import EkoAPIError, EkoAuthenticationError, EkoSessionExpiredError

logger = logging.getLogger(__name__)

_DEVICE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"


class JwtAuthMixin:
    """
    Mixin that adds JWT (Bearer) authentication to BaseEkoClient.

    MRO note: place this mixin *before* BaseEkoClient in the class definition:

        class MyClient(JwtAuthMixin, BaseEkoClient): ...

    Constructor parameters
    ----------------------
    client_id : str
        Identifier sent to the device-code and device-token endpoints.
        Defaults to ``"jana-sdk"``.

    All other parameters are forwarded to BaseEkoClient.
    """

    def __init__(self, *args, client_id: str = "jana-sdk", **kwargs):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.client_id: str = client_id
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------
    # Header override — Bearer scheme replaces DRF Token scheme
    # ------------------------------------------------------------------

    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif getattr(self, "token", None):
            # Fallback: DRF token set directly on the client (management APIs)
            headers["Authorization"] = f"Token {self.token}"
        return headers

    # ------------------------------------------------------------------
    # Password login
    # ------------------------------------------------------------------

    def login_password(self, email: str, password: str) -> None:
        """
        Authenticate with email + password and store JWT tokens.

        POSTs to ``/api/auth/login/`` and stores the returned
        ``access_token`` / ``refresh_token`` on the instance.

        Args:
            email:    User email address.
            password: User password.

        Raises:
            EkoAuthenticationError: If the server rejects the credentials or
                the response is missing an ``access_token``.
        """
        try:
            response = self._request_sync(
                "POST",
                "/api/auth/login/",
                json_data={"email": email, "password": password},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Login failed: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        data = response.get("data") or response
        access_token = data.get("access_token")
        if not access_token:
            raise EkoAuthenticationError("No access_token received from login response.")

        self.access_token = access_token
        self.refresh_token = data.get("refresh_token")
        logger.info("Password login successful.")

    async def login_password_async(self, email: str, password: str) -> None:
        """Async version of :meth:`login_password`."""
        try:
            response = await self._request_async(
                "POST",
                "/api/auth/login/",
                json_data={"email": email, "password": password},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Login failed: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        data = response.get("data") or response
        access_token = data.get("access_token")
        if not access_token:
            raise EkoAuthenticationError("No access_token received from login response.")

        self.access_token = access_token
        self.refresh_token = data.get("refresh_token")
        logger.info("Password login successful.")

    # ------------------------------------------------------------------
    # Device Code flow  (RFC 8628)
    # ------------------------------------------------------------------

    def login_device(self) -> None:
        """
        Authenticate using the OAuth 2.0 Device Code flow (RFC 8628).

        Flow (SDK side)
        ---------------
        1. POST /api/auth/device-code/  — get a device_code + user_code (no auth needed).
        2. Open the verification URL in the browser so the user can log in on the
           Jana web app and approve the request.  The SDK has no token at this point —
           the web app handles login + approval independently.
        3. Poll /api/auth/device-token/ (no auth needed) until the web app approves.
           On approval the server returns { access_token, refresh_token }.
           These are stored on the instance and used for all subsequent API calls
           as ``Authorization: Bearer <access_token>``.

        Server-side ``slow_down`` responses are handled automatically.

        Raises:
            EkoAuthenticationError: If the device code cannot be issued, the
                user denies the request, the code expires, or any other
                terminal error is returned by the server.
        """
        # Step 1 — request device code (public endpoint, no auth)
        try:
            r = self._request_sync(
                "POST",
                "/api/auth/device-code/",
                json_data={"client_id": self.client_id},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Failed to request device code: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        issue_data = r.get("data") or r
        device_code = issue_data["device_code"]
        interval: int = issue_data.get("interval", 5)
        verify_url: str = (
            issue_data.get("verification_uri_complete")
            or issue_data.get("verification_uri", "")
        )

        # Step 2 — prompt user to log in and approve via the Jana web app
        # Do not auto-open: user may need to open in private/incognito window for a
        # fresh login (avoids cached session that skips the login form).
        print(
            f"\nOpen the following URL in your browser to log in and authorize this device:\n"
            f"  {verify_url}\n"
            f"\nTip: Open in a private/incognito window if you need to log in fresh.\n"
            f"Waiting for you to approve in the browser..."
        )

        # Step 3 — poll device-token (public endpoint, no auth) until approved.
        # The access_token is returned here once the user approves in the browser.
        while True:
            time.sleep(interval)

            poll_response: dict = {}
            try:
                poll_response = self._request_sync(
                    "POST",
                    "/api/auth/device-token/",
                    json_data={
                        "grant_type": _DEVICE_GRANT_TYPE,
                        "device_code": device_code,
                        "client_id": self.client_id,
                    },
                )
            except EkoAPIError as exc:
                # device-token returns HTTP 400 for all non-success states (RFC 8628 §3.5)
                poll_response = exc.response_data or {}

            poll_data = poll_response.get("data") or poll_response

            if "access_token" in poll_data:
                self.access_token = poll_data["access_token"]
                self.refresh_token = poll_data.get("refresh_token")
                print("Authorization successful. You are now logged in.")
                logger.info("Device login successful.")
                return

            error = poll_response.get("error") or poll_data.get("error")

            if error == "authorization_pending":
                continue

            if error == "slow_down":
                interval = poll_data.get("interval", interval + 5)
                continue

            raise EkoAuthenticationError(f"Device login failed: {error}")

    async def login_device_async(self) -> None:
        """Async version of :meth:`login_device`."""
        # Step 1 — request device code (public endpoint, no auth)
        try:
            r = await self._request_async(
                "POST",
                "/api/auth/device-code/",
                json_data={"client_id": self.client_id},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Failed to request device code: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        issue_data = r.get("data") or r
        device_code = issue_data["device_code"]
        interval: int = issue_data.get("interval", 5)
        verify_url: str = (
            issue_data.get("verification_uri_complete")
            or issue_data.get("verification_uri", "")
        )

        # Step 2 — prompt user to log in and approve via the Jana web app
        # Do not auto-open: user may need to open in private/incognito window for a
        # fresh login (avoids cached session that skips the login form).
        print(
            f"\nOpen the following URL in your browser to log in and authorize this device:\n"
            f"  {verify_url}\n"
            f"\nTip: Open in a private/incognito window if you need to log in fresh.\n"
            f"Waiting for you to approve in the browser..."
        )

        # Step 3 — poll device-token (public endpoint, no auth) until approved.
        # The access_token is returned here once the user approves in the browser.
        while True:
            await asyncio.sleep(interval)

            poll_response: dict = {}
            try:
                poll_response = await self._request_async(
                    "POST",
                    "/api/auth/device-token/",
                    json_data={
                        "grant_type": _DEVICE_GRANT_TYPE,
                        "device_code": device_code,
                        "client_id": self.client_id,
                    },
                )
            except EkoAPIError as exc:
                # device-token returns HTTP 400 for all non-success states (RFC 8628 §3.5)
                poll_response = exc.response_data or {}

            poll_data = poll_response.get("data") or poll_response

            if "access_token" in poll_data:
                self.access_token = poll_data["access_token"]
                self.refresh_token = poll_data.get("refresh_token")
                print("Authorization successful. You are now logged in.")
                logger.info("Device login successful.")
                return

            error = poll_response.get("error") or poll_data.get("error")

            if error == "authorization_pending":
                continue

            if error == "slow_down":
                interval = poll_data.get("interval", interval + 5)
                continue

            raise EkoAuthenticationError(f"Device login failed: {error}")

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    def refresh_jwt(self) -> None:
        """
        Exchange the stored refresh token for a new access token.

        POSTs ``{"refresh_token": ...}`` to ``/api/auth/refresh/`` and updates
        ``self.access_token`` (and ``self.refresh_token`` if the server rotates
        it).

        Raises:
            EkoAuthenticationError: If no refresh token is stored or the
                server rejects the request.
        """
        if not self.refresh_token:
            raise EkoAuthenticationError(
                "No refresh token stored. Call login_password() or login_device() first."
            )

        try:
            r = self._request_sync(
                "POST",
                "/api/auth/refresh/",
                json_data={"refresh_token": self.refresh_token},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Token refresh failed: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        data = r.get("data") or r
        self.access_token = data["access_token"]
        if "refresh_token" in data:
            self.refresh_token = data["refresh_token"]

    # Alias matching the private name used in the implementation plan (§10)
    _refresh_jwt = refresh_jwt

    async def refresh_jwt_async(self) -> None:
        """Async version of :meth:`refresh_jwt`."""
        if not self.refresh_token:
            raise EkoAuthenticationError(
                "No refresh token stored. Call login_password_async() or login_device_async() first."
            )

        try:
            r = await self._request_async(
                "POST",
                "/api/auth/refresh/",
                json_data={"refresh_token": self.refresh_token},
            )
        except EkoAPIError as exc:
            raise EkoAuthenticationError(
                f"Token refresh failed: {exc.message}",
                status_code=exc.status_code,
                response_data=exc.response_data,
            ) from exc

        data = r.get("data") or r
        self.access_token = data["access_token"]
        if "refresh_token" in data:
            self.refresh_token = data["refresh_token"]

    # ------------------------------------------------------------------
    # Auto-refresh request wrappers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_auth_failure(exc: Exception) -> bool:
        """Check if an exception represents an authentication failure.

        Matches both 401 (``EkoAuthenticationError``) and 403 responses whose
        body contains a JWT-related error message.  The server returns 403
        (not 401) for expired/invalid JWTs due to DRF's ``AuthenticationFailed``
        interaction with ``AllowAny`` permission classes.
        """
        if isinstance(exc, EkoAuthenticationError):
            return True
        if isinstance(exc, EkoAPIError) and exc.status_code == 403:
            msg = str(exc.message).lower() if exc.message else ""
            data = exc.response_data or {}
            detail = str(data.get("detail", "")).lower()
            return any(
                kw in msg or kw in detail
                for kw in ("token", "jwt", "expired", "credentials")
            )
        return False

    def _request_sync(self, method: str, endpoint: str, **kwargs):
        """Override: on auth failure (401 or JWT-related 403), refresh and retry once.

        If the refresh token is also expired/invalid, raises
        ``EkoSessionExpiredError`` so callers can distinguish "re-login
        needed" from transient auth errors.
        """
        try:
            return super()._request_sync(method, endpoint, **kwargs)
        except (EkoAuthenticationError, EkoAPIError) as exc:
            if not self._is_auth_failure(exc) or getattr(self, "_refreshing", False):
                raise
            if not self.refresh_token:
                raise EkoSessionExpiredError() from exc
            self._refreshing = True
            try:
                self.refresh_jwt()
            except (EkoAuthenticationError, EkoAPIError):
                self.access_token = None
                self.refresh_token = None
                raise EkoSessionExpiredError() from exc
            finally:
                self._refreshing = False
            return super()._request_sync(method, endpoint, **kwargs)

    async def _request_async(self, method: str, endpoint: str, **kwargs):
        """Async override: on auth failure, refresh and retry once.

        If the refresh token is also expired/invalid, raises
        ``EkoSessionExpiredError``.
        """
        try:
            return await super()._request_async(method, endpoint, **kwargs)
        except (EkoAuthenticationError, EkoAPIError) as exc:
            if not self._is_auth_failure(exc) or getattr(self, "_refreshing", False):
                raise
            if not self.refresh_token:
                raise EkoSessionExpiredError() from exc
            self._refreshing = True
            try:
                await self.refresh_jwt_async()
            except (EkoAuthenticationError, EkoAPIError):
                self.access_token = None
                self.refresh_token = None
                raise EkoSessionExpiredError() from exc
            finally:
                self._refreshing = False
            return await super()._request_async(method, endpoint, **kwargs)

    # ------------------------------------------------------------------
    # User info
    # ------------------------------------------------------------------

    def get_user_info(self) -> dict:
        """Return the authenticated user's profile from ``/api/auth/user/``.

        Unwraps ``data`` if the API returns ``{"data": {"username": ..., "email": ...}}``,
        so callers can use ``user_info.get("username")`` / ``user_info.get("email")``
        regardless of response shape.
        """
        response = self._request_sync("GET", "/api/auth/user/")
        return response.get("data") or response

    async def get_user_info_async(self) -> dict:
        """Async version of :meth:`get_user_info`."""
        response = await self._request_async("GET", "/api/auth/user/")
        return response.get("data") or response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_authenticated(self) -> bool:
        """Return ``True`` if an access token is currently stored."""
        return bool(self.access_token)
