"""
Eko User Client - End-user client for unified API access.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .client import BaseEkoClient
from .jwt_auth import JwtAuthMixin
from .utils import build_url
from .sync_wrapper import auto_sync_wrapper
from .models import (
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
)


@auto_sync_wrapper
class EkoUserClient(JwtAuthMixin, BaseEkoClient):
    """
    End-user client for accessing unified environmental data APIs.

    This client provides access to all unified data endpoints but excludes
    job management APIs. For job management, use EkoAdminClient.

    All methods have both sync and async versions:
    - Async methods end with '_async' suffix (e.g., get_data_async)
    - Sync methods are auto-generated without the suffix (e.g., get_data)

    Example (single URL — all requests go to one host):
        >>> client = EkoUserClient(base_url="https://api.jana.com")
        >>> client.login_device()  # opens browser for OAuth 2.0 device code flow
        >>> data = client.get_data(sources=["openaq", "climatetrace"])

    Example (dual URL — auth and data on separate hosts):
        >>> client = EkoUserClient(
        ...     base_url="https://auth-dev.jana.earth",      # auth endpoints
        ...     api_base_url="https://api-dev.jana.earth",    # data/ESG endpoints
        ... )
        >>> client.login_device()       # -> auth-dev.jana.earth/api/auth/device-code/
        >>> data = client.get_data(...)  # -> api-dev.jana.earth/api/v1/esg/data/
    """

    # =============================================================================
    # Core Data Access
    # =============================================================================

    async def get_data_async(
        self,
        sources: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        location_point: Optional[List[float]] = None,
        radius_km: Optional[float] = None,
        country_codes: Optional[List[str]] = None,
        admin_areas: Optional[List[str]] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        temporal_resolution: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        quality_threshold: Optional[int] = None,
        include_flags: Optional[bool] = None,
        correlation_analysis: Optional[bool] = None,
        trend_analysis: Optional[bool] = None,
        anomaly_detection: Optional[bool] = None,
        statistical_tests: Optional[bool] = None,
        output_format: Optional[str] = None,
        bbox_precision: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get unified environmental data from multiple sources.

        Args:
            sources: Data sources to include (openaq, climatetrace, edgar)
            location_bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            location_point: Point coordinates [longitude, latitude]
            radius_km: Search radius in kilometers for point-based queries
            country_codes: ISO 3-letter country codes
            admin_areas: Administrative area IDs
            date_from: Start date (ISO 8601 or datetime)
            date_to: End date (ISO 8601 or datetime)
            temporal_resolution: Aggregation level (raw, hourly, daily, monthly)
            parameters: Environmental parameters to include
            quality_threshold: Minimum data quality score (0-100)
            include_flags: Include data quality flags
            correlation_analysis: Enable cross-source correlation analysis
            trend_analysis: Include temporal trend indicators
            anomaly_detection: Flag anomalous data points
            statistical_tests: Include statistical significance testing
            output_format: Response format (json, geojson, csv)
            bbox_precision: Geographic precision level (low, medium, high)
            limit: Maximum number of results (1-10000)
            offset: Result offset for pagination

        Returns:
            Unified data response dictionary
        """
        params = {
            'sources': sources,
            'location_bbox': location_bbox,
            'location_point': location_point,
            'radius_km': radius_km,
            'country_codes': country_codes,
            'admin_areas': admin_areas,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'temporal_resolution': temporal_resolution,
            'parameters': parameters,
            'quality_threshold': quality_threshold,
            'include_flags': include_flags,
            'correlation_analysis': correlation_analysis,
            'trend_analysis': trend_analysis,
            'anomaly_detection': anomaly_detection,
            'statistical_tests': statistical_tests,
            'output_format': output_format,
            'bbox_precision': bbox_precision,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/esg/data/', params=params)

    async def get_aggregations_async(
        self,
        temporal_resolution: str,
        sources: Optional[List[str]] = None,
        country_codes: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        quality_threshold: Optional[int] = None,
        parameters: Optional[List[str]] = None,
        include_correlations: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Get pre-computed temporal aggregations.

        Args:
            temporal_resolution: Aggregation level (hourly, daily, monthly)
            sources: Data sources to include
            country_codes: ISO 3-letter country codes (required by server)
            location_bbox: Geographic bounding box
            date_from: Start date
            date_to: End date
            quality_threshold: Minimum quality score
            parameters: Parameters to aggregate
            include_correlations: Include cross-source correlations

        Returns:
            Aggregation response dictionary
        """
        params = {
            'temporal_resolution': temporal_resolution,
            'sources': sources,
            'country_codes': country_codes,
            'location_bbox': location_bbox,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'quality_threshold': quality_threshold,
            'parameters': parameters,
            'include_correlations': include_correlations,
        }
        return await self._request_async('GET', '/api/v1/esg/aggregations/', params=params)

    # =============================================================================
    # Analytics & Intelligence
    # =============================================================================

    async def get_correlations_async(
        self,
        sources: List[str],
        country_codes: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        correlation_type: Optional[str] = None,
        location_bbox: Optional[List[float]] = None,
        temporal_window_days: Optional[int] = None,
        spatial_radius_km: Optional[float] = None,
        minimum_data_points: Optional[int] = None,
        statistical_tests: Optional[bool] = None,
        sector_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get cross-source correlation analysis.

        Args:
            sources: Data sources for correlation (minimum 2)
            country_codes: ISO 3-letter country codes (required by API)
            parameters: Parameters to correlate
            correlation_type: Type of correlation (spatial, temporal, parameter, sector)
            location_bbox: Geographic area for analysis
            temporal_window_days: Temporal window for correlation (1-365)
            spatial_radius_km: Spatial radius for proximity-based correlations
            minimum_data_points: Minimum data points required
            statistical_tests: Include statistical significance testing
            sector_filter: Filter by specific industrial sectors

        Returns:
            Correlation analysis response dictionary
        """
        params = {
            'sources': sources,
            'country_codes': country_codes,
            'parameters': parameters,
            'correlation_type': correlation_type,
            'location_bbox': location_bbox,
            'temporal_window_days': temporal_window_days,
            'spatial_radius_km': spatial_radius_km,
            'minimum_data_points': minimum_data_points,
            'statistical_tests': statistical_tests,
            'sector_filter': sector_filter,
        }
        return await self._request_async('GET', '/api/v1/esg/correlations/', params=params)

    async def get_trends_async(
        self,
        sources: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        analysis_type: Optional[str] = None,
        temporal_resolution: Optional[str] = None,
        location_bbox: Optional[List[float]] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        forecast_days: Optional[int] = None,
        confidence_level: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get temporal trend analysis and forecasting.

        Args:
            sources: Data sources for trend analysis
            parameters: Parameters to analyze
            analysis_type: Type of analysis (trend, seasonal, anomaly, forecast)
            temporal_resolution: Temporal resolution (daily, weekly, monthly)
            location_bbox: Geographic area for analysis
            date_from: Start date
            date_to: End date
            forecast_days: Number of days to forecast (1-90)
            confidence_level: Confidence level for statistical tests (0.5-0.99)

        Returns:
            Trend analysis response dictionary
        """
        params = {
            'sources': sources,
            'parameters': parameters,
            'analysis_type': analysis_type,
            'temporal_resolution': temporal_resolution,
            'location_bbox': location_bbox,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'forecast_days': forecast_days,
            'confidence_level': confidence_level,
        }
        return await self._request_async('GET', '/api/v1/esg/trends/', params=params)

    # =============================================================================
    # Quality & Monitoring
    # =============================================================================

    async def get_quality_async(
        self,
        sources: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        parameters: Optional[List[str]] = None,
        quality_detail_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get unified data quality insights.

        Args:
            sources: Data sources for quality analysis
            location_bbox: Geographic area for quality analysis
            date_from: Start date
            date_to: End date
            parameters: Parameters to assess
            quality_detail_level: Level of detail (summary, detailed, comprehensive)

        Returns:
            Quality analysis response dictionary
        """
        params = {
            'sources': sources,
            'location_bbox': location_bbox,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'parameters': parameters,
            'quality_detail_level': quality_detail_level,
        }
        return await self._request_async('GET', '/api/v1/esg/quality/', params=params)

    async def get_alerts_async(
        self,
        alert_types: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        status: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get quality-based intelligent alerts.

        Args:
            alert_types: Types of alerts (quality, correlation, availability, threshold, system)
            severity: Alert severity (low, medium, high, critical)
            status: Alert status (active, resolved, acknowledged)
            date_from: Start date for alert retrieval
            limit: Maximum number of alerts (1-1000)

        Returns:
            Alert response dictionary
        """
        params = {
            'alert_types': alert_types,
            'severity': severity,
            'status': status,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'limit': limit,
        }
        return await self._request_async('GET', '/api/v1/esg/alerts/', params=params)

    # =============================================================================
    # Geographic & Spatial
    # =============================================================================

    async def get_geojson_async(
        self,
        sources: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        parameters: Optional[List[str]] = None,
        temporal_resolution: Optional[str] = None,
        quality_threshold: Optional[int] = None,
        geometry_simplification: Optional[str] = None,
        include_quality_styling: Optional[bool] = None,
        layer_separation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Get mapping-ready unified data in GeoJSON format.

        Args:
            sources: Data sources to include
            location_bbox: Geographic bounding box
            parameters: Parameters to include in GeoJSON properties
            temporal_resolution: Temporal resolution for time-series animation
            quality_threshold: Minimum quality score for included features
            geometry_simplification: Geometry simplification level (none, low, medium, high)
            include_quality_styling: Include quality-based styling properties
            layer_separation: Separate features by data source into different layers

        Returns:
            GeoJSON feature collection dictionary
        """
        params = {
            'sources': sources,
            'location_bbox': location_bbox,
            'parameters': parameters,
            'temporal_resolution': temporal_resolution,
            'quality_threshold': quality_threshold,
            'geometry_simplification': geometry_simplification,
            'include_quality_styling': include_quality_styling,
            'layer_separation': layer_separation,
        }
        return await self._request_async('GET', '/api/v1/esg/geojson/', params=params)

    async def get_locations_async(
        self,
        sources: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        location_point: Optional[List[float]] = None,
        radius_km: Optional[float] = None,
        country_codes: Optional[List[str]] = None,
        admin_areas: Optional[List[str]] = None,
        include_metadata: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get unified location data.

        Args:
            sources: Data sources to include
            location_bbox: Geographic bounding box
            location_point: Point coordinates for radius-based search
            radius_km: Search radius in kilometers
            country_codes: Country code filter
            admin_areas: Administrative area filter
            include_metadata: Include detailed location metadata
            limit: Maximum number of locations (1-10000)

        Returns:
            Location response dictionary
        """
        params = {
            'sources': sources,
            'location_bbox': location_bbox,
            'location_point': location_point,
            'radius_km': radius_km,
            'country_codes': country_codes,
            'admin_areas': admin_areas,
            'include_metadata': include_metadata,
            'limit': limit,
        }
        return await self._request_async('GET', '/api/v1/esg/locations/', params=params)

    # =============================================================================
    # Export & Bulk Access
    # =============================================================================

    async def create_export_async(
        self,
        format: str,
        query: Dict[str, Any],
        compression: Optional[str] = None,
        chunk_size: Optional[int] = None,
        email_notification: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create bulk data export.

        Args:
            format: Export format (csv, json, parquet, geojson)
            query: Query parameters for data selection
            compression: Compression type (none, gzip, bzip2)
            chunk_size: Chunk size for processing (1000-100000)
            email_notification: Email address for notification
            expires_in_hours: Export expiration in hours (1-168)

        Returns:
            Export response dictionary with export_id
        """
        json_data = {
            'query_params': query,
            'export_format': format,
        }
        if compression is not None:
            json_data['compression'] = compression
        if chunk_size is not None:
            json_data['chunk_size'] = chunk_size
        if email_notification is not None:
            json_data['email_notification'] = email_notification
        if expires_in_hours is not None:
            json_data['expires_in_hours'] = expires_in_hours
        return await self._request_async('POST', '/api/v1/esg/exports/', json_data=json_data)

    async def get_export_status_async(self, export_id: str) -> Dict[str, Any]:
        """
        Get export status.

        Args:
            export_id: Export request ID

        Returns:
            Export status response dictionary
        """
        endpoint = f'/api/v1/esg/exports/{export_id}/status/'
        return await self._request_async('GET', endpoint)

    async def download_export_async(self, export_id: str) -> bytes:
        """
        Download exported data.

        Args:
            export_id: Export request ID

        Returns:
            Export file content as bytes
        """
        endpoint = f'/api/v1/esg/exports/{export_id}/download/'
        url = build_url(self.base_url, endpoint)
        headers = self._get_headers()

        async with self._async_lock:
            client = self._get_async_client()
            response = await client.get(url, headers=headers)

            if not response.is_success:
                self._handle_response(response)

            return response.content

    # =============================================================================
    # Metadata & Definitions
    # =============================================================================

    async def get_definitions_async(self) -> Dict[str, Any]:
        """
        Get unified definitions and metadata.

        Returns:
            Definitions response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/definitions/')

    async def get_parameter_definitions_async(
        self,
        sources: Optional[List[str]] = None,
        parameter_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get environmental parameter definitions.

        Args:
            sources: Filter parameters by data sources
            parameter_types: Filter by parameter types (air_quality, emissions, climate, meteorological)

        Returns:
            Parameter definitions response dictionary
        """
        params = {
            'sources': sources,
            'parameter_types': parameter_types,
        }
        return await self._request_async('GET', '/api/v1/esg/parameters/', params=params)

    async def get_unit_definitions_async(self) -> Dict[str, Any]:
        """
        Get unit definitions and conversions.

        Returns:
            Unit definitions response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/definitions/units/')

    async def get_source_definitions_async(self) -> Dict[str, Any]:
        """
        Get data source information.

        Returns:
            Source definitions response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/definitions/sources/')

    # =============================================================================
    # System & Health
    # =============================================================================

    async def get_health_async(self) -> Dict[str, Any]:
        """
        Get API health check.

        Returns:
            Health response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/health/')

    async def get_system_health_async(self) -> Dict[str, Any]:
        """
        Get comprehensive system health.

        Returns:
            System health response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/system-health/')

    async def get_summary_async(self) -> Dict[str, Any]:
        """
        Get platform summary.

        Returns:
            Platform summary response dictionary
        """
        return await self._request_async('GET', '/api/v1/esg/summary/')

    async def get_sectors_async(
        self,
        sources: Optional[List[str]] = None,
        country_codes: Optional[List[str]] = None,
        limit: Optional[int] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Get unified sectors across all data sources.

        Args:
            sources: List of data sources to include ['climatetrace', 'edgar'] (default: all)
            country_codes: ISO 3-letter country codes (required when sources includes 'climatetrace')
            limit: Maximum number of results (default: 1000)
            date_from: Filter Climate TRACE sectors to those with data from this date (ISO format)
            date_to: Filter Climate TRACE sectors to those with data until this date (ISO format)

        Returns:
            Dictionary with sectors from all requested sources
        """
        params = {}
        if sources:
            params['sources'] = sources  # format_query_params will handle the list
        if country_codes:
            params['country_codes'] = country_codes
        if limit:
            params['limit'] = limit
        if date_from:
            params['date_from'] = date_from.isoformat() if isinstance(date_from, datetime) else date_from
        if date_to:
            params['date_to'] = date_to.isoformat() if isinstance(date_to, datetime) else date_to
        return await self._request_async('GET', '/api/v1/esg/sectors/', params=params)

    # =============================================================================
    # Source-Specific Endpoints (Read-Only)
    # =============================================================================

    # OpenAQ Methods
    async def get_openaq_locations_async(
        self,
        country_codes: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ locations."""
        params = {
            'country_codes': country_codes,
            'location_bbox': location_bbox,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/openaq/locations/', params=params)

    async def get_openaq_location_async(self, location_id: int) -> Dict[str, Any]:
        """Get specific OpenAQ location by ID."""
        endpoint = f'/api/v1/data-sources/openaq/locations/{location_id}/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_sensors_async(
        self,
        location_id: Optional[int] = None,
        parameter: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ sensors."""
        params = {
            'location_id': location_id,
            'parameter': parameter,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/openaq/sensors/', params=params)

    async def get_openaq_sensor_async(self, sensor_id: int) -> Dict[str, Any]:
        """Get specific OpenAQ sensor by ID."""
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_measurements_async(
        self,
        location_id: Optional[int] = None,
        parameter: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ measurements."""
        params = {
            'location_id': location_id,
            'parameter': parameter,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/openaq/measurements/', params=params)

    async def get_openaq_measurement_async(self, measurement_id: int) -> Dict[str, Any]:
        """Get specific OpenAQ measurement by ID."""
        endpoint = f'/api/v1/data-sources/openaq/measurements/{measurement_id}/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_measurements_date_range_async(self) -> Dict[str, Any]:
        """
        Get the minimum and maximum measured_at dates for OpenAQ measurements.
        Uses SQL MIN/MAX aggregation for efficient date range detection.

        Returns:
            Dictionary with 'earliest_date', 'latest_date', 'total_records'
        """
        return await self._request_async('GET', '/api/v1/data-sources/openaq/measurements/date_range/')

    async def get_openaq_measurements_totals_async(self) -> Dict[str, Any]:
        """
        Get global measurement totals using SQL aggregations.

        Returns:
            Dictionary with 'record_count', 'avg_value', 'min_value', 'max_value'
        """
        return await self._request_async('GET', '/api/v1/data-sources/openaq/measurements/totals/')

    async def get_openaq_measurements_parameter_totals_async(self) -> Dict[str, Any]:
        """
        Get measurements grouped by parameter using SQL GROUP BY aggregation.

        Returns:
            List of dictionaries with 'parameter_name', 'unit', 'record_count',
            'avg_value', 'min_value', 'max_value'
        """
        return await self._request_async('GET', '/api/v1/data-sources/openaq/measurements/parameter_totals/')

    async def get_openaq_measurements_country_totals_async(self) -> Dict[str, Any]:
        """
        Get measurements grouped by country using SQL GROUP BY aggregation.

        Returns:
            List of dictionaries with 'country_code', 'record_count', 'avg_value'
        """
        return await self._request_async('GET', '/api/v1/data-sources/openaq/measurements/country_totals/')

    async def get_openaq_parameters_async(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ parameters."""
        params = {'limit': limit, 'offset': offset}
        return await self._request_async('GET', '/api/v1/data-sources/openaq/parameters/', params=params)

    async def get_openaq_parameter_async(self, parameter_id: int) -> Dict[str, Any]:
        """Get specific OpenAQ parameter by ID."""
        endpoint = f'/api/v1/data-sources/openaq/parameters/{parameter_id}/'
        return await self._request_async('GET', endpoint)

    # Climate TRACE Methods
    async def get_climatetrace_sectors_async(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE sectors."""
        params = {'limit': limit, 'offset': offset}
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/sectors/', params=params)

    async def get_climatetrace_countries_async(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE countries."""
        params = {'limit': limit, 'offset': offset}
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/countries/', params=params)

    async def get_climatetrace_assets_async(
        self,
        sector_id: Optional[int] = None,
        country_code: Optional[str] = None,
        location_bbox: Optional[List[float]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE assets."""
        params = {
            'sector_id': sector_id,  # API now accepts both 'sector_id' and 'sector'
            'country_code': country_code,
            'location_bbox': location_bbox,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/assets/', params=params)

    async def get_climatetrace_emissions_async(
        self,
        asset_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        sector_name: Optional[str] = None,
        country_code: Optional[str] = None,
        gas: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE emissions.

        Args:
            asset_id: Filter by asset ID
            sector_id: Filter by sector ID
            sector_name: Filter by sector name
            country_code: Filter by ISO 3-letter country code (e.g. 'NPL')
            gas: Filter by gas type
            date_from: Start date filter
            date_to: End date filter
            limit: Maximum results per page
            offset: Result offset for pagination
        """
        params = {
            'asset_id': asset_id,
            'sector_id': sector_id,
            'sector_name': sector_name,
            'country_code': country_code,
            'gas': gas,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/', params=params)

    async def get_climatetrace_emissions_date_range_async(
        self,
        country_code: Optional[str] = None,
        sector_name: Optional[str] = None,
        gas: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the minimum and maximum start_time dates for Climate TRACE emissions.
        Uses SQL MIN/MAX aggregation for efficient date range detection.

        Args:
            country_code: Filter by ISO 3-letter country code (e.g. 'NPL')
            sector_name: Filter by sector name
            gas: Filter by gas type

        Returns:
            Dictionary with 'earliest_date', 'latest_date', and 'total_records'
        """
        params = {'country_code': country_code, 'sector_name': sector_name, 'gas': gas}
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/date_range/', params=params)

    async def get_climatetrace_emissions_totals_async(
        self,
        country_code: Optional[str] = None,
        sector_name: Optional[str] = None,
        gas: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Get emission totals using SQL SUM aggregation.

        When filters are provided, the API performs live aggregation against
        the filtered queryset. Without filters, it reads from a materialized view.

        Args:
            country_code: Filter by ISO 3-letter country code (e.g. 'NPL')
            sector_name: Filter by sector name
            gas: Filter by gas type
            date_from: Start date filter
            date_to: End date filter

        Returns:
            Dictionary with 'total_co2e', 'total_co2', 'total_ch4', 'total_n2o',
            'record_count', and 'avg_co2e'
        """
        params = {
            'country_code': country_code,
            'sector_name': sector_name,
            'gas': gas,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/totals/', params=params)

    async def get_climatetrace_emissions_sector_totals_async(
        self,
        country_code: Optional[str] = None,
        gas: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Get emissions grouped by sector using SQL GROUP BY aggregation.

        Args:
            country_code: Filter by ISO 3-letter country code (e.g. 'NPL')
            gas: Filter by gas type
            date_from: Start date filter
            date_to: End date filter

        Returns:
            List of dictionaries with 'sector_name', 'total_co2e', 'record_count', 'unique_assets'
        """
        params = {
            'country_code': country_code,
            'gas': gas,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/sector_totals/', params=params)

    async def get_climatetrace_emissions_country_totals_async(
        self,
        gas: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Get emissions grouped by country using SQL GROUP BY aggregation.

        Args:
            gas: Filter by gas type
            date_from: Start date filter
            date_to: End date filter

        Returns:
            List of dictionaries with 'country_iso3', 'total_co2e', 'record_count', 'unique_assets'
        """
        params = {
            'gas': gas,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/country_totals/', params=params)

    async def get_climatetrace_emissions_gas_type_distribution_async(
        self,
        country_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get distribution of gas types across all emissions using SQL GROUP BY.

        Args:
            country_code: Filter by ISO 3-letter country code (e.g. 'NPL')

        Returns:
            Dictionary with 'total_records' and 'gas_types' list containing
            'gas', 'record_count', 'percentage' for each gas type
        """
        params = {'country_code': country_code}
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/gas_type_distribution/', params=params)

    async def get_climatetrace_company_matches_async(
        self,
        asset_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE company matches."""
        params = {
            'asset_id': asset_id,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/company-matches/', params=params)

    async def get_climatetrace_violations_async(
        self,
        asset_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE violations."""
        params = {
            'asset_id': asset_id,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/violations/', params=params)

    # EDGAR Methods
    async def get_edgar_country_totals_async(
        self,
        country_code: Optional[str] = None,
        year: Optional[int] = None,
        gas: Optional[str] = None,
        sector: Optional[str] = None,
        provisional: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR country totals."""
        params = {
            'country_code': country_code,
            'year': year,
            'gas': gas,
            'sector': sector,
            'provisional': provisional,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/country-totals/', params=params)

    async def get_edgar_grid_emissions_async(
        self,
        year: Optional[int] = None,
        gas: Optional[str] = None,
        sector: Optional[str] = None,
        min_value: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR grid emissions."""
        params = {
            'year': year,
            'gas': gas,
            'sector': sector,
            'min_value': min_value,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/grid-emissions/', params=params)

    async def get_edgar_temporal_profiles_async(
        self,
        sector: Optional[str] = None,
        temporal_level: Optional[str] = None,
        month: Optional[int] = None,
        hour: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR temporal profiles."""
        params = {
            'sector': sector,
            'temporal_level': temporal_level,
            'month': month,
            'hour': hour,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/temporal-profiles/', params=params)

    async def get_edgar_fasttrack_async(
        self,
        country_code: Optional[str] = None,
        year: Optional[int] = None,
        gas: Optional[str] = None,
        sector: Optional[str] = None,
        provisional: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR fasttrack data."""
        params = {
            'country_code': country_code,
            'year': year,
            'gas': gas,
            'sector': sector,
            'provisional': provisional,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/fasttrack/', params=params)
