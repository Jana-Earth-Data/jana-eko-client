"""Tests for BaseEkoClient.fetch_all_pages and fetch_all_pages_async."""

import pytest
import httpx
import respx

from eko_client.client import BaseEkoClient

BASE_URL = "https://test.jana.earth"


def _page(results, count=None, next_url=None):
    """Build a paginated response dict."""
    d = {"results": results}
    if count is not None:
        d["count"] = count
    if next_url is not None:
        d["next"] = next_url
    return d


# ── fetch_all_pages (sync) ───────────────────────────────────────────────────

class TestFetchAllPagesSync:

    @respx.mock
    def test_single_page_with_count(self):
        """Page-number pagination: one page, count present."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}, {"id": 2}], count=2,
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/", page_size=100)
        assert len(results) == 2
        assert results[0]["id"] == 1
        client.close()

    @respx.mock
    def test_multi_page_with_count(self):
        """Page-number pagination: two pages via next URL."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": 1}], count=2,
                    next_url=f"{BASE_URL}/api/v1/data/?page=2&page_size=1",
                )),
                httpx.Response(200, json=_page(
                    [{"id": 2}], count=2,
                )),
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/", page_size=1)
        assert len(results) == 2
        client.close()

    @respx.mock
    def test_cursor_pagination_no_count(self):
        """Cursor pagination: no count field, uses next URL."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": 1}],
                    next_url=f"{BASE_URL}/api/v1/data/?cursor=abc",
                )),
                httpx.Response(200, json=_page([{"id": 2}])),
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/", page_size=1)
        assert len(results) == 2
        client.close()

    @respx.mock
    def test_empty_first_page(self):
        """Empty results on first page returns empty list."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([], count=0))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/")
        assert results == []
        client.close()

    @respx.mock
    def test_max_pages_limit(self, capsys):
        """Stops at max_pages even if more data exists."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": i}],
                    next_url=f"{BASE_URL}/api/v1/data/?cursor=page{i+1}",
                ))
                for i in range(5)
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages(
            "/api/v1/data/", page_size=1, max_pages=3, progress=True,
        )
        assert len(results) == 3
        captured = capsys.readouterr()
        assert "max page limit" in captured.out.lower()
        client.close()

    @respx.mock
    def test_sends_both_page_size_and_limit(self):
        """Verify first request sends both page_size and limit params."""
        route = respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([], count=0))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.fetch_all_pages("/api/v1/data/", page_size=500)
        req = route.calls[0].request
        assert "page_size" in str(req.url)
        assert "limit" in str(req.url)
        client.close()

    @respx.mock
    def test_preserves_existing_params(self):
        """User-supplied params are preserved and not overwritten."""
        route = respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([], count=0))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.fetch_all_pages(
            "/api/v1/data/",
            params={"country_code": "NPL", "page_size": 50},
            page_size=1000,
        )
        req = route.calls[0].request
        url_str = str(req.url)
        assert "country_code=NPL" in url_str
        # User's page_size=50 takes precedence over the default 1000
        assert "page_size=50" in url_str
        client.close()

    @respx.mock
    def test_progress_output_page_number(self, capsys):
        """Progress output for page-number pagination shows count."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}, {"id": 2}], count=2,
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.fetch_all_pages("/api/v1/data/", progress=True)
        captured = capsys.readouterr()
        assert "2 total records" in captured.out
        assert "Done: 2 records" in captured.out
        client.close()

    @respx.mock
    def test_progress_output_cursor(self, capsys):
        """Progress output for cursor pagination detects 'no count'."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}],
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.fetch_all_pages("/api/v1/data/", progress=True)
        captured = capsys.readouterr()
        assert "Cursor pagination" in captured.out
        client.close()

    @respx.mock
    def test_no_progress_when_disabled(self, capsys):
        """progress=False produces no output."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}], count=1,
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        client.fetch_all_pages("/api/v1/data/", progress=False)
        captured = capsys.readouterr()
        assert captured.out == ""
        client.close()

    @respx.mock
    def test_stops_when_all_results_fetched(self):
        """Stops when len(results) >= count even if next exists."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}, {"id": 2}], count=2,
                next_url=f"{BASE_URL}/api/v1/data/?page=2",
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/")
        assert len(results) == 2
        client.close()

    @respx.mock
    def test_no_next_url_stops(self):
        """Cursor pagination without next URL stops."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([{"id": 1}]))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/")
        assert len(results) == 1
        client.close()


# ── fetch_all_pages_async ────────────────────────────────────────────────────

