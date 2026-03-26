"""Handler for /labs command."""


def handle_labs(args: str = "") -> str:
    """Handle the /labs command.
    
    Args:
        args: Command arguments (unused for /labs)
    
    Returns:
        List of available labs
    """
    # TODO: In Task 2, fetch from LMS API
    return (
        "📋 Available Labs:\n\n"
        "• Lab 01 – Products, Architecture & Roles\n"
        "• Lab 02 — Run, Fix, and Deploy a Backend Service\n"
        "• Lab 03 — Backend API: Explore, Debug, Implement, Deploy\n"
        "• Lab 04 — Testing, Front-end, and AI Agents\n"
        "• Lab 05 — Data Pipeline and Analytics Dashboard\n"
        "• Lab 06 — Build Your Own Agent\n"
        "• Lab 07 — Build a Client with an AI Coding Agent\n\n"
        "Use /scores [lab_name] to view your score for a specific lab."
    )
