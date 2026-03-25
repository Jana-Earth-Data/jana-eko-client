"""Tests for eko_client.user_client — EkoUserClient endpoint methods.

Strategy: Each async method is the source of truth (the sync version is
auto-generated). We test every async method with respx, and spot-check
a few sync wrappers to verify auto_sync_wrapper works end-to-end.
"""

import pytest
import httpx
import respx
from datetime import datetime

from eko_client.user_client import EkoUserClient

BASE_URL = "https://test.jana.earth"
OK = {"results": [{"id": 1}], "count": 1}


def _client():
    return EkoUserClient(base_url=BASE_URL, token="tok")


# ── Core Data Access ─────────────────────────────────────────────────────────

class TestGetData:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_data_async_minimal(self):
        respx.get(f"{BASE_URL}/api/v1/esg/data/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_data_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_data_async_all_params(self):
        route = respx.get(f"{BASE_URL}/api/v1/esg/data/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        await client.get_data_async(
            sources=["openaq", "edgar"],
            location_bbox=[80, 26, 88, 30],
            location_point=[85.3, 27.7],
            radius_km=50.0,
            country_codes=["NPL"],
            date_from=datetime(2024, 1, 1),
            date_to="2024-12-31",
            temporal_resolution="daily",
            parameters=["pm25"],
            quality_threshold=80,
            include_flags=True,
            limit=100,
            offset=0,
        )
        assert route.called
        await client.close_async()

    @respx.mock
    def test_get_data_sync(self):
        respx.get(f"{BASE_URL}/api/v1/esg/data/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_data(sources=["openaq"], limit=10)
        assert result == OK
        client.close()


class TestGetAggregations:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/aggregations/").mock(
            return_value=httpx.Response(200, json={"aggregations": {}})
        )
        client = _client()
        result = await client.get_aggregations_async("daily")
        assert "aggregations" in result
        await client.close_async()


# ── Analytics & Intelligence ─────────────────────────────────────────────────

class TestGetCorrelations:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/correlations/").mock(
            return_value=httpx.Response(200, json={"correlations": {}})
        )
        client = _client()
        result = await client.get_correlations_async(sources=["openaq", "edgar"])
        assert "correlations" in result
        await client.close_async()


class TestGetTrends:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/trends/").mock(
            return_value=httpx.Response(200, json={"trends": []})
        )
        client = _client()
        result = await client.get_trends_async(
            sources=["openaq"],
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 6, 30),
        )
        assert "trends" in result
        await client.close_async()


# ── Quality & Monitoring ─────────────────────────────────────────────────────

class TestGetQuality:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/quality/").mock(
            return_value=httpx.Response(200, json={"overall_quality": {}})
        )
        client = _client()
        result = await client.get_quality_async(
            date_from=datetime(2024, 1, 1),
        )
        assert "overall_quality" in result
        await client.close_async()


class TestGetAlerts:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/alerts/").mock(
            return_value=httpx.Response(200, json={"alerts": []})
        )
        client = _client()
        result = await client.get_alerts_async(
            alert_types=["quality"],
            date_from=datetime(2024, 1, 1),
        )
        assert "alerts" in result
        await client.close_async()


# ── Geographic & Spatial ─────────────────────────────────────────────────────

class TestGetGeojson:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/geojson/").mock(
            return_value=httpx.Response(200, json={"type": "FeatureCollection"})
        )
        client = _client()
        result = await client.get_geojson_async(sources=["openaq"])
        assert result["type"] == "FeatureCollection"
        await client.close_async()


class TestGetLocations:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/esg/locations/").mock(
            return_value=httpx.Response(200, json={"locations": []})
        )
        client = _client()
        result = await client.get_locations_async(limit=10)
        assert "locations" in result
        await client.close_async()


# ── Export & Bulk Access ─────────────────────────────────────────────────────

