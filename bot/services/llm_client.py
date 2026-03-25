"""LLM client for intent-based natural language routing.

This client wraps the LLM API and provides tool-calling capabilities.
The LLM receives tool definitions and decides which tools to call based on user input.
"""

import json
import sys
from typing import Any

import httpx

from .lms_api import LMSClient


# Define all 9 backend endpoints as LLM tools
def get_tool_definitions() -> list[dict[str, Any]]:
    """Return the list of tool definitions for the LLM.

    Each tool is a function schema that the LLM can call.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks available in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled learners and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab. Use this to compare pass rates between labs or find the lowest/highest pass rate.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day timeline for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab. Use this to compare groups or find the best/worst performing group.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use this to find the best students or show a leaderboard.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, e.g. 5, 10",
                        },
                    },
                    "required": ["lab", "limit"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh data. Use this when data seems outdated.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def get_system_prompt() -> str:
    """Return the system prompt for the LLM.

    This prompt instructs the LLM to use tools for answering questions.
    """
    return """You are a helpful assistant for a Learning Management System (LMS). You have access to tools that fetch data from the backend API.

Available labs in the system: lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07

When a user asks a question:
1. If they ask about available labs, tasks, or what's available - call get_items
2. If they ask about scores, pass rates, or performance - call the appropriate analytics tool
3. If they ask about students or groups - call get_learners, get_groups, or get_top_learners
4. If they ask about data freshness - you can call trigger_sync

For questions that require comparing multiple labs (like "which lab has the lowest pass rate?"):
1. First call get_items to get all labs
2. Then call get_pass_rates for EACH lab (lab-01 through lab-07) - you MUST call the tool for every lab before answering
3. After you have all the data, compare the results and provide a summary with specific numbers

For questions about a specific lab:
1. Call the appropriate tool with the lab parameter

If the user greets you or says hello, respond warmly and mention what you can help with.

If the user types gibberish or something you can't understand, politely ask them to clarify and give examples of what you can help with.

IMPORTANT: Always use tools to get real data before answering. Never make up numbers. Never answer with "let me check" - always call the tool first, then answer.

