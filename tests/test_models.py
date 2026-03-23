"""Tests for eko_client.models — Pydantic model validation."""

from datetime import datetime
from eko_client.models import (
    QueryMetadata,
    QualityFlag,
    QualitySummary,
    Attribution,
    AirQualityMeasurement,
    EmissionMeasurement,
    UnifiedDataResponse,
    AggregationResponse,
    CorrelationResponse,
    TrendResponse,
    QualityResponse,
    AlertResponse,
    Alert,
    LocationResponse,
    UnifiedLocation,
    ExportResponse,
    ExportStatusResponse,
    DefinitionsResponse,
    ParameterDefinitionsResponse,
    ParameterDefinition,
    UnitDefinitionsResponse,
    UnitDefinition,
    UnitConversion,
    SourceDefinitionsResponse,
    SourceDefinition,
    HealthResponse,
    SystemHealthResponse,
    PlatformSummaryResponse,
    AggregatedMeasurement,
    SpatialCorrelation,
    TemporalCorrelation,
    ParameterCorrelation,
    TrendAnalysis,
    SeasonalPattern,
    Anomaly,
    Forecast,
)


class TestQueryMetadata:

    def test_from_dict(self):
        m = QueryMetadata(sources=["openaq"], total_records=100)
        assert m.sources == ["openaq"]
        assert m.total_records == 100

    def test_all_optional(self):
        m = QueryMetadata()
        assert m.sources is None


class TestQualityFlag:

    def test_from_dict(self):
        f = QualityFlag(flag_type="outlier", severity="high")
        assert f.flag_type == "outlier"


class TestQualitySummary:

    def test_with_flags(self):
        s = QualitySummary(overall_score=85, completeness=0.95)
        assert s.overall_score == 85


class TestAttribution:

    def test_from_dict(self):
        a = Attribution(openaq="CC-BY-4.0")
        assert a.openaq == "CC-BY-4.0"


class TestAirQualityMeasurement:

    def test_full_record(self):
        m = AirQualityMeasurement(
            location_id=1,
            parameter="pm25",
            value=35.0,
            unit="ug/m3",
            timestamp=datetime(2024, 1, 1),
            coordinates=[85.3, 27.7],
            source="openaq",
        )
        assert m.value == 35.0
        assert m.coordinates == [85.3, 27.7]


class TestEmissionMeasurement:

    def test_full_record(self):
        m = EmissionMeasurement(
            asset_id=100,
            parameter="co2",
            value=1234.5,
            sector="energy",
        )
        assert m.sector == "energy"


class TestUnifiedDataResponse:

    def test_minimal(self):
        r = UnifiedDataResponse()
        assert r.data is None

    def test_with_data(self):
        r = UnifiedDataResponse(
            data={"air_quality": [{"id": 1}]},
            metadata=QueryMetadata(total_records=1),
        )
        assert r.data["air_quality"][0]["id"] == 1


class TestAggregationResponse:

    def test_minimal(self):
        r = AggregationResponse(aggregations={"daily": []})
        assert r.aggregations == {"daily": []}


class TestAggregatedMeasurement:

    def test_from_dict(self):
        m = AggregatedMeasurement(parameter="pm25", temporal_resolution="daily")
        assert m.temporal_resolution == "daily"


class TestSpatialCorrelation:

    def test_from_dict(self):
        c = SpatialCorrelation(distance_km=10.5, correlation_coefficient=0.85)
        assert c.distance_km == 10.5


class TestTemporalCorrelation:

    def test_from_dict(self):
        c = TemporalCorrelation(parameter_1="pm25", parameter_2="co2", lag_days=7)
        assert c.lag_days == 7


class TestParameterCorrelation:

    def test_from_dict(self):
        c = ParameterCorrelation(parameter_1="pm25", sample_size=1000)
        assert c.sample_size == 1000


class TestCorrelationResponse:

    def test_minimal(self):
        r = CorrelationResponse(correlations={"spatial": []})
        assert "spatial" in r.correlations


class TestTrendAnalysis:

    def test_from_dict(self):
        t = TrendAnalysis(parameter="pm25", trend_direction="increasing", slope=0.5)
        assert t.slope == 0.5


class TestSeasonalPattern:

    def test_from_dict(self):
        p = SeasonalPattern(pattern_type="annual", amplitude=10.0)
        assert p.amplitude == 10.0


