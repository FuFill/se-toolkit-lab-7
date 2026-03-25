"""Command handlers for the LMS bot.

Handlers are pure functions that take input and return text responses.
They have no dependency on Telegram, enabling offline testing.
"""

from .start import handle_start
from .help import handle_help
from .health import handle_health
from .labs import handle_labs
from .scores import handle_scores
from .intent_router import route as route_intent

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "route_intent",
]
