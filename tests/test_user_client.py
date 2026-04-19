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



# ── Geographic & Spatial ─────────────────────────────────────────────────────

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
        respx.get(f"{BASE_URL}/api/v1/esg/exports/abc/").mock(
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
    async def test_get_company_matches_minimal(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/company-matches/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_company_matches_async(limit=5)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_company_matches_by_lei(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/company-matches/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_company_matches_async(
            legal_entity_lei="HWUPKR0MPOU8FGXBT394",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_company_matches_all_filters(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/company-matches/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_company_matches_async(
            legal_entity_lei="HWUPKR0MPOU8FGXBT394",
            company_id="COMP-001",
            matching_method="exact_name",
            relationship_type="owner",
            verified=True,
            search="Alphabet",
            ordering="-matching_confidence",
            limit=10,
            offset=0,
        )
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


# ── GCP (Global Carbon Project) ──────────────────────────────────────────────

class TestGCPNationalEmissions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/national-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_national_emissions_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/national-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_national_emissions_async(
            country_code="USA", year=2020, budget_version="2024", limit=100,
        )
        assert route.called
        assert result == OK
        await client.close_async()


class TestGCPEmissionsByFuel:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/emissions-by-fuel/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_emissions_by_fuel_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/emissions-by-fuel/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_emissions_by_fuel_async(
            year=2020, budget_version="2024", limit=50,
        )
        assert route.called
        assert result == OK
        await client.close_async()


class TestGCPCarbonBudget:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/carbon-budget/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_carbon_budget_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/carbon-budget/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_carbon_budget_async(
            year=2020, budget_version="2024", limit=10,
        )
        assert route.called
        assert result == OK
        await client.close_async()


class TestGCPMethaneBudget:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/methane-budget/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_methane_budget_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/methane-budget/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gcp_methane_budget_async(
            year=2020, budget_version="2024", limit=10,
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    def test_gcp_sync_wrapper(self):
        """Verify sync wrapper works for GCP."""
        respx.get(f"{BASE_URL}/api/v1/data-sources/gcp/national-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_gcp_national_emissions(country_code="USA")
        assert result == OK
        client.close()


# ── NOAA Storm Events ─────────────────────────────────────────────────────────

class TestNOAAStormEvents:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/noaa_storm_events/events/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_noaa_storm_events_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_standard_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/noaa_storm_events/events/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_noaa_storm_events_async(
            event_type="Tornado", state="TEXAS", year=2023, month=1, limit=100,
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_spatial_bbox(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/noaa_storm_events/events/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_noaa_storm_events_async(
            bbox="25.0,-100.0,36.5,-93.5", year=2023, limit=50,
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_spatial_point_radius(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/noaa_storm_events/events/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_noaa_storm_events_async(
            lat=29.76, lon=-95.37, radius_km=50.0, event_type="Tornado", year=2023,
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    def test_noaa_sync_wrapper(self):
        """Verify sync wrapper works for NOAA."""
        respx.get(f"{BASE_URL}/api/v1/data-sources/noaa_storm_events/events/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.get_noaa_storm_events(state="TEXAS", year=2023)
        assert result == OK
        client.close()


# ── OpenAQ Detail Actions ───────────────────────────────────────────────────

class TestOpenAQDetailActions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_location_sensors(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/42/sensors/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_location_sensors_async(42)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_location_flags(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/42/flags/").mock(
            return_value=httpx.Response(200, json={"flags": []})
        )
        client = _client()
        result = await client.get_openaq_location_flags_async(42)
        assert "flags" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_location_latest_measurements(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/42/latest_measurements/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_location_latest_measurements_async(42)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_location_latest_measurements_with_datetime_min(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/locations/42/latest_measurements/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_location_latest_measurements_async(
            42, datetime_min="2024-01-01T00:00:00Z"
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_measurements(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/measurements/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_sensor_measurements_async(7, limit=50, days=3)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_flags(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/flags/").mock(
            return_value=httpx.Response(200, json={"flags": []})
        )
        client = _client()
        result = await client.get_openaq_sensor_flags_async(7)
        assert "flags" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_hourly(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/hourly/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_sensor_hourly_async(
            7, date_from=datetime(2024, 1, 1), date_to="2024-01-07"
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_daily(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/daily/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_sensor_daily_async(
            7, date_from=datetime(2024, 1, 1), date_to=datetime(2024, 6, 30)
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_yearly(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/yearly/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_sensor_yearly_async(7)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_hour_of_day(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/hour-of-day/").mock(
            return_value=httpx.Response(200, json={"hours": []})
        )
        client = _client()
        result = await client.get_openaq_sensor_hour_of_day_async(7)
        assert "hours" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_day_of_week(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/day-of-week/").mock(
            return_value=httpx.Response(200, json={"days": []})
        )
        client = _client()
        result = await client.get_openaq_sensor_day_of_week_async(7)
        assert "days" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sensor_month_of_year(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/sensors/7/month-of-year/").mock(
            return_value=httpx.Response(200, json={"months": []})
        )
        client = _client()
        result = await client.get_openaq_sensor_month_of_year_async(7)
        assert "months" in result
        await client.close_async()


# ── OpenAQ Reference Data ───────────────────────────────────────────────────

class TestOpenAQReferenceData:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_providers(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/providers/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_providers_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_owners(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/owners/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_owners_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_manufacturers(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/manufacturers/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_manufacturers_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_instruments(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/instruments/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_instruments_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_licenses(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/licenses/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_openaq_licenses_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_stats(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/openaq/stats/").mock(
            return_value=httpx.Response(200, json={"total_locations": 100})
        )
        client = _client()
        result = await client.get_openaq_stats_async()
        assert "total_locations" in result
        await client.close_async()


# ── Climate TRACE Detail Actions ────────────────────────────────────────────

class TestClimateTRACEDetailActions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sector_assets(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/sectors/5/assets/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_sector_assets_async(5)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_sector_emissions_summary(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/sectors/5/emissions_summary/").mock(
            return_value=httpx.Response(200, json={"total_assets": 10, "total_co2e_tonnes": 99999})
        )
        client = _client()
        result = await client.get_climatetrace_sector_emissions_summary_async(5)
        assert "total_assets" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_country_assets(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/countries/12/assets/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_country_assets_async(12)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_asset_emissions(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/assets/100/emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_asset_emissions_async(100)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_asset_violations(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/assets/100/violations/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_asset_violations_async(100)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_aggregated_emissions(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/emissions/aggregated-emissions/").mock(
            return_value=httpx.Response(200, json={"emissions": []})
        )
        client = _client()
        result = await client.get_climatetrace_aggregated_emissions_async(
            countries="USA,CHN", sectors="power", gas="co2", years="2020,2021"
        )
        assert "emissions" in result
        await client.close_async()


# ── Climate TRACE Annual Country Emissions ──────────────────────────────────

class TestClimateTRACEAnnualCountryEmissions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_basic(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/annual-country-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_annual_country_emissions_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_with_filters(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/annual-country-emissions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_annual_country_emissions_async(
            country_iso3="USA", year=2020, sector="power",
            gas_type="co2", ordering="-emissions_quantity", limit=50,
        )
        assert route.called
        assert result == OK
        await client.close_async()


# ── Climate TRACE Definitions ───────────────────────────────────────────────

class TestClimateTRACEDefinitions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_subsectors(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/definitions/subsectors/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_definition_subsectors_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_groups(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/definitions/groups/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_definition_groups_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_continents(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/definitions/continents/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_definition_continents_async()
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_gases(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/definitions/gases/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_definition_gases_async()
        assert result == OK
        await client.close_async()


# ── Climate TRACE Admin Areas ───────────────────────────────────────────────

class TestClimateTRACEAdminAreas:

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_admin_areas(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/admin-areas/search/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_admin_areas_search_async(
            query="Nepal", level="country"
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_admin_areas_by_point(self):
        route = respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/admin-areas/search/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_climatetrace_admin_areas_search_async(
            point="85.3,27.7"
        )
        assert route.called
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_admin_area_geojson(self):
        geojson = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}}
        respx.get(f"{BASE_URL}/api/v1/data-sources/climatetrace/admin-areas/NPL/geojson/").mock(
            return_value=httpx.Response(200, json=geojson)
        )
        client = _client()
        result = await client.get_climatetrace_admin_area_geojson_async("NPL")
        assert result["type"] == "Feature"
        await client.close_async()


# ── EDGAR Air Pollutant Endpoints ───────────────────────────────────────────

class TestEDGARAirPollutant:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_air_pollutant_totals(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/air-pollutant-totals/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_air_pollutant_totals_async(
            country_code="USA", year=2022, gas="NOx", limit=10,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_air_pollutant_grid(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/edgar/air-pollutant-grid/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_edgar_air_pollutant_grid_async(
            year=2022, gas="SO2", bbox="80,26,88,30", limit=10,
        )
        assert result == OK
        await client.close_async()


# ── ESG Analytics & Statistics ──────────────────────────────────────────────

class TestESGAnalyticsStatistics:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_analytics(self):
        respx.get(f"{BASE_URL}/api/v1/esg/analytics/").mock(
            return_value=httpx.Response(200, json={"correlations": []})
        )
        client = _client()
        result = await client.get_analytics_async(
            country_codes=["NPL"], temporal_window_days=30,
        )
        assert "correlations" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_openaq_statistics(self):
        respx.get(f"{BASE_URL}/api/v1/esg/openaq-statistics/").mock(
            return_value=httpx.Response(200, json={"locations": 50})
        )
        client = _client()
        result = await client.get_openaq_statistics_async(country_codes=["NPL"])
        assert "locations" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_climatetrace_statistics(self):
        respx.get(f"{BASE_URL}/api/v1/esg/climatetrace-statistics/").mock(
            return_value=httpx.Response(200, json={"assets": 200})
        )
        client = _client()
        result = await client.get_climatetrace_statistics_async(country_codes=["NPL"])
        assert "assets" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_table_statistics(self):
        respx.get(f"{BASE_URL}/api/v1/esg/statistics/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_table_statistics_async(limit=10)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_export_data_sync(self):
        respx.get(f"{BASE_URL}/api/v1/esg/export/").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client = _client()
        result = await client.export_data_sync_async(
            sources=["openaq"],
            country_codes=["NPL"],
            date_from=datetime(2024, 1, 1),
            output_format="json",
        )
        assert "data" in result
        await client.close_async()


# ── GLEIF Detail Actions ────────────────────────────────────────────────────

class TestGLEIFDetailActions:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_entity_asset_matches(self):
        respx.get(f"{BASE_URL}/api/v1/data-sources/gleif/entities/HWUPKR0MPOU8FGXBT394/asset-matches/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_gleif_entity_asset_matches_async("HWUPKR0MPOU8FGXBT394")
        assert result == OK
        await client.close_async()