class TestExports:

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_export(self):
        respx.post(f"{BASE_URL}/api/v1/esg/exports/").mock(
            return_value=httpx.Response(201, json={"export_id": "abc"})
        )
        client = _client()
        result = await client.create_export_async(
            format="csv",
            query={"sources": ["openaq"]},
            compression="gzip",
            chunk_size=5000,
            email_notification="test@test.com",
            expires_in_hours=24,
        )
        assert result["export_id"] == "abc"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_export_status(self):
        respx.get(f"{BASE_URL}/api/v1/esg/exports/abc/status/").mock(
            return_value=httpx.Response(200, json={"status": "completed"})
        )
        client = _client()
        result = await client.get_export_status_async("abc")
        assert result["status"] == "completed"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_download_export(self):
        respx.get(f"{BASE_URL}/api/v1/esg/exports/abc/download/").mock(
            return_value=httpx.Response(200, content=b"csv,data,here")
        )
        client = _client()
        content = await client.download_export_async("abc")
        assert content == b"csv,data,here"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_download_export_error(self):
        """Error response on download triggers _handle_response (line 491)."""
        from eko_client.exceptions import EkoNotFoundError
        respx.get(f"{BASE_URL}/api/v1/esg/exports/bad/download/").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )
        client = _client()
        with pytest.raises(EkoNotFoundError):
            await client.download_export_async("bad")
        await client.close_async()


# ── Metadata & Definitions ───────────────────────────────────────────────────

