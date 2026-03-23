"""Tests for eko_client.admin_client — EkoAdminClient endpoint methods."""

import pytest
import httpx
import respx
from datetime import datetime

from eko_client.admin_client import EkoAdminClient
from eko_client.user_client import EkoUserClient

BASE_URL = "https://test.jana.earth"
OK = {"results": [{"id": 1}], "count": 1}


def _client():
    return EkoAdminClient(base_url=BASE_URL, token="tok")


class TestAdminInheritance:

    def test_inherits_user_client(self):
        assert issubclass(EkoAdminClient, EkoUserClient)

    @respx.mock
    def test_can_call_user_methods(self):
        """Admin client inherits all EkoUserClient methods."""
        respx.get(f"{BASE_URL}/api/v1/esg/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = _client()
        result = client.get_health()
        assert result["status"] == "ok"
        client.close()


# ── Job Management ───────────────────────────────────────────────────────────

class TestJobManagement:

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_jobs(self):
        respx.get(f"{BASE_URL}/api/v1/management/jobs/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.list_jobs_async(
            data_source="openaq", job_type="ingest", status="active",
            is_active=True, limit=10,
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    def test_list_jobs_sync(self):
        respx.get(f"{BASE_URL}/api/v1/management/jobs/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = client.list_jobs(limit=10)
        assert result == OK
        client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_job(self):
        respx.get(f"{BASE_URL}/api/v1/management/jobs/5/").mock(
            return_value=httpx.Response(200, json={"id": 5})
        )
        client = _client()
        result = await client.get_job_async(5)
        assert result["id"] == 5
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_job(self):
        respx.post(f"{BASE_URL}/api/v1/management/jobs/").mock(
            return_value=httpx.Response(201, json={"id": 10})
        )
        client = _client()
        result = await client.create_job_async({"name": "test", "type": "ingest"})
        assert result["id"] == 10
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_update_job(self):
        respx.put(f"{BASE_URL}/api/v1/management/jobs/5/").mock(
            return_value=httpx.Response(200, json={"id": 5, "name": "updated"})
        )
        client = _client()
        result = await client.update_job_async(5, {"name": "updated"})
        assert result["name"] == "updated"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_delete_job(self):
        respx.delete(f"{BASE_URL}/api/v1/management/jobs/5/").mock(
            return_value=httpx.Response(204, json={})
        )
        client = _client()
        await client.delete_job_async(5)
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_trigger_job(self):
        respx.post(f"{BASE_URL}/api/v1/management/jobs/5/trigger/").mock(
            return_value=httpx.Response(200, json={"execution_id": "abc"})
        )
        client = _client()
        result = await client.trigger_job_async(5, override_config={"key": "val"})
        assert result["execution_id"] == "abc"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_trigger_job_no_config(self):
        respx.post(f"{BASE_URL}/api/v1/management/jobs/5/trigger/").mock(
            return_value=httpx.Response(200, json={"execution_id": "def"})
        )
        client = _client()
        result = await client.trigger_job_async(5)
        assert result["execution_id"] == "def"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_pause_job(self):
        respx.post(f"{BASE_URL}/api/v1/management/jobs/5/pause/").mock(
            return_value=httpx.Response(200, json={"status": "paused"})
        )
        client = _client()
        result = await client.pause_job_async(5)
        assert result["status"] == "paused"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_resume_job(self):
        respx.post(f"{BASE_URL}/api/v1/management/jobs/5/resume/").mock(
            return_value=httpx.Response(200, json={"status": "active"})
        )
        client = _client()
        result = await client.resume_job_async(5)
        assert result["status"] == "active"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_job_executions(self):
        respx.get(f"{BASE_URL}/api/v1/management/jobs/5/executions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.get_job_executions_async(5, status="completed", limit=10)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_job_stats(self):
        respx.get(f"{BASE_URL}/api/v1/management/jobs/5/stats/").mock(
            return_value=httpx.Response(200, json={"total_runs": 42})
        )
        client = _client()
        result = await client.get_job_stats_async(5)
        assert result["total_runs"] == 42
        await client.close_async()


# ── Execution Management ─────────────────────────────────────────────────────

class TestExecutionManagement:

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_executions(self):
        respx.get(f"{BASE_URL}/api/v1/management/executions/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.list_executions_async(
            job=5, status="completed",
            date_from=datetime(2024, 1, 1),
            date_to="2024-12-31",
        )
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_execution(self):
        respx.get(f"{BASE_URL}/api/v1/management/executions/10/").mock(
            return_value=httpx.Response(200, json={"id": 10})
        )
        client = _client()
        result = await client.get_execution_async(10)
        assert result["id"] == 10
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_execution_logs(self):
        respx.get(f"{BASE_URL}/api/v1/management/executions/10/logs/").mock(
            return_value=httpx.Response(200, json={"logs": ["line1"]})
        )
        client = _client()
        result = await client.get_execution_logs_async(10)
        assert "logs" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_cancel_execution(self):
        respx.post(f"{BASE_URL}/api/v1/management/executions/10/cancel/").mock(
            return_value=httpx.Response(200, json={"status": "cancelled"})
        )
        client = _client()
        result = await client.cancel_execution_async(10)
        assert result["status"] == "cancelled"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_retry_execution(self):
        respx.post(f"{BASE_URL}/api/v1/management/executions/10/retry/").mock(
            return_value=httpx.Response(200, json={"id": 11})
        )
        client = _client()
        result = await client.retry_execution_async(10)
        assert result["id"] == 11
        await client.close_async()


# ── Data Source Management ───────────────────────────────────────────────────

class TestDataSourceManagement:

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_data_sources(self):
        respx.get(f"{BASE_URL}/api/v1/management/data-sources/").mock(
            return_value=httpx.Response(200, json=OK)
        )
        client = _client()
        result = await client.list_data_sources_async(is_active=True, limit=10)
        assert result == OK
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_data_source(self):
        respx.get(f"{BASE_URL}/api/v1/management/data-sources/3/").mock(
            return_value=httpx.Response(200, json={"id": 3})
        )
        client = _client()
        result = await client.get_data_source_async(3)
        assert result["id"] == 3
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_data_source(self):
        respx.post(f"{BASE_URL}/api/v1/management/data-sources/").mock(
            return_value=httpx.Response(201, json={"id": 4})
        )
        client = _client()
        result = await client.create_data_source_async({"name": "new-source"})
        assert result["id"] == 4
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_update_data_source(self):
        respx.put(f"{BASE_URL}/api/v1/management/data-sources/3/").mock(
            return_value=httpx.Response(200, json={"id": 3, "name": "updated"})
        )
        client = _client()
        result = await client.update_data_source_async(3, {"name": "updated"})
        assert result["name"] == "updated"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_delete_data_source(self):
        respx.delete(f"{BASE_URL}/api/v1/management/data-sources/3/").mock(
            return_value=httpx.Response(204, json={})
        )
        client = _client()
        await client.delete_data_source_async(3)
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_check_data_source_health(self):
        respx.post(f"{BASE_URL}/api/v1/management/data-sources/3/check_health/").mock(
            return_value=httpx.Response(200, json={"healthy": True})
        )
        client = _client()
        result = await client.check_data_source_health_async(3)
        assert result["healthy"] is True
        await client.close_async()


# ── System Management ────────────────────────────────────────────────────────

class TestSystemManagement:

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_management_health(self):
        respx.get(f"{BASE_URL}/api/v1/management/health/").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = _client()
        result = await client.get_management_health_async()
        assert result["status"] == "ok"
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_management_summary(self):
        respx.get(f"{BASE_URL}/api/v1/management/summary/").mock(
            return_value=httpx.Response(200, json={"overview": {}})
        )
        client = _client()
        result = await client.get_management_summary_async()
        assert "overview" in result
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_database_performance(self):
        respx.get(f"{BASE_URL}/api/v1/management/database/performance/").mock(
            return_value=httpx.Response(200, json={"connections": 10})
        )
        client = _client()
        result = await client.get_database_performance_async()
        assert result["connections"] == 10
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_redis_performance(self):
        respx.get(f"{BASE_URL}/api/v1/management/redis/performance/").mock(
            return_value=httpx.Response(200, json={"used_memory": "50MB"})
        )
        client = _client()
        result = await client.get_redis_performance_async()
        assert "used_memory" in result
        await client.close_async()
