"""Handler for /scores command."""


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: Optional lab assignment identifier.

    Returns:
        Scores information for the specified lab or general scores summary.
    """
    if lab_id is None:
        return (
            "📊 Оценки\n\n"
            "Укажите идентификатор лабораторной работы:\n"
            "/scores lab-04"
        )

    # Placeholder - will be implemented in Task 2 with actual API call
    return (
        f"📊 Оценки за {lab_id}:\n\n"
        "Статус: Проверка...\n"
        "Балл: Будет отображен после проверки"
    )
