"""Handler for /labs command."""

from config import load_config
from services import LmsClient


def handle_labs(args: str = "") -> str:
    """Handle the /labs command.

    Args:
        args: Command arguments (unused for /labs)

    Returns:
        List of available labs from the backend
    """
    config = load_config()

    if not config["lms_api_base_url"] or not config["lms_api_key"]:
        return (
            "⚠️ Configuration missing.\n\n"
            "Please set LMS_API_BASE_URL and LMS_API_KEY in .env.bot.secret"
        )

    try:
        client = LmsClient(
            base_url=config["lms_api_base_url"], api_key=config["lms_api_key"]
        )

        labs = client.get_labs()

        if not labs:
            return "📋 No labs found.\n\nThe backend may not have any labs yet."

        lines = ["📋 Available Labs:\n"]
        for lab in labs:
            title = lab.get("title", "Unknown Lab")
            lines.append(f"• {title}")

        lines.append("\nUse /scores [lab_name] to view your score for a specific lab.")
        return "\n".join(lines)

    except Exception as e:
        return f"❌ Error fetching labs: {str(e)}"
