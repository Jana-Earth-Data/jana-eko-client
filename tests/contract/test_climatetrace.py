"""Climate TRACE wire-contract tests.

These tests pin the request/response contract for CT methods on
``EkoUserClient``. They run against ``respx`` mocks (no network) and
assert on:

* URL path the client builds
* Exact set of query params on the wire
* Correct parsing of the three response shapes recorded in Step-7
  (``page_or_offset``, ``cursor``, ``flat-dict``)

As of v0.3.0 (jana-eko-client #34), the client kwarg ``country_code``
was renamed to ``country_iso3`` on every Climate TRACE method, matching
the server's canonical filter field name from Jana #161 Phase 2A. The
rename is a hard break — passing the legacy name raises ``TypeError``.
The ``test_emissions_legacy_country_code_kwarg_raises_typeerror`` test
pins that contract so any future re-introduction of a backwards-compat
alias forces an explicit test update.

Note on ``sector_name``: live probing in this PR confirmed the server
canonical name on the Climate TRACE FilterSet is still ``sector_name``
(not ``sector``). The original audit assumed otherwise; the client
kwarg therefore stays as ``sector_name`` to match the wire. Tracking
adding a ``sector`` alias on the server in a follow-up Jana issue.

The fixture seed (``STEP7_FIXTURES``) is loaded from the audit artifact
``eko_step7_probe_results_20260428.json`` so we can always trace a test
to a concrete live-probe observation.
"""

from __future__ import annotations

import httpx
import pytest

from .conftest import (
    STEP7_FIXTURES,
    assert_query_params,
    make_paginated_response,
)


# Shared base — matches conftest.user_client_dual fixture
API_BASE_URL = "https://api-test.jana.earth"


# ---------------------------------------------------------------------------
# Pagination-shape contract
# ---------------------------------------------------------------------------

class TestClimateTracePaginationShapes:
    """Each CT endpoint must use the pagination shape Step-7 observed."""

    async def test_sectors_returns_page_or_offset(
        self, mock_api, user_client_dual
    ):
        """ct-sectors → page_or_offset, count=26."""
        fixture = STEP7_FIXTURES["ct-sectors"]
        assert fixture["shape"] == "page_or_offset"

        body = make_paginated_response(
            "page_or_offset",
            results=[{"id": 1, "name": "power"}],
            count=fixture["count"],
        )
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/sectors/"
        ).mock(return_value=httpx.Response(200, json=body))

        result = await user_client_dual.get_climatetrace_sectors_async()

        assert route.called
        assert result["count"] == 26
        assert result["results"] == [{"id": 1, "name": "power"}]

    async def test_assets_returns_cursor(self, mock_api, user_client_dual):
        """ct-assets → cursor (no count)."""
        fixture = STEP7_FIXTURES["ct-assets"]
        assert fixture["shape"] == "cursor"

        body = make_paginated_response(
            "cursor",
            results=[{"id": 42, "name": "Plant X"}],
            next_url=f"{API_BASE_URL}/api/v1/data-sources/climatetrace/assets/?cursor=abc",
        )
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/assets/"
        ).mock(return_value=httpx.Response(200, json=body))

        result = await user_client_dual.get_climatetrace_assets_async()

        assert route.called
        # Cursor responses do not carry a count
        assert "count" not in result or result.get("count") is None
        assert result["next"].endswith("cursor=abc")
        assert result["results"][0]["name"] == "Plant X"

    async def test_emissions_returns_cursor(self, mock_api, user_client_dual):
        """ct-emissions → cursor."""
        fixture = STEP7_FIXTURES["ct-emissions"]
        assert fixture["shape"] == "cursor"

        body = make_paginated_response(
            "cursor",
            results=[{"id": 1, "co2e_100yr": 12345.6}],
            next_url=None,
        )
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(200, json=body))

        result = await user_client_dual.get_climatetrace_emissions_async()

        assert route.called
        assert result["next"] is None
        assert result["results"][0]["co2e_100yr"] == 12345.6


# ---------------------------------------------------------------------------
# Query-param contract — these are the tests that lock in the filter names
# ---------------------------------------------------------------------------

