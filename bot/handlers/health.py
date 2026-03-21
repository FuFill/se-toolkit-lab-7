"""Handler for /health command."""

import httpx

from services.lms_api import LMSAPIClient
from config import get_settings


def handle_health() -> str:
    """Handle the /health command.

    Returns:
        Backend service status message.
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
        result = client.check_health()
        return (
            f"✅ Backend сервис доступен\n\n"
            f"Количество элементов: {result['item_count']}"
        )
    except httpx.ConnectError as e:
        return f"❌ Backend ошибка: connection refused. Проверьте, что сервис запущен."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend ошибка: HTTP {e.response.status_code} {e.response.reason_phrase}. Backend сервис может быть недоступен."
    except httpx.HTTPError as e:
        return f"❌ Backend ошибка: {str(e)}. Проверьте подключение к серверу."
    except Exception as e:
        return f"❌ Backend ошибка: {str(e)}"
