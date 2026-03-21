"""Handler for /help command."""


def handle_help() -> str:
    """Handle the /help command.

    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 Справка по командам бота:\n\n"
        "/start — приветственное сообщение\n"
        "/help — показать эту справку\n"
        "/health — проверить статус backend сервиса\n"
        "/labs — показать список доступных лабораторных работ\n"
        "/scores <lab_id> — показать оценки за указанную лабораторную\n\n"
        "Также вы можете задавать вопросы естественным языком, например:\n"
        "• какие лабораторные доступны?\n"
        "• какая у меня оценка за lab-04?"
    )
