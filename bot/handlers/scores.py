"""Handler for /scores command."""

import httpx

from services.lms_api import LMSAPIClient
from config import get_settings


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

    settings = get_settings()

    if not settings.lms_api_base_url or not settings.lms_api_key:
        return (
            "⚠️ LMS API не настроен\n\n"
            "Проверьте переменные окружения:\n"
            "LMS_API_BASE_URL и LMS_API_KEY"
        )

    try:
        client = LMSAPIClient(settings.lms_api_base_url, settings.lms_api_key)
        pass_rates = client.get_pass_rates(lab_id)

        if not pass_rates:
            return f"📊 Оценки за {lab_id}:\n\nДанные не найдены для этой лабораторной."

        # Format output
        lines = [f"📊 Оценки за {lab_id}:"]
        for record in pass_rates:
            task_name = record.get("task_name", record.get("task_id", "Unknown"))
            pass_rate = record.get("pass_rate", 0)
            attempts = record.get("attempts", 0)
            lines.append(f"• {task_name}: {pass_rate:.1f}% ({attempts} попыток)")

        return "\n".join(lines)

    except httpx.ConnectError:
        return f"❌ Backend ошибка: connection refused. Проверьте, что сервис запущен."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"📊 Оценки за {lab_id}:\n\nЛабораторная работа не найдена."
        return f"❌ Backend ошибка: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.HTTPError as e:
        return f"❌ Backend ошибка: {str(e)}."
    except Exception as e:
        return f"❌ Backend ошибка: {str(e)}"