When you have all the data you need, provide a clear, helpful summary. Mention specific numbers and lab names."""


class LLMClientError(Exception):
    """Error from the LLM API."""

    pass


class LLMClient:
    """Client for the LLM API with tool-calling support.

    This client sends tool definitions to the LLM and parses tool calls.
    It supports a loop: send message -> get tool calls -> execute -> feed back -> get final answer.
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def _call_llm(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, force_tool: str | None = None
    ) -> dict[str, Any]:
        """Make a call to the LLM API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            force_tool: If set, force the LLM to call this specific tool

        Returns:
            The LLM response as a dict

        Raises:
            LLMClientError: If the API call fails
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            if force_tool:
                payload["tool_choice"] = {"type": "function", "function": {"name": force_tool}}
            else:
                payload["tool_choice"] = "auto"

        try:
            response = self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise LLMClientError(f"HTTP {e.response.status_code}: {e.response.text}") from e
        except httpx.ConnectError as e:
            raise LLMClientError(f"connection refused ({self.base_url})") from e
        except httpx.TimeoutException as e:
            raise LLMClientError(f"timeout connecting to LLM ({self.base_url})") from e
        except Exception as e:
            raise LLMClientError(f"unexpected error: {e}") from e

    def _execute_tool(self, tool_name: str, tool_args: dict[str, Any], lms_client: LMSClient) -> Any:
        """Execute a tool call using the LMS client.

        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments for the tool
            lms_client: The LMS client instance

        Returns:
            The tool result

        Raises:
            LLMClientError: If the tool execution fails
        """
        tool_map = {
            "get_items": lambda: lms_client.get_items(),
            "get_learners": lambda: lms_client.get_learners(),
            "get_scores": lambda lab: lms_client.get_scores(lab),
            "get_pass_rates": lambda lab: lms_client.get_pass_rates(lab),
            "get_timeline": lambda lab: lms_client.get_timeline(lab),
            "get_groups": lambda lab: lms_client.get_groups(lab),
            "get_top_learners": lambda lab, limit: lms_client.get_top_learners(lab, limit),
            "get_completion_rate": lambda lab: lms_client.get_completion_rate(lab),
            "trigger_sync": lambda: lms_client.trigger_sync(),
        }

        if tool_name not in tool_map:
            raise LLMClientError(f"Unknown tool: {tool_name}")

        try:
            # Call the tool function with arguments
            tool_func = tool_map[tool_name]
            if tool_args:
                return tool_func(**tool_args)
            else:
                return tool_func()
        except TypeError as e:
            raise LLMClientError(f"Invalid arguments for {tool_name}: {e}") from e
        except Exception as e:
            raise LLMClientError(f"Tool {tool_name} failed: {e}") from e

    def _parse_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]] | None:
        """Parse tool calls from the LLM response.

        Args:
            response: The LLM API response

        Returns:
            List of tool calls, or None if no tool calls
        """
        try:
            choice = response["choices"][0]
            message = choice["message"]

            if "tool_calls" in message and message["tool_calls"]:
                return message["tool_calls"]
            return None
        except (KeyError, IndexError, TypeError):
            return None

    def _get_assistant_message(self, response: dict[str, Any]) -> str | None:
        """Extract the assistant's text message from the LLM response.

        Args:
            response: The LLM API response

        Returns:
            The assistant's message text, or None if no message
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return None

    def route(self, user_message: str, lms_client: LMSClient, debug: bool = False) -> str:
        """Route a user message through the LLM tool-calling loop.

        This is the main entry point. It:
        1. Sends the user message + tool definitions to the LLM
        2. If the LLM calls tools, execute them
        3. Feed results back to the LLM
        4. Repeat until the LLM returns a final answer

        Args:
            user_message: The user's input message
            lms_client: The LMS client for executing tools
            debug: If True, print debug output to stderr

        Returns:
            The final response text
        """

        def log(msg: str) -> None:
            if debug:
                print(msg, file=sys.stderr)

        # Initialize conversation with system prompt and user message
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        tools = get_tool_definitions()
        
        # Track which labs we've checked for multi-lab comparisons
        checked_labs: set[str] = set()
        all_labs = ["lab-01", "lab-02", "lab-03", "lab-04", "lab-05", "lab-06", "lab-07"]
        
        # Detect if this is a multi-lab comparison query
        is_multi_lab_query = any(phrase in user_message.lower() for phrase in [
            "which lab has the lowest",
            "which lab has the highest",
            "lowest pass rate",
            "highest pass rate",
            "compare labs",
            "best lab",
            "worst lab",
        ])

        # Tool-calling loop
        max_iterations = 15  # Prevent infinite loops, allow enough for multi-lab comparisons
        for iteration in range(max_iterations):
            log(f"[iteration {iteration + 1}] Calling LLM...")

            # Determine if we should force a specific tool call
            force_tool = None
            remaining_labs = [lab for lab in all_labs if lab not in checked_labs]
            
            # If we're checking labs and some remain, force get_pass_rates for the next lab
            if is_multi_lab_query and remaining_labs:
                force_tool = "get_pass_rates"

            # Call LLM
            response = self._call_llm(messages, tools, force_tool=force_tool)
            log(f"[llm] Response received")

            # Get the assistant message from response
            choice = response["choices"][0]
            assistant_message = choice["message"]

            # Check for tool calls
            tool_calls = self._parse_tool_calls(response)

            if tool_calls:
                # Add the assistant's message with tool_calls to the conversation
                # This is required for the API to accept tool responses
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.get("content"),
                        "tool_calls": tool_calls,
                    }
                )

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}

                    log(f"[tool] LLM called: {tool_name}({tool_args})")
                    
                    # Track which labs we've checked
                    if tool_name == "get_pass_rates" and "lab" in tool_args:
                        checked_labs.add(tool_args["lab"])
                        log(f"[track] Checked lab: {tool_args['lab']}, remaining: {remaining_labs}")

                    # Execute the tool
                    try:
                        result = self._execute_tool(tool_name, tool_args, lms_client)
                        log(f"[tool] Result: {str(result)[:200]}...")
                    except Exception as e:
                        result = {"error": str(e)}
                        log(f"[tool] Error: {e}")

                    # Add tool result to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", "unknown"),
                            "content": json.dumps(result) if not isinstance(result, str) else result,
                        }
                    )

                log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

            else:
                # No tool calls - LLM returned a final answer
                assistant_text = self._get_assistant_message(response)
                if assistant_text:
                    # Check if this is a "let me check" response (not a real answer)
                    # Only continue if this is a multi-lab query and we haven't checked all labs
                    lower_text = assistant_text.lower()
                    remaining = [lab for lab in all_labs if lab not in checked_labs]
                    
                    if is_multi_lab_query and remaining and ("let me" in lower_text or "i'll check" in lower_text or "i will check" in lower_text):
                        log(f"[intermediate] LLM wants to continue, prompting for next tool call")
                        # Add this as a user prompt to continue
                        messages.append(
                            {"role": "assistant", "content": assistant_text}
                        )
                        # Remind the LLM which labs remain
                        messages.append(
                            {"role": "user", "content": f"Please continue. You still need to check these labs: {', '.join(remaining)}. Call get_pass_rates for the next lab."}
                        )
                        continue
                    
                    log(f"[final] LLM returned answer")
                    return assistant_text
                else:
                    log(f"[error] No tool calls and no message in response")
                    return "I encountered an error processing your request. Please try again."

        # Max iterations reached
        log(f"[error] Max iterations ({max_iterations}) reached")
        return "I'm having trouble processing your request. Please try rephrasing your question."
