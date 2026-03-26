"""Handler for /health command."""

from config import load_config
from services import LmsClient


def handle_health(args: str = "") -> str:
    """Handle the /health command.

    Args:
        args: Command arguments (unused for /health)

    Returns:
        System health status from backend
    """
    config = load_config()

    if not config["lms_api_base_url"] or not config["lms_api_key"]:
        return (
            "⚠️ Configuration missing.\n\n"
            "Please set LMS_API_BASE_URL and LMS_API_KEY in .env.bot.secret"
        )

    client = LmsClient(
        base_url=config["lms_api_base_url"], api_key=config["lms_api_key"]
    )

    is_healthy, message = client.is_healthy()

    if is_healthy:
        return f"✅ {message}"
    else:
        return f"❌ {message}"