class TestDefinitions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_definitions(self):
        respx.get(f"{BASE_URL}/api/v1/esg/definitions/").mock(
            return_value=httpx.Response(200, json={"categories": []})
        )
        client = _client()
        result = await client.get_definitions_async()
        assert "categories" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_parameter_definitions(self):
        respx.get(f"{BASE_URL}/api/v1/esg/parameters/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_parameter_definitions_async(sources=["openaq"])
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_unit_definitions(self):
        respx.get(f"{BASE_URL}/api/v1/esg/definitions/units/").mock(
            return_value=httpx.Response(200, json={"units": []})
        )
        client = _client()
        result = await client.get_unit_definitions_async()
        assert "units" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_source_definitions(self):
        respx.get(f"{BASE_URL}/api/v1/esg/definitions/sources/").mock(
            return_value=httpx.Response(200, json={"sources": []})
        )
        client = _client()
        result = await client.get_source_definitions_async()
        assert "sources" in result
        await client.close_async()


# ── System & Health ──────────────────────────────────────────────────────────

class TestSystemHealth:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_health(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = _client()
        result = await client.get_health_async()
        assert result["status"] == "ok"
        await client.close_async()

    @respx.mock
    def test_get_health_sync(self):
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = _client()
        result = client.get_health()
        assert result["status"] == "ok"
        client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_system_health(self):
        respx.get(f"{BASE_URL}/api/v1/esg/system-health/").mock(
            return_value=httpx.Response(200, json={"system_status": {}})
        )
        client = _client()
        result = await client.get_system_health_async()
        assert "system_status" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_summary(self):
        respx.get(f"{BASE_URL}/api/v1/esg/summary/").mock(
            return_value=httpx.Response(200, json={"platform_overview": {}})
        )
        client = _client()
        result = await client.get_summary_async()
        assert "platform_overview" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sectors(self):
        respx.get(f"{BASE_URL}/api/v1/esg/sectors/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_sectors_async(
            sources=["climatetrace"],
            country_codes=["NPL"],
            limit=100,
            date_from=datetime(2024, 1, 1),
            date_to="2024-12-31",
        )
        assert result == OK
        await client.close_async()


# ── OpenAQ Endpoints ─────────────────────────────────────────────────────────

class TestOpenAQ:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_locations(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_locations_async(country_codes="US", limit=10)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_locations_list_country_codes(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        await client.get_openaq_locations_async(country_codes=["US", "GB"])
        assert route.called
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_location_by_id(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/42/").mock(
            return_value=httpx.Response(200, json={"id": 42})
        )
        client = _client()
        result = await client.get_openaq_location_async(42)
        assert result["id"] == 42
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensors(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_sensors_async(
            location_id=1,
            parameter="pm25",
            country_code="US",
            location_bbox=[80, 26, 88, 30],
            coordinates=[85.3, 27.7],
            radius_km=10.0,
            limit=5,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_by_id(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/").mock(
            return_value=httpx.Response(200, json={"id": 7})
        )
        client = _client()
        result = await client.get_openaq_sensor_async(7)
        assert result["id"] == 7
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurements(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_measurements_async(
            parameter="pm25",
            date_from=datetime(2024, 1, 1),
            date_to="2024-06-30",
            ordering="-measured_at",
            page=1,
            page_size=50,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurement_by_id(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/99/").mock(
            return_value=httpx.Response(200, json={"id": 99})
        )
        client = _client()
        result = await client.get_openaq_measurement_async(99)
        assert result["id"] == 99
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurements_date_range(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/date_range/").mock(
            return_value=httpx.Response(200, json={"earliest_date": "2020-01-01"})
        )
        client = _client()
        result = await client.get_openaq_measurements_date_range_async()
        assert "earliest_date" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurements_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/totals/").mock(
            return_value=httpx.Response(200, json={"record_count": 1000})
        )
        client = _client()
        result = await client.get_openaq_measurements_totals_async()
        assert result["record_count"] == 1000
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurements_parameter_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/parameter_totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_measurements_parameter_totals_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_measurements_country_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/measurements/country_totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_measurements_country_totals_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_parameters(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/parameters/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_parameters_async(limit=50)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_parameter_by_id(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/parameters/3/").mock(
            return_value=httpx.Response(200, json={"id": 3})
        )
        client = _client()
        result = await client.get_openaq_parameter_async(3)
        assert result["id"] == 3
        await client.close_async()

    @respx.mock
    def test_get_locations_sync(self):
        """Verify sync wrapper works for OpenAQ locations."""
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_openaq_locations(limit=5)
        assert result == OK
        client.close()


# ── Climate TRACE Endpoints ──────────────────────────────────────────────────

class TestClimateTRACE:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sectors(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/sectors/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_sectors_async(limit=100)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_countries(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/countries/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_countries_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_assets(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/assets/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_assets_async(
            sector_id=1, country_code="NPL",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_emissions_async(
            country_code="NPL",
            gas="co2",
            date_from=datetime(2024, 1, 1),
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions_date_range(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/date_range/").mock(
            return_value=httpx.Response(200, json={"earliest_date": "2015-01-01"})
        )
        client = _client()
        result = await client.get_climatetrace_emissions_date_range_async(country_code="NPL")
        assert "earliest_date" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/totals/").mock(
            return_value=httpx.Response(200, json={"total_co2e": 12345.6})
        )
        client = _client()
        result = await client.get_climatetrace_emissions_totals_async(
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
        )
        assert "total_co2e" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions_sector_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/sector_totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_emissions_sector_totals_async(
            date_from=datetime(2024, 1, 1),
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions_country_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/country_totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_emissions_country_totals_async(
            date_from=datetime(2024, 1, 1),
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_emissions_gas_type_distribution(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/gas_type_distribution/").mock(
            return_value=httpx.Response(200, json={"gas_types": []})
        )
        client = _client()
        result = await client.get_climatetrace_emissions_gas_type_distribution_async()
        assert "gas_types" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_company_matches(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/company-matches/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_company_matches_async(limit=5)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_violations(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/violations/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_violations_async(limit=5)
        assert result == OK
        await client.close_async()


# ── EDGAR Endpoints ──────────────────────────────────────────────────────────

class TestEDGAR:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_country_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/country-totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_country_totals_async(
            country_code="USA", year=2023, gas="CO2",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_grid_emissions(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/grid-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_grid_emissions_async(
            year=2023, gas="CO2", min_value=1000,
            bbox="80,26,88,30", coordinates="85.3,27.7", radius=50.0,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_temporal_profiles(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/temporal-profiles/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_temporal_profiles_async(
            sector="energy", temporal_level="monthly",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_fasttrack(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/fasttrack/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_fasttrack_async(
            year=2024, provisional=True,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    def test_get_country_totals_sync(self):
        """Verify sync wrapper works for EDGAR."""
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/country-totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_edgar_country_totals(country_code="NPL")
        assert result == OK
        client.close()


class TestGLEIF:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_entities(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_entities_async(
            search="Apple Inc", legal_address_country="US", entity_status="ACTIVE",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_entity_detail(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/HWUPKR0MPOU8FGXBT394/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_entity_async("HWUPKR0MPOU8FGXBT394")
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_entity_parents(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/HWUPKR0MPOU8FGXBT394/parents/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_entity_parents_async("HWUPKR0MPOU8FGXBT394")
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_entity_children(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/HWUPKR0MPOU8FGXBT394/children/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_entity_children_async("HWUPKR0MPOU8FGXBT394")
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_relationships(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/relationships/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_relationships_async(
            start_lei="HWUPKR0MPOU8FGXBT394", relationship_type="IS_DIRECTLY_CONSOLIDATED_BY",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_exceptions(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/exceptions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_exceptions_async(
            lei="HWUPKR0MPOU8FGXBT394", exception_category="DIRECT_ACCOUNTING_CONSOLIDATION_PARENT",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    def test_get_entities_sync(self):
        """Verify sync wrapper works for GLEIF."""
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_gleif_entities(search="Apple")
        assert result == OK
        client.close()