class TestAnomaly:

    def test_from_dict(self):
        a = Anomaly(anomaly_score=3.5, anomaly_type="spike", severity="high")
        assert a.severity == "high"


class TestForecast:

    def test_from_dict(self):
        f = Forecast(parameter="pm25", forecast_horizon=30)
        assert f.forecast_horizon == 30


class TestTrendResponse:

    def test_with_all_sections(self):
        r = TrendResponse(
            trends=[TrendAnalysis(parameter="pm25")],
            anomalies=[Anomaly(anomaly_score=2.0)],
            forecasts=[Forecast(forecast_horizon=7)],
        )
        assert len(r.trends) == 1
        assert len(r.anomalies) == 1


class TestQualityResponse:

    def test_minimal(self):
        r = QualityResponse(recommendations=["Add more sensors"])
        assert len(r.recommendations) == 1


class TestAlert:

    def test_from_dict(self):
        a = Alert(
            id="alert-1",
            type="quality",
            severity="high",
            status="active",
            title="Data gap",
        )
        assert a.title == "Data gap"


class TestAlertResponse:

    def test_with_alerts(self):
        r = AlertResponse(
            alerts=[Alert(id="1")],
            total_count=1,
            active_count=1,
        )
        assert r.total_count == 1


class TestUnifiedLocation:

    def test_from_dict(self):
        loc = UnifiedLocation(
            id=1,
            name="Kathmandu",
            coordinates=[85.3, 27.7],
            country_code="NPL",
            source="openaq",
        )
        assert loc.name == "Kathmandu"


class TestLocationResponse:

    def test_with_locations(self):
        r = LocationResponse(
            locations=[UnifiedLocation(id=1)],
            total_count=1,
        )
        assert r.total_count == 1


class TestExportResponse:

    def test_from_dict(self):
        r = ExportResponse(export_id="abc", status="processing")
        assert r.export_id == "abc"


class TestExportStatusResponse:

    def test_from_dict(self):
        r = ExportStatusResponse(export_id="abc", status="completed")
        assert r.status == "completed"


class TestParameterDefinition:

    def test_from_dict(self):
        p = ParameterDefinition(
            parameter="pm25",
            display_name="PM2.5",
            unit="ug/m3",
            sources=["openaq"],
        )
        assert p.display_name == "PM2.5"


class TestParameterDefinitionsResponse:

    def test_from_dict(self):
        r = ParameterDefinitionsResponse(
            parameters=[ParameterDefinition(parameter="pm25")],
            total_count=1,
        )
        assert r.total_count == 1


class TestUnitDefinition:

    def test_from_dict(self):
        u = UnitDefinition(unit="ug/m3", display_name="Micrograms per cubic meter")
        assert u.unit == "ug/m3"


class TestUnitConversion:

    def test_from_dict(self):
        c = UnitConversion(from_unit="mg/m3", to_unit="ug/m3", conversion_factor=1000.0)
        assert c.conversion_factor == 1000.0


class TestUnitDefinitionsResponse:

    def test_from_dict(self):
        r = UnitDefinitionsResponse(
            units=[UnitDefinition(unit="ug/m3")],
            conversions=[UnitConversion(from_unit="mg/m3", to_unit="ug/m3")],
        )
        assert len(r.units) == 1


class TestSourceDefinition:

    def test_from_dict(self):
        s = SourceDefinition(source="openaq", display_name="OpenAQ")
        assert s.source == "openaq"


class TestSourceDefinitionsResponse:

    def test_from_dict(self):
        r = SourceDefinitionsResponse(sources=[SourceDefinition(source="openaq")])
        assert len(r.sources) == 1


class TestDefinitionsResponse:

    def test_from_dict(self):
        r = DefinitionsResponse(total_parameters=50, total_units=10, total_sources=3)
        assert r.total_parameters == 50


class TestHealthResponse:

    def test_from_dict(self):
        r = HealthResponse(service="esg-api", status="ok")
        assert r.status == "ok"


class TestSystemHealthResponse:

    def test_from_dict(self):
        r = SystemHealthResponse(
            system_status={"overall_health": "ok"},
            recommendations=["Scale up workers"],
        )
        assert r.system_status["overall_health"] == "ok"


class TestPlatformSummaryResponse:

    def test_from_dict(self):
        r = PlatformSummaryResponse(
            platform_overview={"total_records": 1000000},
            generated_at=datetime(2024, 6, 15),
        )
        assert r.platform_overview["total_records"] == 1000000
