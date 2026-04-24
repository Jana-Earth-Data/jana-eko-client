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

    This client provides access to all unified data endpoints.

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

    # =============================================================================
    # Geographic & Spatial
    # =============================================================================

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
        # Jana API: GET /api/v1/esg/exports/<uuid>/ (no /status/ suffix)
        endpoint = f'/api/v1/esg/exports/{export_id}/'
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
        country_codes: Optional[Union[List[str], str]] = None,
        location_bbox: Optional[List[float]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ locations.

        Args:
            country_codes: Country code(s) — single string or list (e.g. 'US' or ['US', 'GB']).
            location_bbox: Geographic bounding box [min_lon, min_lat, max_lon, max_lat].
            page: Page number (1-based).
            page_size: Number of results per page.
            limit: Alias for page_size (backward compatibility).
            offset: Result offset (backward compatibility).
        """
        # Normalize single string to list for consistent handling
        if isinstance(country_codes, str):
            country_codes = [country_codes]
        params = {
            'country_codes': country_codes,
            'location_bbox': location_bbox,
            'page': page,
            'page_size': page_size or limit,
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
        country_code: Optional[str] = None,
        location_bbox: Optional[List[float]] = None,
        coordinates: Optional[List[float]] = None,
        radius_km: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ sensors.

        Args:
            location_id: Filter by location FK ID.
            parameter: Filter by parameter name.
            country_code: Filter by country ISO3 code.
            location_bbox: Bounding box [min_lon, min_lat, max_lon, max_lat].
            coordinates: Point [lon, lat] (requires radius_km).
            radius_km: Radius in km around *coordinates*.
            limit: Max results to return.
            offset: Pagination offset.
        """
        bbox_str = ','.join(str(v) for v in location_bbox) if location_bbox else None
        coords_str = ','.join(str(v) for v in coordinates) if coordinates else None
        params = {
            'location_id': location_id,
            'parameter__name': parameter,
            'location__country_code': country_code,
            'bbox': bbox_str,
            'coordinates': coords_str,
            'radius': radius_km,
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
        country_code: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get OpenAQ measurements.

        Args:
            location_id: Filter by location ID.
            parameter: Filter by parameter name (e.g. 'pm25', 'o3').
            date_from: Start date (ISO 8601 string or datetime).
            date_to: End date (ISO 8601 string or datetime).
            country_code: Filter by country code (e.g. 'US').
            ordering: Sort field (e.g. 'measured_at', '-measured_at').
            page: Page number (1-based, used with page_size).
            page_size: Number of results per page.
            limit: Alias for page_size (backward compatibility).
            offset: Result offset (backward compatibility).
        """
        params = {
            'location_id': location_id,
            'parameter_name': parameter,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'location__country_code': country_code,
            'ordering': ordering,
            'page': page,
            'page_size': page_size or limit,
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
        legal_entity_lei: Optional[str] = None,
        company_id: Optional[str] = None,
        matching_method: Optional[str] = None,
        relationship_type: Optional[str] = None,
        verified: Optional[bool] = None,
        search: Optional[str] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE company-asset matches.

        Links between Climate TRACE emission-producing assets and GLEIF
        legal entities (companies/organizations).

        Args:
            legal_entity_lei: Filter by GLEIF Legal Entity Identifier (20-char LEI).
            company_id: Filter by internal company identifier.
            matching_method: Filter by how the match was established
                (e.g. 'exact_name', 'fuzzy_name').
            relationship_type: Filter by relationship type
                (e.g. 'owner', 'operator', 'parent').
            verified: Filter by verification status (True/False).
            search: Full-text search across asset name, owner name, and
                legal entity name.
            ordering: Sort field. Options: 'matching_confidence',
                '-matching_confidence', 'created_at', '-created_at'.
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with 'count', 'next', 'previous', and
            'results' keys.  Each result includes asset details and,
            when linked, ``legal_entity_lei`` and ``legal_entity_name``.
        """
        params = {
            'legal_entity_lei': legal_entity_lei,
            'company_id': company_id,
            'matching_method': matching_method,
            'relationship_type': relationship_type,
            'verified': verified,
            'search': search,
            'ordering': ordering,
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
        bbox: Optional[str] = None,
        coordinates: Optional[str] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR grid emissions.

        Args:
            year: Filter by year (e.g. 2022). At least one filter required.
            gas: Filter by gas type (e.g. 'CO2', 'CH4').
            sector: Filter by EDGAR sector code.
            min_value: Minimum emission value threshold.
            bbox: Bounding box as 'min_lon,min_lat,max_lon,max_lat'.
            coordinates: Point as 'lon,lat' (requires radius).
            radius: Radius in km around coordinates point.
            limit: Results per page.
            offset: Pagination offset.
        """
        params = {
            'year': year,
            'gas': gas,
            'sector': sector,
            'min_value': min_value,
            'bbox': bbox,
            'coordinates': coordinates,
            'radius': radius,
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

    # ── GLEIF Methods ──────────────────────────────────────────────────

    async def get_gleif_entities_async(
        self,
        search: Optional[str] = None,
        entity_status: Optional[str] = None,
        registration_status: Optional[str] = None,
        entity_category: Optional[str] = None,
        legal_address_country: Optional[str] = None,
        headquarters_country: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GLEIF legal entities.

        Args:
            search: Search by legal_name, LEI, BIC, or registered_as.
            entity_status: Filter by entity status (ACTIVE, INACTIVE).
            registration_status: Filter by registration status (ISSUED, LAPSED, RETIRED, etc.).
            entity_category: Filter by category (GENERAL, FUND, BRANCH, etc.).
            legal_address_country: Filter by legal address country (ISO 3166-1 alpha-2).
            headquarters_country: Filter by headquarters country (ISO 3166-1 alpha-2).
            jurisdiction: Filter by jurisdiction (ISO 3166-1/2).
            ordering: Sort field (legal_name, last_update_date, entity_creation_date).
            limit: Results per page.
            offset: Pagination offset.
        """
        params = {
            'search': search,
            'entity_status': entity_status,
            'registration_status': registration_status,
            'entity_category': entity_category,
            'legal_address_country': legal_address_country,
            'headquarters_country': headquarters_country,
            'jurisdiction': jurisdiction,
            'ordering': ordering,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gleif/entities/', params=params)

    async def get_gleif_entity_async(
        self,
        lei: str,
    ) -> Dict[str, Any]:
        """Get a single GLEIF legal entity by LEI.

        Args:
            lei: The 20-character Legal Entity Identifier.
        """
        return await self._request_async('GET', f'/api/v1/data-sources/gleif/entities/{lei}/')

    async def get_gleif_entity_parents_async(
        self,
        lei: str,
    ) -> Dict[str, Any]:
        """Get direct and ultimate parent entities for a given LEI.

        Args:
            lei: The 20-character Legal Entity Identifier.

        Returns:
            Dict with 'direct_parent' and 'ultimate_parent' keys (each null or entity object).
        """
        return await self._request_async('GET', f'/api/v1/data-sources/gleif/entities/{lei}/parents/')

    async def get_gleif_entity_children_async(
        self,
        lei: str,
    ) -> List:
        """Get direct child entities (subsidiaries) for a given LEI.

        Args:
            lei: The 20-character Legal Entity Identifier.

        Returns:
            List of child entity objects.
        """
        return await self._request_async('GET', f'/api/v1/data-sources/gleif/entities/{lei}/children/')

    async def get_gleif_relationships_async(
        self,
        start_lei: Optional[str] = None,
        end_lei: Optional[str] = None,
        relationship_type: Optional[str] = None,
        relationship_status: Optional[str] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GLEIF entity relationships.

        Args:
            start_lei: Filter by child entity LEI.
            end_lei: Filter by parent entity LEI.
            relationship_type: Filter by type (IS_DIRECTLY_CONSOLIDATED_BY,
                IS_ULTIMATELY_CONSOLIDATED_BY, IS_FEEDER_TO, IS_FUND-MANAGED_BY).
            relationship_status: Filter by status (ACTIVE, INACTIVE).
            ordering: Sort field (start_lei, end_lei, ingested_at).
            limit: Results per page.
            offset: Pagination offset.
        """
        params = {
            'start_lei': start_lei,
            'end_lei': end_lei,
            'relationship_type': relationship_type,
            'relationship_status': relationship_status,
            'ordering': ordering,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gleif/relationships/', params=params)

    async def get_gleif_exceptions_async(
        self,
        lei: Optional[str] = None,
        exception_category: Optional[str] = None,
        exception_reason: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GLEIF reporting exceptions.

        Args:
            lei: Filter by entity LEI.
            exception_category: Filter by category (DIRECT_ACCOUNTING_CONSOLIDATION_PARENT,
                ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT).
            exception_reason: Filter by reason (NON_CONSOLIDATING, NO_KNOWN_PERSON,
                NO_LEI, NATURAL_PERSONS, etc.).
            limit: Results per page.
            offset: Pagination offset.
        """
        params = {
            'lei': lei,
            'exception_category': exception_category,
            'exception_reason': exception_reason,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gleif/exceptions/', params=params)

    # ── GCP (Global Carbon Project) Methods ───────────────────────────

    async def get_gcp_national_emissions_async(
        self,
        country_code: Optional[str] = None,
        year: Optional[int] = None,
        budget_version: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GCP national CO2 emissions.

        Returns territorial and consumption-based CO2 emissions by country
        and year, including per-capita values.

        Args:
            country_code: ISO-3 country code (e.g. 'USA', 'CHN', 'IND').
            year: Emission year (e.g. 2020).
            budget_version: GCP budget version (e.g. '2024').
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with national emissions records.
        """
        params = {
            'country_code': country_code,
            'year': year,
            'budget_version': budget_version,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gcp/national-emissions/', params=params)

    async def get_gcp_emissions_by_fuel_async(
        self,
        year: Optional[int] = None,
        budget_version: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GCP global fossil CO2 emissions by fuel type.

        Returns emissions from coal, oil, gas, cement, flaring, and other
        sources by year.

        Args:
            year: Emission year (e.g. 2020).
            budget_version: GCP budget version (e.g. '2024').
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with fuel-type emission records.
        """
        params = {
            'year': year,
            'budget_version': budget_version,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gcp/emissions-by-fuel/', params=params)

    async def get_gcp_carbon_budget_async(
        self,
        year: Optional[int] = None,
        budget_version: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GCP global carbon budget.

        Returns global carbon budget components (fossil emissions, land-use
        change, atmospheric growth, ocean sink, land sink) by year.

        Args:
            year: Budget year (e.g. 2020).
            budget_version: GCP budget version (e.g. '2024').
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with carbon budget records.
        """
        params = {
            'year': year,
            'budget_version': budget_version,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gcp/carbon-budget/', params=params)

    async def get_gcp_methane_budget_async(
        self,
        year: Optional[int] = None,
        budget_version: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get GCP global methane budget.

        Returns methane budget components (anthropogenic and natural sources
        and sinks) by year.

        Args:
            year: Budget year (e.g. 2020).
            budget_version: GCP budget version (e.g. '2024').
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with methane budget records.
        """
        params = {
            'year': year,
            'budget_version': budget_version,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/gcp/methane-budget/', params=params)

    # ── NOAA Storm Events Methods ─────────────────────────────────────

    async def get_noaa_storm_events_async(
        self,
        event_type: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        bbox: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get NOAA severe weather events.

        Returns storm event records across the United States including
        tornadoes, hurricanes, floods, hail, thunderstorms, winter storms,
        and more.

        Args:
            event_type: Storm event type (e.g. 'Tornado', 'Hurricane',
                'Flood', 'Hail', 'Thunderstorm Wind', 'Winter Storm').
            state: US state name in uppercase (e.g. 'TEXAS', 'FLORIDA').
            year: Event year (2015-2024 available).
            month: Event month (1-12).
            bbox: Bounding box as 'min_lat,min_lon,max_lat,max_lon'.
            lat: Latitude for point+radius search (-90 to 90).
            lon: Longitude for point+radius search (-180 to 180).
            radius_km: Search radius in km (requires lat and lon).
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with storm event records including
            event type, location, dates, damage, injuries, and deaths.
        """
        params = {
            'event_type': event_type,
            'state': state,
            'year': year,
            'month': month,
            'bbox': bbox,
            'lat': lat,
            'lon': lon,
            'radius_km': radius_km,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/noaa_storm_events/events/', params=params)

    # ── OpenAQ Detail Actions ─────────────────────────────────────────

    async def get_openaq_location_sensors_async(self, location_id: int) -> Dict[str, Any]:
        """Get all sensors for an OpenAQ location.

        Args:
            location_id: Location ID.

        Returns:
            List of sensor records for the location.
        """
        endpoint = f'/api/v1/data-sources/openaq/locations/{location_id}/sensors/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_location_flags_async(self, location_id: int) -> Dict[str, Any]:
        """Get data quality flags for an OpenAQ location.

        Args:
            location_id: Location ID.

        Returns:
            Quality flags from OpenAQ upstream (cached 15 min).
        """
        endpoint = f'/api/v1/data-sources/openaq/locations/{location_id}/flags/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_location_latest_measurements_async(
        self,
        location_id: int,
        datetime_min: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get latest measurements for an OpenAQ location.

        Args:
            location_id: Location ID.
            datetime_min: Minimum datetime filter (ISO 8601).

        Returns:
            List of latest measurement summaries per sensor.
        """
        endpoint = f'/api/v1/data-sources/openaq/locations/{location_id}/latest_measurements/'
        params = {'datetime_min': datetime_min}
        return await self._request_async('GET', endpoint, params=params)

    async def get_openaq_sensor_measurements_async(
        self,
        sensor_id: int,
        limit: Optional[int] = None,
        days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get recent measurements for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.
            limit: Maximum number of measurements (default 100).
            days: Number of days to look back (default 7).

        Returns:
            List of measurement summaries.
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/measurements/'
        params = {'limit': limit, 'days': days}
        return await self._request_async('GET', endpoint, params=params)

    async def get_openaq_sensor_flags_async(self, sensor_id: int) -> Dict[str, Any]:
        """Get data quality flags for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.

        Returns:
            Quality flags from OpenAQ upstream (cached 15 min).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/flags/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_sensor_hourly_async(
        self,
        sensor_id: int,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """Get hourly aggregated data for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.
            date_from: Start date (ISO 8601 or datetime).
            date_to: End date (ISO 8601 or datetime).

        Returns:
            Hourly aggregated data from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/hourly/'
        params = {
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', endpoint, params=params)

    async def get_openaq_sensor_daily_async(
        self,
        sensor_id: int,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """Get daily aggregated data for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.
            date_from: Start date (ISO 8601 or datetime).
            date_to: End date (ISO 8601 or datetime).

        Returns:
            Daily aggregated data from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/daily/'
        params = {
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', endpoint, params=params)

    async def get_openaq_sensor_yearly_async(
        self,
        sensor_id: int,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """Get yearly aggregated data for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.
            date_from: Start date (ISO 8601 or datetime).
            date_to: End date (ISO 8601 or datetime).

        Returns:
            Yearly aggregated data from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/yearly/'
        params = {
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        return await self._request_async('GET', endpoint, params=params)

    async def get_openaq_sensor_hour_of_day_async(self, sensor_id: int) -> Dict[str, Any]:
        """Get hour-of-day aggregated pattern for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.

        Returns:
            Hour-of-day aggregation from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/hour-of-day/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_sensor_day_of_week_async(self, sensor_id: int) -> Dict[str, Any]:
        """Get day-of-week aggregated pattern for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.

        Returns:
            Day-of-week aggregation from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/day-of-week/'
        return await self._request_async('GET', endpoint)

    async def get_openaq_sensor_month_of_year_async(self, sensor_id: int) -> Dict[str, Any]:
        """Get month-of-year aggregated pattern for an OpenAQ sensor.

        Args:
            sensor_id: Sensor ID.

        Returns:
            Month-of-year aggregation from OpenAQ upstream (cached 1 hour).
        """
        endpoint = f'/api/v1/data-sources/openaq/sensors/{sensor_id}/month-of-year/'
        return await self._request_async('GET', endpoint)

    # ── OpenAQ Reference Data ─────────────────────────────────────────

    async def get_openaq_providers_async(self) -> Dict[str, Any]:
        """Get OpenAQ data providers (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/providers/')

    async def get_openaq_owners_async(self) -> Dict[str, Any]:
        """Get OpenAQ station owners (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/owners/')

    async def get_openaq_manufacturers_async(self) -> Dict[str, Any]:
        """Get OpenAQ instrument manufacturers (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/manufacturers/')

    async def get_openaq_instruments_async(self) -> Dict[str, Any]:
        """Get OpenAQ instruments (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/instruments/')

    async def get_openaq_licenses_async(self) -> Dict[str, Any]:
        """Get OpenAQ data licenses (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/licenses/')

    async def get_openaq_stats_async(self) -> Dict[str, Any]:
        """Get OpenAQ data statistics (record counts, coverage, etc.)."""
        return await self._request_async('GET', '/api/v1/data-sources/openaq/stats/')

    # ── Climate TRACE Detail Actions ──────────────────────────────────

    async def get_climatetrace_sector_assets_async(
        self,
        sector_id: int,
    ) -> Dict[str, Any]:
        """Get assets for a Climate TRACE sector.

        Args:
            sector_id: Sector ID.

        Returns:
            List of asset records for the sector (limit 100).
        """
        endpoint = f'/api/v1/data-sources/climatetrace/sectors/{sector_id}/assets/'
        return await self._request_async('GET', endpoint)

    async def get_climatetrace_sector_emissions_summary_async(
        self,
        sector_id: int,
    ) -> Dict[str, Any]:
        """Get emissions summary for a Climate TRACE sector.

        Args:
            sector_id: Sector ID.

        Returns:
            Aggregated data (total_assets, total_co2e_tonnes, avg_co2e_tonnes).
        """
        endpoint = f'/api/v1/data-sources/climatetrace/sectors/{sector_id}/emissions_summary/'
        return await self._request_async('GET', endpoint)

    async def get_climatetrace_country_assets_async(
        self,
        country_id: int,
    ) -> Dict[str, Any]:
        """Get assets for a Climate TRACE country.

        Args:
            country_id: Country ID.

        Returns:
            List of asset records for the country (limit 100).
        """
        endpoint = f'/api/v1/data-sources/climatetrace/countries/{country_id}/assets/'
        return await self._request_async('GET', endpoint)

    async def get_climatetrace_asset_emissions_async(
        self,
        asset_id: int,
    ) -> Dict[str, Any]:
        """Get emissions for a Climate TRACE asset.

        Args:
            asset_id: Asset ID.

        Returns:
            List of emission records for the asset (limit 100).
        """
        endpoint = f'/api/v1/data-sources/climatetrace/assets/{asset_id}/emissions/'
        return await self._request_async('GET', endpoint)

    async def get_climatetrace_asset_violations_async(
        self,
        asset_id: int,
    ) -> Dict[str, Any]:
        """Get emission violations for a Climate TRACE asset.

        Args:
            asset_id: Asset ID.

        Returns:
            List of violation records for the asset.
        """
        endpoint = f'/api/v1/data-sources/climatetrace/assets/{asset_id}/violations/'
        return await self._request_async('GET', endpoint)

    async def get_climatetrace_aggregated_emissions_async(
        self,
        countries: Optional[str] = None,
        sectors: Optional[str] = None,
        subsectors: Optional[str] = None,
        continents: Optional[str] = None,
        groups: Optional[str] = None,
        gas: Optional[str] = None,
        years: Optional[str] = None,
        bbox: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get aggregated emissions from Climate TRACE upstream API.

        Proxies to Climate TRACE v6 assets/emissions endpoint with server-side
        caching (15 min).

        Args:
            countries: Comma-separated country codes.
            sectors: Comma-separated sector names.
            subsectors: Comma-separated subsector names.
            continents: Comma-separated continent names.
            groups: Comma-separated group names.
            gas: Gas type filter.
            years: Comma-separated years.
            bbox: Bounding box as 'min_lon,min_lat,max_lon,max_lat'.

        Returns:
            Aggregated emissions data from Climate TRACE.
        """
        params = {
            'countries': countries,
            'sectors': sectors,
            'subsectors': subsectors,
            'continents': continents,
            'groups': groups,
            'gas': gas,
            'years': years,
            'bbox': bbox,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/emissions/aggregated-emissions/', params=params)

    # ── Climate TRACE Annual Country Emissions ────────────────────────

    async def get_climatetrace_annual_country_emissions_async(
        self,
        country_iso3: Optional[str] = None,
        year: Optional[int] = None,
        sector: Optional[str] = None,
        gas_type: Optional[str] = None,
        search: Optional[str] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Climate TRACE annual country-level emissions.

        Args:
            country_iso3: ISO-3 country code (e.g. 'USA').
            year: Emission year.
            sector: Sector name filter.
            gas_type: Gas type filter.
            search: Search country_name or country_iso3.
            ordering: Sort field (year, emissions_quantity, country_iso3).
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with annual country emission records.
        """
        params = {
            'country_iso3': country_iso3,
            'year': year,
            'sector': sector,
            'gas_type': gas_type,
            'search': search,
            'ordering': ordering,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/annual-country-emissions/', params=params)

    # ── Climate TRACE Definitions ─────────────────────────────────────

    async def get_climatetrace_definition_subsectors_async(self) -> Dict[str, Any]:
        """Get Climate TRACE subsector definitions (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/definitions/subsectors/')

    async def get_climatetrace_definition_groups_async(self) -> Dict[str, Any]:
        """Get Climate TRACE group definitions (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/definitions/groups/')

    async def get_climatetrace_definition_continents_async(self) -> Dict[str, Any]:
        """Get Climate TRACE continent definitions (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/definitions/continents/')

    async def get_climatetrace_definition_gases_async(self) -> Dict[str, Any]:
        """Get Climate TRACE gas type definitions (cached 24 hours)."""
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/definitions/gases/')

    # ── Climate TRACE Admin Areas ─────────────────────────────────────

    async def get_climatetrace_admin_areas_search_async(
        self,
        query: Optional[str] = None,
        point: Optional[str] = None,
        bbox: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search Climate TRACE administrative areas.

        Args:
            query: Text search query.
            point: Point as 'lon,lat'.
            bbox: Bounding box as 'min_lon,min_lat,max_lon,max_lat'.
            level: Admin level filter.

        Returns:
            Matching administrative areas from Climate TRACE upstream.
        """
        params = {
            'query': query,
            'point': point,
            'bbox': bbox,
            'level': level,
        }
        return await self._request_async('GET', '/api/v1/data-sources/climatetrace/admin-areas/search/', params=params)

    async def get_climatetrace_admin_area_geojson_async(
        self,
        admin_id: str,
    ) -> Dict[str, Any]:
        """Get GeoJSON boundary for a Climate TRACE administrative area.

        Args:
            admin_id: Administrative area ID.

        Returns:
            GeoJSON geometry from Climate TRACE upstream (cached 7 days).
        """
        endpoint = f'/api/v1/data-sources/climatetrace/admin-areas/{admin_id}/geojson/'
        return await self._request_async('GET', endpoint)

    # ── EDGAR Air Pollutant Endpoints ─────────────────────────────────

    async def get_edgar_air_pollutant_totals_async(
        self,
        country_code: Optional[str] = None,
        year: Optional[int] = None,
        gas: Optional[str] = None,
        sector: Optional[str] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR air pollutant country totals.

        Args:
            country_code: ISO-3 country code (e.g. 'USA').
            year: Emission year.
            gas: Pollutant type (e.g. 'NOx', 'SO2', 'CO', 'PM2.5').
            sector: EDGAR sector code.
            ordering: Sort field (country_code, year, gas, sector, value, ingested_at).
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response (cursor-based) with air pollutant total records.
        """
        params = {
            'country_code': country_code,
            'year': year,
            'gas': gas,
            'sector': sector,
            'ordering': ordering,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/air-pollutant-totals/', params=params)

    async def get_edgar_air_pollutant_grid_async(
        self,
        year: Optional[int] = None,
        gas: Optional[str] = None,
        sector: Optional[str] = None,
        bbox: Optional[str] = None,
        coordinates: Optional[str] = None,
        radius: Optional[float] = None,
        ordering: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get EDGAR air pollutant grid emissions.

        At least one filter (year, gas, sector, bbox, or coordinates) is required;
        returns empty results otherwise.

        Args:
            year: Emission year.
            gas: Pollutant type (e.g. 'NOx', 'SO2', 'CO', 'PM2.5').
            sector: EDGAR sector code.
            bbox: Bounding box as 'min_lon,min_lat,max_lon,max_lat'.
            coordinates: Point as 'lon,lat' (requires radius).
            radius: Radius in km around coordinates point.
            ordering: Sort field (year, gas, sector, value, latitude, longitude, ingested_at).
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response (cursor-based) with air pollutant grid records.
        """
        params = {
            'year': year,
            'gas': gas,
            'sector': sector,
            'bbox': bbox,
            'coordinates': coordinates,
            'radius': radius,
            'ordering': ordering,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/data-sources/edgar/air-pollutant-grid/', params=params)

    # ── ESG Analytics & Statistics ────────────────────────────────────

    async def get_analytics_async(
        self,
        country_codes: List[str],
        temporal_window_days: Optional[int] = None,
        correlation_threshold: Optional[float] = None,
        minimum_data_points: Optional[int] = None,
        include_openaq: Optional[bool] = None,
        include_climatetrace: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get cross-source correlation analytics.

        Computes correlations between air quality and emissions data
        (e.g. PM2.5 vs CO2e) for the specified countries.

        Args:
            country_codes: ISO 3-letter country codes (required).
            temporal_window_days: Window for temporal correlation.
            correlation_threshold: Minimum correlation coefficient to include.
            minimum_data_points: Minimum data points required.
            include_openaq: Include OpenAQ data (default True).
            include_climatetrace: Include Climate TRACE data (default True).

        Returns:
            Cross-source correlation analytics response.
        """
        params = {
            'country_codes': country_codes,
            'temporal_window_days': temporal_window_days,
            'correlation_threshold': correlation_threshold,
            'minimum_data_points': minimum_data_points,
            'include_openaq': include_openaq,
            'include_climatetrace': include_climatetrace,
        }
        return await self._request_async('GET', '/api/v1/esg/analytics/', params=params)

    async def get_openaq_statistics_async(
        self,
        country_codes: List[str],
    ) -> Dict[str, Any]:
        """Get OpenAQ-specific statistics for given countries.

        Args:
            country_codes: ISO 3-letter country codes (required).

        Returns:
            OpenAQ statistics (location counts, parameter coverage, etc.).
        """
        params = {'country_codes': country_codes}
        return await self._request_async('GET', '/api/v1/esg/openaq-statistics/', params=params)

    async def get_climatetrace_statistics_async(
        self,
        country_codes: List[str],
    ) -> Dict[str, Any]:
        """Get Climate TRACE-specific statistics for given countries.

        Args:
            country_codes: ISO 3-letter country codes (required).

        Returns:
            Climate TRACE statistics (asset counts, sector breakdown, etc.).
        """
        params = {'country_codes': country_codes}
        return await self._request_async('GET', '/api/v1/esg/climatetrace-statistics/', params=params)

    async def get_table_statistics_async(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get table-level statistics across all data sources.

        Returns record counts, date ranges, and coverage for each data table.

        Args:
            limit: Results per page.
            offset: Pagination offset.

        Returns:
            Paginated response with table statistics.
        """
        params = {'limit': limit, 'offset': offset}
        return await self._request_async('GET', '/api/v1/esg/statistics/', params=params)

    async def export_data_sync_async(
        self,
        sources: Optional[List[str]] = None,
        country_codes: Optional[List[str]] = None,
        location_bbox: Optional[List[float]] = None,
        location_point: Optional[List[float]] = None,
        radius_km: Optional[float] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        parameters: Optional[List[str]] = None,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get synchronous data export (for smaller datasets).

        Unlike create_export_async which is asynchronous, this returns data
        directly in the response. A geographic filter is required.

        Args:
            sources: Data sources to include.
            country_codes: ISO 3-letter country codes.
            location_bbox: Bounding box [min_lon, min_lat, max_lon, max_lat].
            location_point: Point coordinates [longitude, latitude].
            radius_km: Search radius in km.
            date_from: Start date (ISO 8601 or datetime).
            date_to: End date (ISO 8601 or datetime).
            parameters: Environmental parameters to include.
            output_format: Response format (json, csv).

        Returns:
            Exported data response.
        """
        params = {
            'sources': sources,
            'country_codes': country_codes,
            'location_bbox': location_bbox,
            'location_point': location_point,
            'radius_km': radius_km,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'parameters': parameters,
            'output_format': output_format,
        }
        return await self._request_async('GET', '/api/v1/esg/export/', params=params)

    # ── GLEIF Detail Actions ──────────────────────────────────────────

    async def get_gleif_entity_asset_matches_async(
        self,
        lei: str,
    ) -> Dict[str, Any]:
        """Get Climate TRACE asset matches for a GLEIF legal entity.

        Returns assets linked to the entity, ordered by matching confidence.

        Args:
            lei: The 20-character Legal Entity Identifier.

        Returns:
            List of company-asset match records with asset details.
        """
        endpoint = f'/api/v1/data-sources/gleif/entities/{lei}/asset-matches/'
        return await self._request_async('GET', endpoint)
