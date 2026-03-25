"""Handler for /labs command."""

import httpx

from services.lms_api import LMSAPIClient
from config import get_settings


def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available lab assignments.
    """
    settings = get_settings()

    if not settings.lms_api_base_url or not settings.lms_api_key:
        return (
            "⚠️ LMS API не настроен\n\n"
            "Проверьте переменные окружения:\n"
            "LMS_API_BASE_URL и LMS_API_KEY"
        )

    try:
        client = LMSAPIClient(settings.lms_api_base_url, settings.lms_api_key)
        items = client.get_items()

        # Filter only labs (type=lab)
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return "📋 Лабораторные работы не найдены\n\nПохоже, в системе нет данных."

        # Format output
        lines = ["📋 Доступные лабораторные работы:\n"]
        for lab in labs:
            lab_id = f"lab-{lab['id']:02d}"
            title = lab.get("title", f"Lab {lab['id']}")
            lines.append(f"• {lab_id} — {title}")

        lines.append("\nИспользуйте /scores <lab_id> для просмотра оценок.")
        return "\n".join(lines)

    except httpx.ConnectError:
        return "❌ Backend ошибка: connection refused. Проверьте, что сервис запущен."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend ошибка: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.HTTPError as e:
        return f"❌ Backend ошибка: {str(e)}."
    except Exception as e:
        return f"❌ Backend ошибка: {str(e)}"
