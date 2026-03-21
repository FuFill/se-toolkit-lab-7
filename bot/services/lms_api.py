"""LMS API client service.

Provides methods to interact with the LMS backend API.
"""

import httpx
from typing import Any


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the LMS API client.

        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict[str, Any]]:
        """Get all items (labs and tasks) from the backend.

        Returns:
            List of items with their metadata.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Get pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of pass rate records per task.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def check_health(self) -> dict[str, Any]:
        """Check if the backend is healthy.

        Returns:
            Dict with 'healthy' status and 'item_count'.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}