class TestClimateTraceQueryParams:
    """Pin which kwarg names go on the wire as which query params.

    These are the tests that catch silent kwarg renames. If a CT
    filterset on the server changes (e.g. ``country_code`` → ``country_iso3``)
    and the client is not updated, the corresponding test here turns red.
    """

    async def test_emissions_gas_kwarg_goes_on_wire_as_gas(
        self, mock_api, user_client_dual
    ):
        """The client kwarg ``gas`` is sent as the ``gas`` query param.

        Confirmed correct against the live API by Step-7 probe
        ``ct-emissions-gas-co2`` (status 200).
        """
        body = make_paginated_response("cursor", results=[])
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(200, json=body))

        await user_client_dual.get_climatetrace_emissions_async(gas="co2")

        assert route.called
        assert_query_params(route.calls.last.request, {"gas": "co2"})

    async def test_emissions_legacy_country_code_kwarg_raises_typeerror(
        self, user_client_dual
    ):
        """Legacy kwarg ``country_code`` must raise ``TypeError`` post-#34.

        v0.3.0 renamed ``country_code`` → ``country_iso3`` on every CT
        method (jana-eko-client #34). Option A — hard break — was chosen
        deliberately over a deprecation shim, so any caller still passing
        ``country_code`` must surface immediately as ``TypeError`` rather
        than silently sending it on the wire (where the server would
        either silently drop it pre-#161, or 400 post-Phase-2A).

        This test pins the breaking-change behaviour so that anyone who
        later restores a backwards-compat alias has to update this test
        (and explain why they regressed the canonical-only contract).
        """
        with pytest.raises(TypeError):
            await user_client_dual.get_climatetrace_emissions_async(
                country_code="USA"  # legacy kwarg, removed in v0.3.0
            )

    async def test_emissions_country_iso3_kwarg_goes_on_wire_as_country_iso3(
        self, mock_api, user_client_dual
    ):
        """v0.3.0 contract: ``country_iso3`` kwarg → ``country_iso3`` query param.

        Confirmed against the live API by the #161 Phase-2A migration
        (server now requires the canonical name; the old ``country_code``
        alias was retired). This test was previously xfail-strict against
        TypeError — it now passes naturally because v0.3.0 of this client
        renamed the kwarg.
        """
        body = make_paginated_response("cursor", results=[])
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(200, json=body))

        await user_client_dual.get_climatetrace_emissions_async(
            country_iso3="USA"
        )

        assert route.called
        assert_query_params(
            route.calls.last.request, {"country_iso3": "USA"}
        )

    async def test_emissions_sector_name_kwarg_goes_on_wire_as_sector_name(
        self, mock_api, user_client_dual
    ):
        """``sector_name`` kwarg → ``sector_name`` query param.

        Live probing during #34 confirmed the server's canonical filter
        on the Climate TRACE FilterSet is still ``sector_name`` (not
        ``sector``). The client therefore keeps ``sector_name`` as the
        kwarg to match the wire. If a future server release adds
        ``sector`` as an alias, this test should be updated alongside.
        """
        body = make_paginated_response("cursor", results=[])
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(200, json=body))

        await user_client_dual.get_climatetrace_emissions_async(
            sector_name="power"
        )

        assert route.called
        assert_query_params(
            route.calls.last.request, {"sector_name": "power"}
        )

    async def test_emissions_drops_none_kwargs_from_wire(
        self, mock_api, user_client_dual
    ):
        """``None`` kwargs must never reach the wire.

        DRF filtersets treat the literal string ``"None"`` as a value, so
        if a client serialised ``country_iso3=None`` it would silently
        filter to country code ``"None"`` (returning zero rows).
        """
        body = make_paginated_response("cursor", results=[])
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(200, json=body))

        await user_client_dual.get_climatetrace_emissions_async(
            gas="co2",
            country_iso3=None,
            date_from=None,
        )

        assert route.called
        # Only ``gas`` should be on the wire; ``country_iso3`` and
        # ``date_from`` were ``None`` and must be dropped.
        assert_query_params(route.calls.last.request, {"gas": "co2"})

    async def test_assets_sector_id_kwarg_goes_on_wire_as_sector_id(
        self, mock_api, user_client_dual
    ):
        """``sector_id`` kwarg → ``sector_id`` param (server accepts both
        ``sector`` and ``sector_id`` post-Phase-2C, but the client should
        send the canonical name)."""
        body = make_paginated_response("cursor", results=[])
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/assets/"
        ).mock(return_value=httpx.Response(200, json=body))

        await user_client_dual.get_climatetrace_assets_async(sector_id=3)

        assert route.called
        assert_query_params(
            route.calls.last.request, {"sector_id": "3"}
        )


