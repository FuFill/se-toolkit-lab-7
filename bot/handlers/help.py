"""Handler for /help command."""


def handle_help() -> str:
    """Handle the /help command.

    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 Available commands:\n\n"
        "/start — welcome message\n"
        "/help — show this help\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab_id> — show scores for a lab\n\n"
        "You can also ask questions in natural language:\n"
        "• what labs are available?\n"
        "• what is my score for lab-04?"
    )