class TestFetchAllPagesAsync:

    @respx.mock
    @pytest.mark.asyncio
    async def test_single_page(self):
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}], count=1,
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async("/api/v1/data/")
        assert len(results) == 1
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_multi_page_cursor(self):
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": 1}],
                    next_url=f"{BASE_URL}/api/v1/data/?cursor=xyz",
                )),
                httpx.Response(200, json=_page([{"id": 2}])),
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async("/api/v1/data/", page_size=1)
        assert len(results) == 2
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_empty_results(self):
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([], count=0))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async("/api/v1/data/")
        assert results == []
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_max_pages(self, capsys):
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": i}],
                    next_url=f"{BASE_URL}/api/v1/data/?cursor=p{i+1}",
                ))
                for i in range(5)
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async(
            "/api/v1/data/", page_size=1, max_pages=2, progress=True,
        )
        assert len(results) == 2
        captured = capsys.readouterr()
        assert "max page limit" in captured.out.lower()
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_progress_output(self, capsys):
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page(
                [{"id": 1}], count=1,
            ))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        await client.fetch_all_pages_async("/api/v1/data/", progress=True)
        captured = capsys.readouterr()
        assert "Done:" in captured.out
        await client.close_async()

    @respx.mock
    @pytest.mark.asyncio
    async def test_sends_both_params(self):
        route = respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([], count=0))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        await client.fetch_all_pages_async("/api/v1/data/", page_size=250)
        req = route.calls[0].request
        assert "page_size" in str(req.url)
        assert "limit" in str(req.url)
        await client.close_async()


# ── _pagination_progress static method ───────────────────────────────────────

class TestPaginationProgress:

    def test_no_output_when_disabled(self, capsys):
        BaseEkoClient._pagination_progress(1, 10, 100, False, False)
        assert capsys.readouterr().out == ""

    def test_detected_cursor(self, capsys):
        BaseEkoClient._pagination_progress(
            1, 10, None, True, True, _detected=True,
        )
        out = capsys.readouterr().out
        assert "Cursor pagination" in out

    def test_detected_page_number(self, capsys):
        BaseEkoClient._pagination_progress(
            1, 10, 500, False, True, _detected=True,
        )
        out = capsys.readouterr().out
        assert "500 total records" in out

    def test_periodic_progress_with_count(self, capsys):
        BaseEkoClient._pagination_progress(5, 250, 1000, False, True, progress_every=5)
        out = capsys.readouterr().out
        assert "page 5" in out
        assert "250" in out
        assert "25%" in out

    def test_periodic_progress_cursor(self, capsys):
        BaseEkoClient._pagination_progress(10, 500, None, True, True, progress_every=5)
        out = capsys.readouterr().out
        assert "page 10" in out
        assert "500" in out

    def test_non_periodic_page_skipped(self, capsys):
        BaseEkoClient._pagination_progress(3, 100, 1000, False, True, progress_every=5)
        assert capsys.readouterr().out == ""


# ── Edge cases for no-next-url break path ───────────────────────────────────

class TestFetchAllPagesNoNextUrl:

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_no_next_url_stops(self):
        """Async: results but no next URL — breaks at line 412."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json=_page([{"id": 1}]))
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async("/api/v1/data/")
        assert len(results) == 1
        await client.close_async()

    @respx.mock
    def test_sync_no_next_url_with_results_but_no_count(self):
        """Sync: results present, no count, no next URL — hits line 498 break."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            return_value=httpx.Response(200, json={
                "results": [{"id": 1}, {"id": 2}],
                # no "count" key, no "next" key
            })
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = client.fetch_all_pages("/api/v1/data/")
        assert len(results) == 2
        client.close()


# ── max_pages logger.warning path ───────────────────────────────────────────

class TestMaxPagesWarningAsync:

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_max_pages_limit(self, capsys):
        """Async: stops at max_pages and prints warning — covers line 396-397."""
        respx.get(f"{BASE_URL}/api/v1/data/").mock(
            side_effect=[
                httpx.Response(200, json=_page(
                    [{"id": i}],
                    next_url=f"{BASE_URL}/api/v1/data/?cursor=page{i+1}",
                ))
                for i in range(5)
            ]
        )
        client = BaseEkoClient(base_url=BASE_URL, token="tok")
        results = await client.fetch_all_pages_async(
            "/api/v1/data/", page_size=1, max_pages=3, progress=True,
        )
        assert len(results) == 3
        captured = capsys.readouterr()
        assert "max page limit" in captured.out.lower()
        await client.close_async()
