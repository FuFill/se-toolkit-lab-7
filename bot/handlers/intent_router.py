"""Intent router for natural language queries.

This handler uses the LLM to interpret user messages and route them to
the appropriate data sources. It supports:
- Single-step queries (e.g., "show me scores for lab 4")
- Multi-step queries (e.g., "which lab has the lowest pass rate?")
- Fallback handling for greetings and gibberish
"""

import sys
from typing import Any

from services.lms_api import LMSClient, LMSClientError
from services.llm_client import LLMClient, LLMClientError


def route_intent(user_message: str, lms_client: LMSClient, llm_client: LLMClient) -> str:
    """Route a natural language query through the LLM.

    Args:
        user_message: The user's input message
        lms_client: The LMS API client
        llm_client: The LLM client

    Returns:
        The response text
    """
    try:
        return llm_client.route(user_message, lms_client, debug=True)
    except LLMClientError as e:
        return f"LLM error: {e}. Please try again or use a slash command."
    except LMSClientError as e:
        return f"Backend error: {e}. Is the backend running?"
    except Exception as e:
        return f"Unexpected error: {e}. Please try again."


def get_welcome_message() -> str:
    """Return a welcome message with inline button suggestions.

    This message introduces the bot's capabilities.
    """
    return """👋 Hello! I'm your LMS assistant.

I can help you with:
• View available labs and tasks
• Check scores and pass rates for any lab
• Find top learners and group rankings
• Track completion rates and timelines

Just ask me a question like:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students in lab 3?"

Or use commands like /help, /labs, /health"""


def get_help_message() -> str:
    """Return a help message with examples.

    This message shows users what they can ask.
    """
    return """📚 LMS Bot Help

**Commands:**
/start — Welcome message
/help — This help message
/health — Check backend status
/labs — List available labs
/scores <lab_id> — Show scores for a lab

**Natural Language Examples:**

*General queries:*
• "What labs are available?"
• "How many students are enrolled?"

*Lab-specific queries:*
• "Show me scores for lab 4"
• "What's the pass rate for lab 02?"
• "Show the timeline for lab 3"

*Comparisons:*
• "Which lab has the lowest pass rate?"
• "Which group is doing best in lab 3?"
• "Who are the top 5 students in lab 4?"

*Data management:*
• "Refresh the data from autochecker"

Just type your question and I'll figure out what data you need!"""


def get_inline_keyboard_suggestions() -> list[str]:
    """Return a list of suggested queries for inline buttons.

    These buttons help users discover common queries.
    """
    return [
        "What labs are available?",
        "Show scores for lab 4",
        "Which lab has lowest pass rate?",
        "Top 5 students in lab 4",
    ]
