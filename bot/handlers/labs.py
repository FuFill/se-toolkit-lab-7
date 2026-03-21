"""Handler for /labs command."""


def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available lab assignments.
    """
    # Placeholder - will be implemented in Task 2 with actual API call
    return (
        "📋 Доступные лабораторные работы:\n\n"
        "• lab-01 — Введение\n"
        "• lab-02 — Основные понятия\n"
        "• lab-03 — Продвинутые темы\n"
        "• lab-04 — Итоговая работа\n\n"
        "Используйте /scores <lab_id> для просмотра оценок."
    )
