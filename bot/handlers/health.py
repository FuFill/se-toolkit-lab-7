"""Handler for /health command."""

from services.lms_api import LMSClient, LMSClientError


def _get_client() -> LMSClient:
    """Create an LMS client from config settings."""
    from config import get_settings

    settings = get_settings()
    return LMSClient(
        base_url=settings.lms_api_base_url or "http://localhost:42002",
        api_key=settings.lms_api_key or "",
    )


def handle_health() -> str:
    """Handle the /health command.

    Returns:
        Backend service status message.
    """
    try:
        client = _get_client()
        result = client.health_check()
        return f"✅ Backend is healthy. {result['item_count']} items available."
    except LMSClientError as e:
        return f"❌ Backend error: {e}"
