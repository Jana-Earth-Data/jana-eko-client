"""
Eko Admin Client - Admin client with full access including job management.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .user_client import EkoUserClient
from .sync_wrapper import auto_sync_wrapper


@auto_sync_wrapper
class EkoAdminClient(EkoUserClient):
    """
    Admin client for accessing all APIs including job management.

    This client extends EkoUserClient with job management, execution management,
    and data source management capabilities.

    All methods have both sync and async versions:
    - Async methods end with '_async' suffix (e.g., list_jobs_async)
    - Sync methods are auto-generated without the suffix (e.g., list_jobs)

    Example:
        >>> client = EkoAdminClient(base_url="http://localhost:8000", token="...")
        >>> jobs = client.list_jobs()  # Sync version (auto-generated)
        >>> jobs = await client.list_jobs_async()  # Async version
    """

    # =============================================================================
    # Job Management
    # =============================================================================

    async def list_jobs_async(
        self,
        data_source: Optional[str] = None,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List all jobs.

        Args:
            data_source: Filter by data source name
            job_type: Filter by job type
            status: Filter by status
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            List of jobs
        """
        params = {
            'data_source': data_source,
            'job_type': job_type,
            'status': status,
            'is_active': is_active,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/management/jobs/', params=params)

    async def get_job_async(self, job_id: int) -> Dict[str, Any]:
        """
        Get specific job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job details dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/'
        return await self._request_async('GET', endpoint)

    async def create_job_async(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job.

        Args:
            job_data: Job configuration dictionary

        Returns:
            Created job details dictionary
        """
        return await self._request_async('POST', '/api/v1/management/jobs/', json_data=job_data)

    async def update_job_async(self, job_id: int, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing job.

        Args:
            job_id: Job ID
            job_data: Updated job configuration dictionary

        Returns:
            Updated job details dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/'
        return await self._request_async('PUT', endpoint, json_data=job_data)

    async def delete_job_async(self, job_id: int) -> None:
        """
        Delete a job.

        Args:
            job_id: Job ID
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/'
        await self._request_async('DELETE', endpoint)

    async def trigger_job_async(self, job_id: int, override_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a job execution.

        Args:
            job_id: Job ID
            override_config: Optional configuration overrides

        Returns:
            Execution details dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/trigger/'
        json_data = {'override_config': override_config} if override_config else {}
        return await self._request_async('POST', endpoint, json_data=json_data)

    async def pause_job_async(self, job_id: int) -> Dict[str, Any]:
        """
        Pause a job.

        Args:
            job_id: Job ID

        Returns:
            Updated job details dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/pause/'
        return await self._request_async('POST', endpoint)

    async def resume_job_async(self, job_id: int) -> Dict[str, Any]:
        """
        Resume a paused job.

        Args:
            job_id: Job ID

        Returns:
            Updated job details dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/resume/'
        return await self._request_async('POST', endpoint)

    async def get_job_executions_async(
        self,
        job_id: int,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get executions for a specific job.

        Args:
            job_id: Job ID
            status: Filter by execution status
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            List of executions
        """
        params = {
            'status': status,
            'limit': limit,
            'offset': offset,
        }
        endpoint = f'/api/v1/management/jobs/{job_id}/executions/'
        return await self._request_async('GET', endpoint, params=params)

    async def get_job_stats_async(self, job_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific job.

        Args:
            job_id: Job ID

        Returns:
            Job statistics dictionary
        """
        endpoint = f'/api/v1/management/jobs/{job_id}/stats/'
        return await self._request_async('GET', endpoint)

    # =============================================================================
    # Execution Management
    # =============================================================================

    async def list_executions_async(
        self,
        job: Optional[int] = None,
        status: Optional[str] = None,
        trigger_type: Optional[str] = None,
        data_source: Optional[str] = None,
        date_from: Optional[Union[str, datetime]] = None,
        date_to: Optional[Union[str, datetime]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List all executions.

        Args:
            job: Filter by job ID
            status: Filter by execution status
            trigger_type: Filter by trigger type
            data_source: Filter by data source
            date_from: Filter by start date
            date_to: Filter by end date
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            List of executions
        """
        params = {
            'job': job,
            'status': status,
            'trigger_type': trigger_type,
            'data_source': data_source,
            'date_from': date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            'date_to': date_to.isoformat() if isinstance(date_to, datetime) else date_to,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/management/executions/', params=params)

    async def get_execution_async(self, execution_id: int) -> Dict[str, Any]:
        """
        Get specific execution by ID (uses primary key, not UUID).

        Args:
            execution_id: Execution primary key ID

        Returns:
            Execution details dictionary
        """
        endpoint = f'/api/v1/management/executions/{execution_id}/'
        return await self._request_async('GET', endpoint)

    async def get_execution_logs_async(self, execution_id: int) -> Dict[str, Any]:
        """
        Get logs for a specific execution.

        Args:
            execution_id: Execution primary key ID

        Returns:
            Execution logs dictionary
        """
        endpoint = f'/api/v1/management/executions/{execution_id}/logs/'
        return await self._request_async('GET', endpoint)

    async def cancel_execution_async(self, execution_id: int) -> Dict[str, Any]:
        """
        Cancel a running execution.

        Args:
            execution_id: Execution primary key ID

        Returns:
            Updated execution details dictionary
        """
        endpoint = f'/api/v1/management/executions/{execution_id}/cancel/'
        return await self._request_async('POST', endpoint)

    async def retry_execution_async(self, execution_id: int) -> Dict[str, Any]:
        """
        Retry a failed execution.

        Args:
            execution_id: Execution primary key ID

        Returns:
            New execution details dictionary
        """
        endpoint = f'/api/v1/management/executions/{execution_id}/retry/'
        return await self._request_async('POST', endpoint)

    # =============================================================================
    # Data Source Management
    # =============================================================================

    async def list_data_sources_async(
        self,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List all data sources.

        Args:
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Result offset for pagination

        Returns:
            List of data sources
        """
        params = {
            'is_active': is_active,
            'limit': limit,
            'offset': offset,
        }
        return await self._request_async('GET', '/api/v1/management/data-sources/', params=params)

    async def get_data_source_async(self, source_id: int) -> Dict[str, Any]:
        """
        Get specific data source by ID.

        Args:
            source_id: Data source ID

        Returns:
            Data source details dictionary
        """
        endpoint = f'/api/v1/management/data-sources/{source_id}/'
        return await self._request_async('GET', endpoint)

    async def create_data_source_async(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new data source.

        Args:
            source_data: Data source configuration dictionary

        Returns:
            Created data source details dictionary
        """
        return await self._request_async('POST', '/api/v1/management/data-sources/', json_data=source_data)

    async def update_data_source_async(self, source_id: int, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing data source.

        Args:
            source_id: Data source ID
            source_data: Updated data source configuration dictionary

        Returns:
            Updated data source details dictionary
        """
        endpoint = f'/api/v1/management/data-sources/{source_id}/'
        return await self._request_async('PUT', endpoint, json_data=source_data)

    async def delete_data_source_async(self, source_id: int) -> None:
        """
        Delete a data source.

        Args:
            source_id: Data source ID
        """
        endpoint = f'/api/v1/management/data-sources/{source_id}/'
        await self._request_async('DELETE', endpoint)

    async def check_data_source_health_async(self, source_id: int) -> Dict[str, Any]:
        """
        Check health of a data source.

        Args:
            source_id: Data source ID

        Returns:
            Health check results dictionary
        """
        endpoint = f'/api/v1/management/data-sources/{source_id}/check_health/'
        return await self._request_async('POST', endpoint)

    # =============================================================================
    # System Management
    # =============================================================================

    async def get_management_health_async(self) -> Dict[str, Any]:
        """
        Get management API health check.

        Returns:
            Health response dictionary
        """
        return await self._request_async('GET', '/api/v1/management/health/')

    async def get_management_summary_async(self) -> Dict[str, Any]:
        """
        Get management dashboard summary.

        Returns:
            Management summary dictionary
        """
        return await self._request_async('GET', '/api/v1/management/summary/')

    async def get_database_performance_async(self) -> Dict[str, Any]:
        """
        Get database performance metrics.

        Returns:
            Database performance dictionary
        """
        return await self._request_async('GET', '/api/v1/management/database/performance/')

    async def get_redis_performance_async(self) -> Dict[str, Any]:
        """
        Get Redis performance metrics.

        Returns:
            Redis performance dictionary
        """
        return await self._request_async('GET', '/api/v1/management/redis/performance/')
