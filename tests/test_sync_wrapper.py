"""Tests for eko_client.sync_wrapper — auto_sync_wrapper decorator."""

import asyncio
import pytest
from eko_client.sync_wrapper import auto_sync_wrapper, _create_sync_wrapper


class TestAutoSyncWrapper:

    def test_generates_sync_methods(self):
        """Decorator creates sync methods for async methods."""
        @auto_sync_wrapper
        class MyClient:
            async def fetch_data_async(self, param: str) -> dict:
                """Fetch data."""
                return {"param": param}

        client = MyClient()
        assert hasattr(client, "fetch_data")
        assert callable(client.fetch_data)

    def test_sync_method_calls_async(self):
        """Generated sync method actually calls the async method."""
        @auto_sync_wrapper
        class MyClient:
            async def greet_async(self, name: str) -> str:
                return f"Hello, {name}"

        client = MyClient()
        result = client.greet(name="World")
        assert result == "Hello, World"

    def test_preserves_docstring(self):
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self) -> dict:
                """Fetch all the things."""
                return {}

        assert MyClient.fetch.__doc__ == "Fetch all the things."

    def test_no_docstring_generates_one(self):
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self):
                return {}

        assert "fetch_async" in MyClient.fetch.__doc__

    def test_skips_non_async_suffix(self):
        """Methods not ending in _async are not wrapped."""
        @auto_sync_wrapper
        class MyClient:
            def regular_method(self):
                return "regular"

            async def helper_internal(self):
                return "no suffix"

        client = MyClient()
        assert hasattr(client, "regular_method")
        assert not hasattr(client, "helper_internal_sync")

    def test_skips_existing_sync_method(self):
        """If sync method already exists, don't overwrite it."""
        @auto_sync_wrapper
        class MyClient:
            def get_data(self):
                return "manual sync"

            async def get_data_async(self):
                return "async version"

        client = MyClient()
        assert client.get_data() == "manual sync"

    def test_adds_close_sync_loop(self):
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self):
                return {}

        client = MyClient()
        assert hasattr(client, "close_sync_loop")

    def test_close_sync_loop_safe_without_loop(self):
        """close_sync_loop doesn't error if no loop was created."""
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self):
                return {}

        client = MyClient()
        client.close_sync_loop()  # should not raise

    def test_close_sync_loop_closes_loop(self):
        """close_sync_loop closes the event loop if it was created."""
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self):
                return {}

        client = MyClient()
        # Force creation of _sync_loop by calling sync method
        client.fetch()
        if hasattr(client, "_sync_loop") and client._sync_loop:
            assert not client._sync_loop.is_closed()
            client.close_sync_loop()
            assert client._sync_loop is None

    def test_multiple_sequential_calls(self):
        """Sync wrapper supports multiple sequential calls."""
        @auto_sync_wrapper
        class MyClient:
            def __init__(self):
                self.call_count = 0

            async def increment_async(self) -> int:
                self.call_count += 1
                return self.call_count

        client = MyClient()
        assert client.increment() == 1
        assert client.increment() == 2
        assert client.increment() == 3

    def test_preserves_annotations(self):
        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self, limit: int = 10) -> dict:
                return {"limit": limit}

        # Check that annotations are preserved
        annotations = MyClient.fetch.__annotations__
        assert "limit" in annotations or "return" in annotations


class TestCreateSyncWrapper:

    def test_wraps_simple_coroutine(self):
        async def my_async(self):
            return 42

        sync = _create_sync_wrapper(my_async)

        class FakeClient:
            pass

        client = FakeClient()
        result = sync(client)
        assert result == 42

    def test_nest_asyncio_path(self):
        """When a running event loop exists, nest_asyncio is applied."""
        import nest_asyncio

        @auto_sync_wrapper
        class MyClient:
            async def fetch_async(self):
                return "from-jupyter"

        async def run_inside_loop():
            client = MyClient()
            # Calling sync method inside a running event loop triggers
            # the nest_asyncio code path (lines 62-66)
            result = client.fetch()
            return result

        # Apply nest_asyncio so run_until_complete can be re-entered
        loop = asyncio.new_event_loop()
        nest_asyncio.apply(loop)
        try:
            result = loop.run_until_complete(run_inside_loop())
            assert result == "from-jupyter"
        finally:
            loop.close()

    def test_non_coroutine_with_async_suffix_skipped(self):
        """A regular (non-async) method ending in _async is not wrapped.
        Covers sync_wrapper.py line 160 (the `continue` when
        `not inspect.iscoroutinefunction(attr)`)."""
        @auto_sync_wrapper
        class MyClient:
            def not_really_async(self):
                return "sync"

            # This is a regular function, not a coroutine, but ends in _async
            pass

        # Manually add a non-coroutine with _async suffix to verify
        def fake_async(self):
            return "fake"
        fake_async.__name__ = "get_thing_async"

        # Attach it before decorating a new class
        @auto_sync_wrapper
        class MyClient2:
            pass

        MyClient2.get_thing_async = fake_async
        # Re-apply decorator to pick up the new attr
        MyClient2 = auto_sync_wrapper(MyClient2)
        # get_thing should NOT be created since get_thing_async is not a coroutine
        assert not hasattr(MyClient2, "get_thing")
