"""Handler for /start command."""


def handle_start(args: str = "") -> str:
    """Handle the /start command.
    
    Args:
        args: Command arguments (unused for /start)
    
    Returns:
        Welcome message
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you access your learning management system data.\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/health - Check system status\n"
        "/labs - List available labs\n"
        "/scores [lab] - View your scores\n\n"
        "You can also ask me questions in natural language!"
    )