# ---------------------------------------------------------------------------
# Flat-dict (non-paginated) contract
# ---------------------------------------------------------------------------

class TestClimateTraceFlatDictResponses:
    """Aggregation endpoints return a flat dict, not a paginated envelope."""

    async def test_emissions_totals_returns_flat_dict(
        self, mock_api, user_client_dual
    ):
        """``/emissions/totals/`` → flat dict with SUM aggregates."""
        flat = {
            "total_co2e": 5.7e12,
            "total_co2": 4.9e12,
            "total_ch4": 8.1e10,
            "total_n2o": 2.4e9,
            "record_count": 9876543,
            "avg_co2e": 583.4,
        }
        body = make_paginated_response("flat-dict", flat_payload=flat)
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/totals/"
        ).mock(return_value=httpx.Response(200, json=body))

        result = await user_client_dual.get_climatetrace_emissions_totals_async()

        assert route.called
        assert result == flat
        # No paginated envelope keys
        assert "results" not in result
        assert "next" not in result

    async def test_emissions_date_range_returns_flat_dict(
        self, mock_api, user_client_dual
    ):
        """``/emissions/date_range/`` → flat dict with min/max dates."""
        flat = {
            "earliest_date": "2015-01-01",
            "latest_date": "2024-12-31",
            "total_records": 9876543,
        }
        body = make_paginated_response("flat-dict", flat_payload=flat)
        route = mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/date_range/"
        ).mock(return_value=httpx.Response(200, json=body))

        result = await user_client_dual.get_climatetrace_emissions_date_range_async()

        assert route.called
        assert result == flat


# ---------------------------------------------------------------------------
# Strict-server (400) handling — Phase 2A migrated endpoints
# ---------------------------------------------------------------------------

class TestClimateTraceStrictServer:
    """After Jana #161 Phase 2A, CT emissions FilterSet rejects unknown
    params with a 400 + ``unknown_params`` payload. The client must
    surface this as ``EkoAPIError``.
    """

    async def test_emissions_unknown_param_raises_eko_api_error(
        self, mock_api, user_client_dual
    ):
        """Server returns 400 ``{"unknown_params": [...]}`` → client raises."""
        from eko_client.exceptions import EkoAPIError

        # This mirrors the response shape of Step-7 probe
        # ``ct-emissions-gas_type-co2-BUGGY`` (2026-04-28), updated for
        # the post-#161-Phase-2A canonical filter names. Live probing
        # during #34 confirmed the server's actual ``allowed_params``
        # includes both ``country_code`` and ``country_iso3`` and still
        # uses ``sector_name`` (not ``sector``).
        error_body = {
            "detail": "Unknown query parameter(s): gas_type",
            "unknown_params": ["gas_type"],
            "allowed_params": [
                "asset_id", "sector_id", "sector_name",
                "country_code", "country_iso3",
                "gas", "date_from", "date_to", "limit", "offset",
            ],
        }
        mock_api.get(
            f"{API_BASE_URL}/api/v1/data-sources/climatetrace/emissions/"
        ).mock(return_value=httpx.Response(400, json=error_body))

        # Build a raw request because the typed method doesn't expose
        # an unknown kwarg passthrough — we want to prove that *if* the
        # wire ever carries an unknown param, the client surfaces 400.
        with pytest.raises(EkoAPIError) as exc_info:
            await user_client_dual._request_async(
                "GET",
                "/api/v1/data-sources/climatetrace/emissions/",
                params={"gas_type": "co2"},
            )

        # Server response is preserved on the exception
        assert exc_info.value.status_code == 400
        assert "unknown_params" in exc_info.value.response_data
        assert exc_info.value.response_data["unknown_params"] == ["gas_type"]
