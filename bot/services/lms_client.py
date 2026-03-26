"""LMS API client for fetching backend data."""

import httpx
from typing import Optional


class LmsClient:
    """Client for the LMS Backend API.
    
    Handles HTTP requests to the LMS API with proper authentication
    and error handling.
    """
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}
    
    def _make_request(self, endpoint: str) -> dict | list | None:
        """Make an authenticated GET request to the API.
        
        Args:
            endpoint: API endpoint (e.g., "/items/", "/analytics/pass-rates")
        
        Returns:
            JSON response as dict/list, or None on error
        
        Raises:
            httpx.RequestError: On connection/network errors
            httpx.HTTPStatusError: On HTTP error responses
        """
        url = f"{self.base_url}{endpoint}"
        with httpx.Client() as client:
            response = client.get(url, headers=self._headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    def get_items(self) -> list[dict]:
        """Fetch all items (labs and tasks) from the API.
        
        Returns:
            List of item dictionaries
        """
        result = self._make_request("/items/")
        return result if isinstance(result, list) else []
    
    def get_labs(self) -> list[dict]:
        """Fetch only lab items (not tasks).
        
        Returns:
            List of lab dictionaries
        """
        items = self.get_items()
        return [item for item in items if item.get("type") == "lab"]
    
    def get_pass_rates(self, lab: str) -> list[dict]:
        """Fetch pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04")
        
        Returns:
            List of pass rate dictionaries with task info
        """
        result = self._make_request(f"/analytics/pass-rates?lab={lab}")
        return result if isinstance(result, list) else []
    
    def is_healthy(self) -> tuple[bool, str]:
        """Check if the backend is healthy.
        
        Returns:
            Tuple of (is_healthy, message)
        """
        try:
            items = self.get_items()
            count = len(items)
            return True, f"Backend is healthy. {count} items available."
        except httpx.ConnectError as e:
            return False, f"Backend error: connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return False, f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except Exception as e:
            return False, f"Backend error: {str(e)}"
