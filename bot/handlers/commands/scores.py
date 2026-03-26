"""Handler for /scores command."""

from config import load_config
from services import LmsClient


def handle_scores(args: str = "") -> str:
    """Handle the /scores command.

    Args:
        args: Lab name argument (e.g., "lab-04" or "lab 4")

    Returns:
        Score information for the specified lab
    """
    if not args.strip():
        return (
            "📊 Score Lookup\n\n"
            "Please specify a lab:\n"
            "• /scores lab-01\n"
            "• /scores lab-04\n\n"
            "Use /labs to see all available labs."
        )

    config = load_config()

    if not config["lms_api_base_url"] or not config["lms_api_key"]:
        return (
            "⚠️ Configuration missing.\n\n"
            "Please set LMS_API_BASE_URL and LMS_API_KEY in .env.bot.secret"
        )

    lab_name = args.strip()

    try:
        client = LmsClient(
            base_url=config["lms_api_base_url"], api_key=config["lms_api_key"]
        )

        pass_rates = client.get_pass_rates(lab_name)

        if not pass_rates:
            return (
                f"📊 No scores found for {lab_name}\n\n"
                "The lab may not exist or no students have completed it yet.\n"
                "Use /labs to see available labs."
            )

        lines = [f"📊 Pass rates for {lab_name}:\n"]
        for rate in pass_rates:
            task_title = rate.get("task_title", rate.get("title", "Unknown Task"))
            pass_rate = rate.get("pass_rate", 0) * 100  # Convert to percentage
            attempts = rate.get("attempts", 0)
            lines.append(f"• {task_title}: {pass_rate:.1f}% ({attempts} attempts)")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Error fetching scores: {str(e)}"
