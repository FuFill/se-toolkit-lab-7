"""Handler for /scores command."""

from services.lms_api import LMSClient, LMSClientError


def _get_client() -> LMSClient:
    """Create an LMS client from config settings."""
    from config import get_settings

    settings = get_settings()
    return LMSClient(
        base_url=settings.lms_api_base_url or "http://localhost:42002",
        api_key=settings.lms_api_key or "",
    )


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: Optional lab assignment identifier.

    Returns:
        Scores information for the specified lab or general scores summary.
    """
    if lab_id is None:
        return "📊 Scores\n\nPlease specify a lab ID:\n/scores lab-04"

    try:
        client = _get_client()
        pass_rates = client.get_pass_rates(lab_id)
        if not pass_rates:
            return f"📊 No scores found for {lab_id}."
        
        lines = [f"📊 Pass rates for {lab_id}:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown task")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"• {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except LMSClientError as e:
        return f"❌ Backend error: {e}"
