"""Tests for eko_client.exceptions — all custom exception classes."""

import pytest
from eko_client.exceptions import (
    EkoClientError,
    EkoAuthenticationError,
    EkoAPIError,
    EkoRateLimitError,
    EkoSessionExpiredError,
    EkoNotFoundError,
)


class TestEkoClientError:

    def test_message_stored(self):
        err = EkoClientError("something broke")
        assert err.message == "something broke"
        assert str(err) == "something broke"

    def test_defaults(self):
        err = EkoClientError("x")
        assert err.status_code is None
        assert err.response_data == {}

    def test_custom_fields(self):
        err = EkoClientError("x", status_code=500, response_data={"k": "v"})
        assert err.status_code == 500
        assert err.response_data == {"k": "v"}

    def test_is_exception(self):
        with pytest.raises(EkoClientError):
            raise EkoClientError("boom")


class TestEkoAuthenticationError:

    def test_inherits_client_error(self):
        assert issubclass(EkoAuthenticationError, EkoClientError)

    def test_message(self):
        err = EkoAuthenticationError("bad creds")
        assert err.message == "bad creds"


class TestEkoAPIError:

    def test_inherits_client_error(self):
        assert issubclass(EkoAPIError, EkoClientError)

    def test_requires_status_code(self):
        err = EkoAPIError("server error", status_code=500)
        assert err.status_code == 500

    def test_response_data(self):
        err = EkoAPIError("x", status_code=400, response_data={"detail": "bad"})
        assert err.response_data == {"detail": "bad"}


class TestEkoRateLimitError:

    def test_inherits_api_error(self):
        assert issubclass(EkoRateLimitError, EkoAPIError)

    def test_status_code_is_429(self):
        err = EkoRateLimitError("slow down")
        assert err.status_code == 429

    def test_retry_after(self):
        err = EkoRateLimitError("slow down", retry_after=30)
        assert err.retry_after == 30

    def test_retry_after_default_none(self):
        err = EkoRateLimitError("slow down")
        assert err.retry_after is None


class TestEkoSessionExpiredError:

    def test_inherits_authentication_error(self):
        assert issubclass(EkoSessionExpiredError, EkoAuthenticationError)

    def test_default_message(self):
        err = EkoSessionExpiredError()
        assert "Session expired" in err.message

    def test_custom_message(self):
        err = EkoSessionExpiredError("custom msg")
        assert err.message == "custom msg"


class TestEkoNotFoundError:

    def test_inherits_api_error(self):
        assert issubclass(EkoNotFoundError, EkoAPIError)

    def test_status_code_is_404(self):
        err = EkoNotFoundError()
        assert err.status_code == 404

    def test_default_message(self):
        err = EkoNotFoundError()
        assert err.message == "Resource not found"

    def test_custom_message(self):
        err = EkoNotFoundError("no such thing")
        assert err.message == "no such thing"


class TestExceptionHierarchy:
    """Verify that except clauses catch the right subclasses."""

    def test_catch_client_error_catches_auth(self):
        with pytest.raises(EkoClientError):
            raise EkoAuthenticationError("x")

    def test_catch_client_error_catches_api(self):
        with pytest.raises(EkoClientError):
            raise EkoAPIError("x", status_code=500)

    def test_catch_api_error_catches_rate_limit(self):
        with pytest.raises(EkoAPIError):
            raise EkoRateLimitError("x")

    def test_catch_api_error_catches_not_found(self):
        with pytest.raises(EkoAPIError):
            raise EkoNotFoundError("x")

    def test_catch_auth_error_catches_session_expired(self):
        with pytest.raises(EkoAuthenticationError):
            raise EkoSessionExpiredError()
