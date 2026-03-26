"""Handler for /help command."""


def handle_help(args: str = "") -> str:
    """Handle the /help command.
    
    Args:
        args: Command arguments (unused for /help)
    
    Returns:
        Help message with available commands
    """
    return (
        "📚 LMS Bot Help\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - System status\n"
        "/labs - List all labs\n"
        "/scores [lab_name] - View scores for a specific lab\n\n"
        "Examples:\n"
        "• /scores lab-01\n"
        "• What labs are available?\n"
        "• Show my score for lab 4"
    )
