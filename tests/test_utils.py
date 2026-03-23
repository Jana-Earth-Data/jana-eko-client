"""Tests for eko_client.utils — format_query_params, parse_date, build_url."""

from datetime import datetime
from eko_client.utils import format_query_params, parse_date, build_url


# ── format_query_params ──────────────────────────────────────────────────────

class TestFormatQueryParams:

    def test_strips_none_values(self):
        result = format_query_params({"a": 1, "b": None, "c": "x"})
        assert result == {"a": 1, "c": "x"}

    def test_all_none_returns_empty(self):
        assert format_query_params({"a": None, "b": None}) == {}

    def test_empty_dict(self):
        assert format_query_params({}) == {}

    def test_list_to_comma_separated(self):
        result = format_query_params({"sources": ["openaq", "edgar"]})
        assert result == {"sources": "openaq,edgar"}

    def test_tuple_to_comma_separated(self):
        result = format_query_params({"sources": ("openaq", "edgar")})
        assert result == {"sources": "openaq,edgar"}

    def test_location_bbox_kept_as_list(self):
        bbox = [1.0, 2.0, 3.0, 4.0]
        result = format_query_params({"location_bbox": bbox})
        assert result == {"location_bbox": bbox}

    def test_location_point_kept_as_list(self):
        point = [85.3, 27.7]
        result = format_query_params({"location_point": point})
        assert result == {"location_point": point}

    def test_datetime_converted_to_isoformat(self):
        dt = datetime(2024, 6, 15, 12, 0, 0)
        result = format_query_params({"date_from": dt})
        assert result == {"date_from": "2024-06-15T12:00:00"}

    def test_bool_converted_to_lowercase_string(self):
        result = format_query_params({"provisional": True, "active": False})
        assert result == {"provisional": "true", "active": "false"}

    def test_scalar_values_passed_through(self):
        result = format_query_params({"year": 2023, "gas": "CO2", "limit": 100})
        assert result == {"year": 2023, "gas": "CO2", "limit": 100}

    def test_mixed_types(self):
        result = format_query_params({
            "sources": ["openaq"],
            "location_bbox": [1, 2, 3, 4],
            "year": 2023,
            "provisional": True,
            "date_from": datetime(2024, 1, 1),
            "unused": None,
        })
        assert result == {
            "sources": "openaq",
            "location_bbox": [1, 2, 3, 4],
            "year": 2023,
            "provisional": "true",
            "date_from": "2024-01-01T00:00:00",
        }


# ── parse_date ───────────────────────────────────────────────────────────────

class TestParseDate:

    def test_valid_iso_date(self):
        result = parse_date("2024-06-15T12:00:00")
        assert result == datetime(2024, 6, 15, 12, 0, 0)

    def test_z_suffix_replaced(self):
        result = parse_date("2024-06-15T12:00:00Z")
        assert result is not None
        assert result.year == 2024

    def test_none_returns_none(self):
        assert parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert parse_date("") is None

    def test_invalid_string_returns_none(self):
        assert parse_date("not-a-date") is None


# ── build_url ────────────────────────────────────────────────────────────────

class TestBuildUrl:

    def test_simple_url(self):
        result = build_url("https://api.test.com", "/api/v1/health/")
        assert result == "https://api.test.com/api/v1/health/"

    def test_strips_trailing_slash_from_base(self):
        result = build_url("https://api.test.com/", "/api/v1/health/")
        assert result == "https://api.test.com/api/v1/health/"

    def test_strips_leading_slash_from_path(self):
        result = build_url("https://api.test.com", "api/v1/health/")
        assert result == "https://api.test.com/api/v1/health/"

    def test_multiple_path_parts(self):
        result = build_url("https://api.test.com", "/api/v1", "health/")
        assert result == "https://api.test.com/api/v1/health/"

    def test_empty_path_parts_skipped(self):
        result = build_url("https://api.test.com", "", "/api/v1/health/")
        assert result == "https://api.test.com/api/v1/health/"
