"""Live-API contract tests for Climate TRACE methods.

These tests hit the real Climate TRACE endpoints on
``api-test.jana.earth`` and assert that the response shape and
filterable params match the unit-level contract tests in
``tests/contract/test_climatetrace.py``.

They are intentionally minimal — one probe per representative endpoint
— so the nightly run completes in seconds and does not stress the dev
cluster. Deeper coverage stays in the unit contract suite.

Skipped unless ``-m integration`` is passed AND
``EKO_TEST_USER`` + ``EKO_TEST_PASSWORD`` are set.
"""

from __future__ import annotations

import pytest


pytestmark = pytest.mark.integration


class TestClimateTraceLive:
    """Smoke-level live contract for CT endpoints."""

    async def test_sectors_returns_paginated_envelope(self, live_client):
        """Live ``/sectors/`` returns a page_or_offset envelope."""
        result = await live_client.get_climatetrace_sectors_async(limit=2)
        assert "results" in result, "expected paginated envelope"
        assert isinstance(result["results"], list)
        # Page-or-offset endpoints carry a count
        assert "count" in result
        assert isinstance(result["count"], int)

    async def test_assets_returns_cursor_envelope(self, live_client):
        """Live ``/assets/`` returns a cursor envelope (no count)."""
        result = await live_client.get_climatetrace_assets_async(limit=2)
        assert "results" in result
        assert "next" in result
        # Cursor pagination omits ``count``
        assert result.get("count") is None

    async def test_emissions_gas_filter_returns_200(self, live_client):
        """Live ``/emissions/?gas=co2`` returns 200 (server accepts the
        ``gas`` filter)."""
        result = await live_client.get_climatetrace_emissions_async(
            gas="co2", limit=2,
        )
        assert "results" in result

    async def test_emissions_unknown_param_returns_400(self, live_client):
        """Live ``/emissions/?gas_type=co2`` returns 400 with
        ``unknown_params`` in the payload (post-Phase-2A strict mode).

        This is the single most important live-contract assertion: it
        proves the server-side filterset hardening is still in effect.
        If a future server regression silently accepts ``gas_type``
        again, this test catches it.
        """
        from eko_client.exceptions import EkoAPIError

        with pytest.raises(EkoAPIError) as exc_info:
            await live_client._request_async(
                "GET",
                "/api/v1/data-sources/climatetrace/emissions/",
                params={"gas_type": "co2"},
            )
        assert exc_info.value.status_code == 400
        assert "unknown_params" in exc_info.value.response_data
