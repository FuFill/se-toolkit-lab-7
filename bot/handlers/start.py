"""Handler for /start command."""


def handle_start() -> str:
    """Handle the /start command.

    Returns:
        Welcome message for new users.
    """
    return (
        "👋 Welcome to LMS Bot!\n\n"
        "I can help you get information about your assignments and scores.\n\n"
        "Available commands:\n"
        "/help — show available commands\n"
        "/health — check backend status\n"
        "/labs — show available labs\n"
        "/scores <lab_id> — show scores for a lab"
    )
