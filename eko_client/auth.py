"""
Authentication handling for Eko Client.
"""

from typing import Optional
from .client import BaseEkoClient


class AuthMixin:
    """Mixin class for authentication methods."""
    
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
        return super().login(username, password)
    
    def logout(self) -> None:
        """
        Logout and invalidate token.
        
        Clears the token from the client instance.
        """
        super().logout()
        self.token = None
    
    def get_user_info(self) -> dict:
        """
        Get current user information.
        
        Returns:
            Dictionary with user information
            
        Raises:
            EkoAuthenticationError: If not authenticated
        """
        endpoint = '/api/auth/user/'
        return self._request_sync('GET', endpoint)
    
    async def get_user_info_async(self) -> dict:
        """
        Get current user information (async).
        
        Returns:
            Dictionary with user information
            
        Raises:
            EkoAuthenticationError: If not authenticated
        """
        endpoint = '/api/auth/user/'
        return await self._request_async('GET', endpoint)

