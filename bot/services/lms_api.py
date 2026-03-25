"""LMS API client for fetching data from the backend."""

from typing import Any

import httpx


class LMSClientError(Exception):
    """Error from the LMS API."""

    pass


class LMSClient:
    """Client for the LMS backend API.
    
    Uses Bearer token authentication and handles errors gracefully.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the API.
        
        Args:
            path: API path (e.g., "/items/")
            params: Optional query parameters
        
        Returns:
            JSON response data
        
        Raises:
            LMSClientError: If the request fails
        """
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise LMSClientError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}") from e
        except httpx.ConnectError as e:
            raise LMSClientError(f"connection refused ({self.base_url}). Check that the services are running.") from e
        except httpx.TimeoutException as e:
            raise LMSClientError(f"timeout connecting to backend ({self.base_url})") from e
        except Exception as e:
            raise LMSClientError(f"unexpected error: {e}") from e

    def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs and tasks) from the backend."""
        return self._get("/items/")

    def get_labs(self) -> list[dict[str, Any]]:
        """Fetch only labs (filter out tasks)."""
        items = self.get_items()
        return [item for item in items if item.get("type") == "lab"]

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of task pass rates with avg_score and attempts
        """
        return self._get("/analytics/pass-rates", params={"lab": lab})

    def get_scores(self, lab: str) -> list[dict[str, Any]]:
        """Fetch score distribution for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of score buckets with counts
        """
        return self._get("/analytics/scores", params={"lab": lab})

    def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        """Fetch submissions per day timeline for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of daily submission counts
        """
        return self._get("/analytics/timeline", params={"lab": lab})

    def get_groups(self, lab: str) -> list[dict[str, Any]]:
        """Fetch per-group scores and student counts for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of groups with scores and student counts
        """
        return self._get("/analytics/groups", params={"lab": lab})

    def get_top_learners(self, lab: str, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch top N learners by score for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")
            limit: Number of top learners to return (default: 10)

        Returns:
            List of top learners with their scores
        """
        return self._get("/analytics/top-learners", params={"lab": lab, "limit": limit})

    def get_completion_rate(self, lab: str) -> dict[str, Any]:
        """Fetch completion rate percentage for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            Dict with completion rate percentage
        """
        return self._get("/analytics/completion-rate", params={"lab": lab})

    def get_learners(self) -> list[dict[str, Any]]:
        """Fetch all enrolled learners and their groups.

        Returns:
            List of learners with their group assignments
        """
        return self._get("/learners/")

    def trigger_sync(self) -> dict[str, Any]:
        """Trigger a data sync from the autochecker.

        Returns:
            Dict with sync status
        """
        return self._post("/pipeline/sync")

    def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Make a POST request to the API.

        Args:
            path: API path (e.g., "/pipeline/sync")
            json: Optional JSON body

        Returns:
            JSON response data

        Raises:
            LMSClientError: If the request fails
        """
        try:
            response = self._client.post(path, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise LMSClientError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}") from e
        except httpx.ConnectError as e:
            raise LMSClientError(f"connection refused ({self.base_url}). Check that the services are running.") from e
        except httpx.TimeoutException as e:
            raise LMSClientError(f"timeout connecting to backend ({self.base_url})") from e
        except Exception as e:
            raise LMSClientError(f"unexpected error: {e}") from e

    def health_check(self) -> dict[str, Any]:
        """Check if the backend is healthy by fetching items.

        Returns:
            Dict with status and item count
        """
        items = self.get_items()
        return {"status": "healthy", "item_count": len(items)}
