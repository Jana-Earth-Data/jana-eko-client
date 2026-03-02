"""
Utility functions for the Eko Client library.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime


def format_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format query parameters for API requests.
    
    Converts lists to comma-separated strings and handles special types.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Formatted dictionary ready for API request
    """
    formatted = {}
    
    for key, value in params.items():
        if value is None:
            continue
            
        # Handle list parameters - convert to comma-separated string
        if isinstance(value, (list, tuple)):
            # For location_bbox and location_point, keep as list
            if key in ['location_bbox', 'location_point']:
                formatted[key] = value
            else:
                # Convert other lists to comma-separated strings
                formatted[key] = ','.join(str(v) for v in value)
        # Handle datetime objects
        elif isinstance(value, datetime):
            formatted[key] = value.isoformat()
        # Handle boolean values
        elif isinstance(value, bool):
            formatted[key] = 'true' if value else 'false'
        else:
            formatted[key] = value
    
    return formatted


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 date string to datetime object.
    
    Args:
        date_str: ISO 8601 formatted date string
        
    Returns:
        datetime object or None
    """
    if not date_str:
        return None
    
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def build_url(base_url: str, *path_parts: str) -> str:
    """
    Build URL from base URL and path parts.
    
    Args:
        base_url: Base URL (e.g., 'http://localhost:8000')
        *path_parts: Path segments to join
        
    Returns:
        Complete URL string
    """
    # Remove trailing slash from base_url
    base_url = base_url.rstrip('/')
    
    # Join path parts, removing leading slashes
    path = '/'.join(str(part).lstrip('/') for part in path_parts if part)
    
    return f"{base_url}/{path}"

