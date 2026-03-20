"""
Base client class with HTTP request handling for async and sync operations.
"""

import asyncio
import threading
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import httpx
from .exceptions import (
    EkoClientError,
    EkoAuthenticationError,
    EkoAPIError,
    EkoRateLimitError,
    EkoNotFoundError,
)
from .utils import build_url, format_query_params

logger = logging.getLogger(__name__)


class BaseEkoClient:
    """Base client with common functionality for async and sync operations."""
    
    # Auth endpoint prefixes — requests matching these use base_url (auth service).
    # Everything else uses api_base_url (data service) when provided.
    _AUTH_PREFIXES = ("/api/auth/",)

    def __init__(
        self,
        base_url: str,
        api_base_url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize base client.

        Args:
            base_url: API base URL for auth endpoints (e.g., 'https://auth-dev.jana.earth').
                When api_base_url is not set, this is used for all requests.
            api_base_url: Optional separate base URL for data/ESG endpoints
                (e.g., 'https://api-dev.jana.earth'). When set, auth endpoints
                (``/api/auth/...``) continue to use base_url while all other
                requests are sent to api_base_url.
            token: Authentication token (if available)
            username: Username for login (if token not provided)
            password: Password for login (if token not provided)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.api_base_url = api_base_url.rstrip('/') if api_base_url else None
        self.token = token
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Create async client
        self._async_client: Optional[httpx.AsyncClient] = None
        self._async_lock = asyncio.Lock()
        
        # Create sync client
        self._sync_client: Optional[httpx.Client] = None
        self._sync_lock = threading.Lock()
        
        # Auto-login if credentials provided
        if not self.token and self.username and self.password:
            self.token = self.login(self.username, self.password)
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        return self._async_client
    
    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        return self._sync_client
    
    def _resolve_base_url(self, endpoint: str) -> str:
        """Return the correct base URL for the given endpoint.

        Auth endpoints (``/api/auth/...``) always use ``self.base_url``.
        All other endpoints use ``self.api_base_url`` when it is set,
        falling back to ``self.base_url`` otherwise.
        """
        if self.api_base_url and not any(
            endpoint.startswith(prefix) for prefix in self._AUTH_PREFIXES
        ):
            return self.api_base_url
        return self.base_url

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers including authentication."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        
        return headers
    
    async def _request_async(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make async HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., '/api/v1/esg/data/')
            params: Query parameters
            json_data: JSON body data
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response JSON data as dictionary
            
        Raises:
            EkoAuthenticationError: If authentication fails
            EkoAPIError: If API returns an error
            EkoRateLimitError: If rate limit is exceeded
            EkoNotFoundError: If resource not found
        """
        url = build_url(self._resolve_base_url(endpoint), endpoint)
        headers = self._get_headers()

        # Format query parameters
        if params:
            params = format_query_params(params)

        async with self._async_lock:
            client = self._get_async_client()
            
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    **kwargs
                )
                
                return self._handle_response(response)
                
            except httpx.HTTPError as e:
                raise EkoClientError(f"HTTP request failed: {str(e)}")
    
    def _request_sync(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make synchronous HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., '/api/v1/esg/data/')
            params: Query parameters
            json_data: JSON body data
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response JSON data as dictionary
            
        Raises:
            EkoAuthenticationError: If authentication fails
            EkoAPIError: If API returns an error
            EkoRateLimitError: If rate limit is exceeded
            EkoNotFoundError: If resource not found
        """
        url = build_url(self._resolve_base_url(endpoint), endpoint)
        headers = self._get_headers()

        # Format query parameters
        if params:
            params = format_query_params(params)

        with self._sync_lock:
            client = self._get_sync_client()
            
            try:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    **kwargs
                )
                
                return self._handle_response(response)
                
            except httpx.HTTPError as e:
                raise EkoClientError(f"HTTP request failed: {str(e)}")
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.
        
        Args:
            response: httpx Response object
            
        Returns:
            Response JSON data as dictionary
            
        Raises:
            EkoAuthenticationError: If authentication fails (401)
            EkoNotFoundError: If resource not found (404)
            EkoRateLimitError: If rate limit exceeded (429)
            EkoAPIError: For other API errors
        """
        # Handle authentication errors
        if response.status_code == 401:
            error_data = self._parse_error_response(response)
            raise EkoAuthenticationError(
                error_data.get('error', 'Authentication failed'),
                status_code=401,
                response_data=error_data
            )
        
        # Handle not found errors
        if response.status_code == 404:
            error_data = self._parse_error_response(response)
            raise EkoNotFoundError(
                error_data.get('error', 'Resource not found'),
                response_data=error_data
            )
        
        # Handle rate limit errors
        if response.status_code == 429:
            error_data = self._parse_error_response(response)
            retry_after = None
            if 'retry_after' in error_data:
                retry_after = int(error_data['retry_after'])
            raise EkoRateLimitError(
                error_data.get('error', 'Rate limit exceeded'),
                retry_after=retry_after,
                response_data=error_data
            )
        
        # Handle other errors
        if not response.is_success:
            error_data = self._parse_error_response(response)
            raise EkoAPIError(
                error_data.get('error', f'API error: {response.status_code}'),
                status_code=response.status_code,
                response_data=error_data
            )
        
        # Parse successful response
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as e:
            # If response is not JSON, return text
            logger.warning(f"Response is not valid JSON: {e}. Returning raw text.")
            return {'content': response.text}
    
    def _parse_error_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse error response JSON."""
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Error response is not valid JSON: {e}. Status: {response.status_code}")
            return {'error': response.text or f'HTTP {response.status_code}'}
    
    # =========================================================================
    # Pagination helpers
    # =========================================================================

    async def fetch_all_pages_async(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        page_size: int = 1000,
        max_pages: int = 1000,
        progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all pages of a paginated endpoint, following cursor ``next`` URLs.

        Works with both CursorPagination (follows ``next`` URL) and
        LimitOffsetPagination (increments ``offset``). Automatically detects
        which style the API uses based on the response.

        Args:
            endpoint: API endpoint path (e.g., '/api/v1/data-sources/climatetrace/emissions/')
            params: Initial query parameters (filters, etc.)
            page_size: Number of records per page (default 1000, the API max for most endpoints)
            max_pages: Safety limit on number of pages to fetch (default 1000)
            progress: If True, print progress messages

        Returns:
            List of all result dictionaries across all pages
        """
        all_results: List[Dict[str, Any]] = []
        params = dict(params or {})
        params['limit'] = page_size
        page = 0

        # First request uses the endpoint + params
        response = await self._request_async('GET', endpoint, params=params)

        while True:
            page += 1
            results = response.get('results', [])
            if not results:
                break
            all_results.extend(results)

            total = response.get('count')
            if progress:
                if total:
                    logger.info("Page %d: %d/%d records", page, len(all_results), total)
                else:
                    logger.info("Page %d: %d records so far", page, len(all_results))

            # Stop conditions
            if total and len(all_results) >= total:
                break
            if page >= max_pages:
                logger.warning("Reached max_pages=%d, stopping", max_pages)
                break

            # Follow cursor next URL if present (CursorPagination)
            next_url = response.get('next')
            if next_url:
                # Extract the path + query from the full URL and make a raw request
                parsed = urlparse(next_url)
                next_endpoint = parsed.path
                # Parse query string into flat dict
                next_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
                response = await self._request_async('GET', next_endpoint, params=next_params)
            else:
                # No next URL and count not reached -- we're done
                break

        return all_results

    def fetch_all_pages(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        page_size: int = 1000,
        max_pages: int = 1000,
        progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of :meth:`fetch_all_pages_async`.

        Fetch all pages of a paginated endpoint, following cursor ``next`` URLs.

        Args:
            endpoint: API endpoint path
            params: Initial query parameters (filters, etc.)
            page_size: Records per page (default 1000)
            max_pages: Safety limit on pages (default 1000)
            progress: Print progress messages

        Returns:
            List of all result dictionaries across all pages
        """
        all_results: List[Dict[str, Any]] = []
        params = dict(params or {})
        params['limit'] = page_size
        page = 0

        response = self._request_sync('GET', endpoint, params=params)

        while True:
            page += 1
            results = response.get('results', [])
            if not results:
                break
            all_results.extend(results)

            total = response.get('count')
            if progress:
                if total:
                    logger.info("Page %d: %d/%d records", page, len(all_results), total)
                else:
                    logger.info("Page %d: %d records so far", page, len(all_results))

            if total and len(all_results) >= total:
                break
            if page >= max_pages:
                logger.warning("Reached max_pages=%d, stopping", max_pages)
                break

            next_url = response.get('next')
            if next_url:
                parsed = urlparse(next_url)
                next_endpoint = parsed.path
                next_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
                response = self._request_sync('GET', next_endpoint, params=next_params)
            else:
                break

        return all_results

    def login(self, username: str, password: str) -> str:
        """
        Login and get authentication token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Authentication token string
            
        Raises:
            EkoAuthenticationError: If login fails
        """
        endpoint = '/api/auth/login/'
        json_data = {
            'username': username,
            'password': password,
        }
        
        try:
            response = self._request_sync('POST', endpoint, json_data=json_data)
            self.token = response.get('token')
            
            if not self.token:
                raise EkoAuthenticationError('No token received from login')
            
            return self.token
            
        except EkoAPIError as e:
            raise EkoAuthenticationError(
                f'Login failed: {e.message}',
                status_code=e.status_code,
                response_data=e.response_data
            )
    
    def logout(self) -> None:
        """
        Logout and invalidate token.
        
        Note: This calls the logout endpoint but does not clear the token
        from the client instance. You may want to set self.token = None
        after calling this.
        """
        if not self.token:
            return
        
        endpoint = '/api/auth/logout/'

        try:
            self._request_sync('POST', endpoint)
        except (httpx.HTTPError, EkoClientError) as e:
            # Log but don't raise errors on logout - session cleanup should not fail
            logger.warning(f"Error during logout (ignored): {e}")
        finally:
            self.token = None
    
    async def close_async(self) -> None:
        """Close async HTTP client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    def close_sync(self) -> None:
        """Close sync HTTP client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
    
    def close(self) -> None:
        """Close all HTTP clients."""
        self.close_sync()
        # Note: Cannot await in sync method, so async close must be called separately
        # Users should call close_async() in async context if needed
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

