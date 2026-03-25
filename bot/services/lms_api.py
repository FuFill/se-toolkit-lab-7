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

    def get_learners(self) -> list[dict[str, Any]]:
        """Get all enrolled learners and their groups.

        Returns:
            List of learners with their metadata.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict[str, Any]]:
        """Get score distribution (4 buckets) for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of score distribution records.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Get per-task average scores and attempt counts for a lab.

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

    def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        """Get submissions per day for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of timeline records with submission counts per day.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict[str, Any]]:
        """Get per-group scores and student counts for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of group records with scores and student counts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Get top N learners by score.

        Args:
            lab: Optional lab identifier to filter by (e.g., "lab-04")
            limit: Number of top learners to return (default: 10)

        Returns:
            List of top learners with their scores.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        params: dict[str, Any] = {"limit": limit}
        if lab:
            params["lab"] = lab
        response = self._client.get("/analytics/top-learners", params=params)
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict[str, Any]:
        """Get completion rate percentage for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            Dict with completion rate percentage.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict[str, Any]:
        """Trigger data sync from autochecker.

        Returns:
            Dict with sync status.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.post("/pipeline/sync")
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
