"""
Automatic sync wrapper generation for async methods.

This module provides a class decorator that automatically generates synchronous
wrapper methods for all async methods in a class. This eliminates the need for
~1,500 lines of boilerplate sync wrapper code.

Usage:
    @auto_sync_wrapper
    class MyClient:
        async def fetch_data_async(self, param: str) -> dict:
            '''Async implementation.'''
            return await self._request(...)

    # Automatically creates:
    # def fetch_data(self, param: str) -> dict:
    #     '''Sync wrapper for fetch_data_async.'''
    #     return self._run_sync(self.fetch_data_async(param))

The decorator:
- Finds all methods ending with '_async'
- Creates a sync version without the '_async' suffix
- Preserves the async method's signature, docstring, and annotations
- Uses a persistent event loop per instance for proper connection pooling
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, TypeVar


T = TypeVar('T')


def _create_sync_wrapper(async_method: Callable) -> Callable:
    """
    Create a synchronous wrapper for an async method.

    Uses a persistent event loop per instance to support multiple
    sequential calls and proper connection pooling.

    Args:
        async_method: The async method to wrap

    Returns:
        A synchronous wrapper function that uses the instance's event loop
    """
    @wraps(async_method)
    def sync_wrapper(self, *args, **kwargs):
        # Get or create persistent event loop for this instance
        if not hasattr(self, '_sync_loop'):
            self._sync_loop = asyncio.new_event_loop()
            self._sync_loop_refs = 0

        # Run the async method on the persistent loop
        return self._sync_loop.run_until_complete(
            async_method(self, *args, **kwargs)
        )

    # Preserve the original docstring or create a simple one
    if async_method.__doc__:
        sync_wrapper.__doc__ = async_method.__doc__
    else:
        sync_wrapper.__doc__ = f"Sync wrapper for {async_method.__name__}."

    # Preserve annotations
    if hasattr(async_method, '__annotations__'):
        sync_wrapper.__annotations__ = async_method.__annotations__.copy()

    return sync_wrapper


def auto_sync_wrapper(cls: type[T]) -> type[T]:
    """
    Class decorator that automatically generates sync wrappers for async methods.

    This decorator:
    1. Iterates through all class methods
    2. Finds methods ending with '_async'
    3. Creates a synchronous wrapper method without the '_async' suffix
    4. Adds the sync wrapper to the class
    5. Adds a close_sync_loop() method for cleanup

    The sync wrapper:
    - Has the same signature as the async method
    - Has the same docstring as the async method
    - Uses a persistent event loop per instance
    - Supports multiple sequential calls

    Args:
        cls: The class to decorate

    Returns:
        The same class with auto-generated sync wrapper methods

    Example:
        @auto_sync_wrapper
        class MyClient:
            async def get_user_async(self, user_id: str) -> dict:
                '''Fetch user by ID.'''
                return await self._fetch(f'/users/{user_id}')

        # Automatically creates:
        # def get_user(self, user_id: str) -> dict:
        #     '''Fetch user by ID.'''
        #     return self._sync_loop.run_until_complete(
        #         self.get_user_async(user_id)
        #     )

        # Multiple calls work:
        client = MyClient()
        user1 = client.get_user('123')  # Works
        user2 = client.get_user('456')  # Works too!
    """
    # Add cleanup method for the persistent event loop
    def close_sync_loop(self):
        """Close the persistent event loop used for sync methods."""
        if hasattr(self, '_sync_loop') and self._sync_loop:
            if not self._sync_loop.is_closed():
                self._sync_loop.close()
            self._sync_loop = None

    # Add the cleanup method if it doesn't exist
    if not hasattr(cls, 'close_sync_loop'):
        setattr(cls, 'close_sync_loop', close_sync_loop)

    # Iterate through all attributes of the class
    for attr_name in dir(cls):
        # Skip private/magic methods and non-async methods
        if not attr_name.endswith('_async'):
            continue

        # Get the method
        attr = getattr(cls, attr_name)

        # Only process async methods
        if not inspect.iscoroutinefunction(attr):
            continue

        # Generate sync method name by removing '_async' suffix
        sync_name = attr_name[:-6]  # Remove '_async'

        # Skip if sync method already exists
        # (allows manual overrides if needed)
        if hasattr(cls, sync_name):
            continue

        # Create and add the sync wrapper
        sync_wrapper = _create_sync_wrapper(attr)
        setattr(cls, sync_name, sync_wrapper)

    return cls
