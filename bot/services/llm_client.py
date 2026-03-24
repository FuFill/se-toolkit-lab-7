"""LLM client service for intent routing.

Provides methods to interact with the LLM API for natural language understanding.
"""

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for the LLM API."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """Initialize the LLM client.

        Args:
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1)
            api_key: API key for authentication
            model: Model name to use (e.g., "coder-model")
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120.0,  # Increased timeout for complex multi-step queries
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request to the LLM.

        Args:
            messages: List of conversation messages with role and content
            tools: Optional list of tool definitions for function calling

        Returns:
            LLM response with choice message

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def extract_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]] | None:
        """Extract tool calls from LLM response.

        Args:
            response: LLM chat completion response

        Returns:
            List of tool calls with name and arguments, or None if no tool calls
        """
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            return None

        result = []
        for call in tool_calls:
            function = call.get("function", {})
            result.append({
                "id": call.get("id"),
                "name": function.get("name"),
                "arguments": json.loads(function.get("arguments", "{}")),
            })

        return result

    def extract_response_text(self, response: dict[str, Any]) -> str:
        """Extract text response from LLM.

        Args:
            response: LLM chat completion response

        Returns:
            Text content of the response
        """
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        return message.get("content", "")
