"""Intent router for natural language queries.

Routes user messages to LLM with tool definitions, executes tool calls,
and returns formatted responses.
"""

import sys
from typing import Any

from services.lms_api import LMSAPIClient
from services.llm_client import LLMClient


# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a Learning Management System (LMS) Telegram bot.
Your job is to help users get information about their labs, scores, and progress.

You have access to the following tools (API endpoints). Use them to answer user questions.

IMPORTANT:
- Always use tools to get real data before answering questions about labs, scores, students, etc.
- If the user asks about multiple labs or comparisons, call tools for each one.
- After getting tool results, analyze the data and provide a clear, helpful answer.
- If you don't have enough information (e.g., user says "lab 4" without specifying what they want), ask for clarification.
- For greetings or unrelated messages, respond politely and mention what you can help with.

IMPORTANT - EMPTY DATA HANDLING:
- If a tool returns empty data (0 items, empty list, all zeros), DO NOT keep calling the same tool repeatedly.
- Instead, inform the user that no data is available yet and suggest possible reasons (e.g., "no submissions yet", "lab hasn't started").
- Offer to help with something else or suggest checking back later.

AVAILABLE TOOLS:
- get_items(): List all labs and tasks. Use this when user asks "what labs are available" or needs to know lab identifiers.
- get_learners(): List all enrolled students and their groups. Use for questions about enrollment or student lists.
- get_scores(lab): Get score distribution (4 buckets) for a specific lab. Use for questions about score distribution.
- get_pass_rates(lab): Get per-task average scores and attempt counts. Use for questions about pass rates or difficulty.
- get_timeline(lab): Get submissions per day. Use for questions about submission patterns or deadlines.
- get_groups(lab): Get per-group scores and student counts. Use for comparing groups or finding the best group.
- get_top_learners(lab, limit): Get top N learners by score. Use for leaderboards or finding best students. REQUIRES lab parameter.
- get_completion_rate(lab): Get completion rate percentage. Use for questions about how many students finished.
- trigger_sync(): Refresh data from autochecker. Use when user wants to update data.

WHEN ANSWERING:
- Be specific: include numbers from the data (e.g., "Lab 03 has 62.3% pass rate").
- Compare when asked (e.g., "which lab is best" — rank them).
- Format answers clearly with bullet points or numbered lists when appropriate.
- If data is empty, say so clearly and suggest next steps.
"""


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return tool definitions for LLM function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "List of all labs and tasks with their metadata",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "List of all enrolled learners and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
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
                "description": "Get per-task average scores and attempt counts for a lab",
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
                "description": "Get submissions per day for a lab",
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
                "description": "Get per-group scores and student counts for a lab",
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
                "description": "Get top N learners by score for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04' (required)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 10)",
                        },
                    },
                    "required": ["lab"],
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
                "description": "Refresh data from autochecker",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]


def execute_tool(name: str, arguments: dict[str, Any], api_client: LMSAPIClient) -> Any:
    """Execute a tool by calling the appropriate API method.

    Args:
        name: Tool/function name
        arguments: Arguments to pass to the tool
        api_client: LMS API client instance

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool name is unknown
    """
    match name:
        case "get_items":
            return api_client.get_items()
        case "get_learners":
            return api_client.get_learners()
        case "get_scores":
            return api_client.get_scores(arguments.get("lab", ""))
        case "get_pass_rates":
            return api_client.get_pass_rates(arguments.get("lab", ""))
        case "get_timeline":
            return api_client.get_timeline(arguments.get("lab", ""))
        case "get_groups":
            return api_client.get_groups(arguments.get("lab", ""))
        case "get_top_learners":
            lab = arguments.get("lab", "")
            limit = arguments.get("limit", 10)
            return api_client.get_top_learners(lab, limit)
        case "get_completion_rate":
            return api_client.get_completion_rate(arguments.get("lab", ""))
        case "trigger_sync":
            return api_client.trigger_sync()
        case _:
            raise ValueError(f"Unknown tool: {name}")


def route(
    user_message: str,
    api_client: LMSAPIClient,
    llm_client: LLMClient,
    debug: bool = False,
) -> str:
    """Route a user message through the LLM tool-calling loop.

    Args:
        user_message: The user's natural language query
        api_client: LMS API client instance
        llm_client: LLM client instance
        debug: If True, print debug info to stderr

    Returns:
        Formatted response text
    """

    def debug_log(message: str) -> None:
        if debug:
            print(message, file=sys.stderr)

    # Initialize conversation with system prompt and user message
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    tool_definitions = get_tool_definitions()
    max_iterations = 5  # Prevent infinite loops

    for iteration in range(max_iterations):
        debug_log(f"[iteration {iteration + 1}] Calling LLM...")

        # Call LLM with conversation history and tool definitions
        response = llm_client.chat(messages, tools=tool_definitions)

        # Extract tool calls from LLM response
        tool_calls = llm_client.extract_tool_calls(response)

        if not tool_calls:
            # No tool calls — LLM wants to respond directly
            debug_log(f"[iteration {iteration + 1}] No tool calls, getting final response")
            return llm_client.extract_response_text(response)

        # Execute each tool call and collect results
        tool_results = []
        all_empty = True
        for call in tool_calls:
            debug_log(f"[tool] LLM called: {call['name']}({call['arguments']})")

            try:
                result = execute_tool(call["name"], call["arguments"], api_client)
                result_size = len(result) if isinstance(result, (list, dict)) else 1
                debug_log(f"[tool] Result: {result_size} items")
                
                # Check if result is empty
                if isinstance(result, list) and len(result) > 0:
                    all_empty = False
                elif isinstance(result, dict) and result:
                    all_empty = False
                    
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": str(result),
                })
            except Exception as e:
                debug_log(f"[tool] Error executing {call['name']}: {e}")
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": f"Error: {e}",
                })
                all_empty = False  # Error is not empty data

        # If all results are empty, break the loop and inform user
        if all_empty and tool_results:
            debug_log("[early exit] All tool results are empty, breaking loop")
            return "Похоже, что по вашему запросу нет данных. Это может означать, что:\n\n• Данные ещё не были синхронизированы\n• Лабораторные работы ещё не начались\n• Студенты ещё не сдали работы\n\nПопробуйте:\n• Обновить данные: /sync (если доступно)\n• Проверить доступные лаборатории: /labs\n• Задать другой вопрос"

        # Feed tool results back to LLM
        debug_log(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")
        messages.extend(tool_results)

    # If we exhausted iterations, return a fallback message
    return "I'm having trouble processing your request. Please try rephrasing or use a slash command like /help."
