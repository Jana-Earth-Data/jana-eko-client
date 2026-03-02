"""
Pydantic models for API responses.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# Base response models
class QueryMetadata(BaseModel):
    """Query metadata."""
    sources: Optional[List[str]] = None
    temporal_resolution: Optional[str] = None
    quality_threshold: Optional[int] = None
    total_records: Optional[int] = None
    processing_time_ms: Optional[int] = None
    output_format: Optional[str] = None


class QualityFlag(BaseModel):
    """Data quality flag."""
    id: Optional[str] = None
    flag_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    parameter: Optional[str] = None
    location_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    source: Optional[str] = None


class QualitySummary(BaseModel):
    """Data quality summary."""
    overall_score: Optional[int] = None
    flags: Optional[List[QualityFlag]] = None
    completeness: Optional[float] = None


class Attribution(BaseModel):
    """Data source attribution."""
    openaq: Optional[str] = None
    climatetrace: Optional[str] = None
    edgar: Optional[str] = None


# Unified Data Response Models
class AirQualityMeasurement(BaseModel):
    """Air quality measurement."""
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    parameter: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    coordinates: Optional[List[float]] = None
    quality_score: Optional[int] = None
    quality_flags: Optional[List[str]] = None
    source: Optional[str] = None
    source_id: Optional[str] = None


class EmissionMeasurement(BaseModel):
    """Emission measurement."""
    asset_id: Optional[int] = None
    asset_name: Optional[str] = None
    parameter: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    coordinates: Optional[List[float]] = None
    sector: Optional[str] = None
    owner: Optional[str] = None
    quality_score: Optional[int] = None
    source: Optional[str] = None
    source_id: Optional[str] = None


class UnifiedDataResponse(BaseModel):
    """Unified data response."""
    query: Optional[Dict[str, Any]] = None
    metadata: Optional[QueryMetadata] = None
    data: Optional[Dict[str, Any]] = None  # Can contain air_quality, emissions, raw_data, aggregated_data
    quality: Optional[QualitySummary] = None
    analytics: Optional[Dict[str, Any]] = None
    attribution: Optional[Attribution] = None


# Aggregation Response Models
class AggregatedMeasurement(BaseModel):
    """Aggregated measurement."""
    location_id: Optional[int] = None
    parameter: Optional[str] = None
    timestamp: Optional[datetime] = None
    temporal_resolution: Optional[str] = None
    statistics: Optional[Dict[str, float]] = None
    quality: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    coordinates: Optional[List[float]] = None


class AggregationResponse(BaseModel):
    """Aggregation response."""
    query: Optional[Dict[str, Any]] = None
    aggregations: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Correlation Response Models
class SpatialCorrelation(BaseModel):
    """Spatial correlation."""
    location_1: Optional[Dict[str, Any]] = None
    location_2: Optional[Dict[str, Any]] = None
    distance_km: Optional[float] = None
    correlation_coefficient: Optional[float] = None
    p_value: Optional[float] = None
    sample_size: Optional[int] = None
    parameters: Optional[List[str]] = None


class TemporalCorrelation(BaseModel):
    """Temporal correlation."""
    parameter_1: Optional[str] = None
    parameter_2: Optional[str] = None
    correlation_coefficient: Optional[float] = None
    lag_days: Optional[int] = None
    p_value: Optional[float] = None
    sample_size: Optional[int] = None
    time_period: Optional[Dict[str, datetime]] = None


class ParameterCorrelation(BaseModel):
    """Parameter correlation."""
    parameter_1: Optional[str] = None
    parameter_2: Optional[str] = None
    correlation_coefficient: Optional[float] = None
    p_value: Optional[float] = None
    confidence_interval: Optional[Dict[str, float]] = None
    sample_size: Optional[int] = None
    geographic_scope: Optional[str] = None


class CorrelationResponse(BaseModel):
    """Correlation analysis response."""
    query: Optional[Dict[str, Any]] = None
    correlations: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    methodology: Optional[Dict[str, Any]] = None


# Trend Response Models
class TrendAnalysis(BaseModel):
    """Trend analysis."""
    parameter: Optional[str] = None
    location_id: Optional[int] = None
    trend_direction: Optional[str] = None
    trend_strength: Optional[float] = None
    slope: Optional[float] = None
    p_value: Optional[float] = None
    confidence_interval: Optional[Dict[str, float]] = None
    time_period: Optional[Dict[str, datetime]] = None


class SeasonalPattern(BaseModel):
    """Seasonal pattern."""
    parameter: Optional[str] = None
    pattern_type: Optional[str] = None
    amplitude: Optional[float] = None
    phase: Optional[float] = None
    strength: Optional[float] = None
    components: Optional[List[Dict[str, Any]]] = None


class Anomaly(BaseModel):
    """Anomaly detection result."""
    id: Optional[str] = None
    parameter: Optional[str] = None
    location_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    value: Optional[float] = None
    expected_value: Optional[float] = None
    anomaly_score: Optional[float] = None
    anomaly_type: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None


class Forecast(BaseModel):
    """Forecast result."""
    parameter: Optional[str] = None
    location_id: Optional[int] = None
    forecast_horizon: Optional[int] = None
    forecasts: Optional[List[Dict[str, Any]]] = None
    model_info: Optional[Dict[str, Any]] = None


class TrendResponse(BaseModel):
    """Trend analysis response."""
    query: Optional[Dict[str, Any]] = None
    trends: Optional[List[TrendAnalysis]] = None
    seasonal_patterns: Optional[List[SeasonalPattern]] = None
    anomalies: Optional[List[Anomaly]] = None
    forecasts: Optional[List[Forecast]] = None
    statistics: Optional[Dict[str, Any]] = None


# Quality Response Models
class QualityResponse(BaseModel):
    """Quality analysis response."""
    overall_quality: Optional[Dict[str, Any]] = None
    quality_flags: Optional[Dict[str, Any]] = None
    completeness: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None


# Alert Response Models
class Alert(BaseModel):
    """Alert information."""
    id: Optional[str] = None
    type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    location_id: Optional[int] = None
    parameter: Optional[str] = None
    source: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    """Alert response."""
    alerts: Optional[List[Alert]] = None
    total_count: Optional[int] = None
    active_count: Optional[int] = None
    critical_count: Optional[int] = None
    summary: Optional[Dict[str, Any]] = None


# Location Response Models
class UnifiedLocation(BaseModel):
    """Unified location."""
    id: Optional[int] = None
    name: Optional[str] = None
    coordinates: Optional[List[float]] = None
    country_code: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    facility_type: Optional[str] = None
    sector: Optional[str] = None
    owner: Optional[str] = None
    admin_areas: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class LocationResponse(BaseModel):
    """Location response."""
    locations: Optional[List[UnifiedLocation]] = None
    total_count: Optional[int] = None
    sources_included: Optional[List[str]] = None
    query: Optional[Dict[str, Any]] = None
    attribution: Optional[Attribution] = None


# Export Response Models
class ExportResponse(BaseModel):
    """Export request response."""
    export_id: Optional[str] = None
    status: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class ExportStatusResponse(BaseModel):
    """Export status response."""
    export_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


# Definition Response Models
class ParameterDefinition(BaseModel):
    """Parameter definition."""
    parameter: Optional[str] = None
    display_name: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    parameter_type: Optional[str] = None
    sources: Optional[List[str]] = None
    measurement_methods: Optional[List[str]] = None
    typical_range: Optional[Dict[str, float]] = None
    health_implications: Optional[str] = None
    regulatory_standards: Optional[List[Dict[str, Any]]] = None


class ParameterDefinitionsResponse(BaseModel):
    """Parameter definitions response."""
    parameters: Optional[List[ParameterDefinition]] = None
    total_count: Optional[int] = None
    sources_included: Optional[List[str]] = None


class UnitDefinition(BaseModel):
    """Unit definition."""
    unit: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    unit_type: Optional[str] = None
    base_unit: Optional[str] = None
    conversion_factor: Optional[float] = None


class UnitConversion(BaseModel):
    """Unit conversion."""
    from_unit: Optional[str] = None
    to_unit: Optional[str] = None
    conversion_factor: Optional[float] = None
    formula: Optional[str] = None


class UnitDefinitionsResponse(BaseModel):
    """Unit definitions response."""
    units: Optional[List[UnitDefinition]] = None
    conversions: Optional[List[UnitConversion]] = None


class SourceDefinition(BaseModel):
    """Source definition."""
    source: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    attribution: Optional[str] = None
    data_types: Optional[List[str]] = None
    geographic_coverage: Optional[str] = None
    temporal_coverage: Optional[Dict[str, Any]] = None
    data_quality: Optional[Dict[str, Any]] = None
    methodology: Optional[Dict[str, Any]] = None
    license: Optional[Dict[str, Any]] = None


class SourceDefinitionsResponse(BaseModel):
    """Source definitions response."""
    sources: Optional[List[SourceDefinition]] = None


class DefinitionsResponse(BaseModel):
    """Definitions response."""
    categories: Optional[List[Dict[str, Any]]] = None
    total_parameters: Optional[int] = None
    total_units: Optional[int] = None
    total_sources: Optional[int] = None
    last_updated: Optional[datetime] = None


# Health Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    service: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    timestamp: Optional[datetime] = None


class SystemHealthResponse(BaseModel):
    """System health response."""
    system_status: Optional[Dict[str, Any]] = None
    data_freshness: Optional[Dict[str, Any]] = None
    ingestion_health: Optional[Dict[str, Any]] = None
    api_performance: Optional[Dict[str, Any]] = None
    database_health: Optional[Dict[str, Any]] = None
    alerts: Optional[List[Alert]] = None
    recommendations: Optional[List[str]] = None


class PlatformSummaryResponse(BaseModel):
    """Platform summary response."""
    platform_overview: Optional[Dict[str, Any]] = None
    system_health: Optional[Dict[str, Any]] = None
    data_quality: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    generated_at: Optional[datetime] = None
    attribution: Optional[Attribution] = None


# Generic response type for flexible handling
APIResponse = Union[
    UnifiedDataResponse,
    AggregationResponse,
    CorrelationResponse,
    TrendResponse,
    QualityResponse,
    AlertResponse,
    LocationResponse,
    ExportResponse,
    ExportStatusResponse,
    DefinitionsResponse,
    ParameterDefinitionsResponse,
    UnitDefinitionsResponse,
    SourceDefinitionsResponse,
    HealthResponse,
    SystemHealthResponse,
    PlatformSummaryResponse,
    Dict[str, Any],  # Fallback for unknown response types
]

