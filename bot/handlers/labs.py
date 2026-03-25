"""Handler for /labs command."""

from services.lms_api import LMSClient, LMSClientError


def _get_client() -> LMSClient:
    """Create an LMS client from config settings."""
    from config import get_settings

    settings = get_settings()
    return LMSClient(
        base_url=settings.lms_api_base_url or "http://localhost:42002",
        api_key=settings.lms_api_key or "",
    )


def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available lab assignments.
    """
    try:
        client = _get_client()
        labs = client.get_labs()
        if not labs:
            return "📋 No labs available."
        
        lines = ["📋 Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            lines.append(f"• {title}")
        return "\n".join(lines)
    except LMSClientError as e:
        return f"❌ Backend error: {e}"
