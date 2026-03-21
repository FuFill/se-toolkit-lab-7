"""Handler for /start command."""


def handle_start() -> str:
    """Handle the /start command.

    Returns:
        Welcome message for new users.
    """
    return (
        "👋 Добро пожаловать в LMS Bot!\n\n"
        "Я помогу вам получить информацию о ваших учебных заданиях и оценках.\n\n"
        "Доступные команды:\n"
        "/help — показать список команд\n"
        "/health — проверить статус backend\n"
        "/labs — показать доступные лабораторные работы\n"
        "/scores <lab_id> — показать оценки за лабораторную"
    )
