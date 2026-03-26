"""Command handlers for the LMS Telegram Bot.

Handlers are plain functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or the Telegram bot.
"""

from services.llm import query_llm


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
        "Try asking me questions like:\n"
        "• What labs are available?\n"
        "• Show me scores for lab 4\n"
        "• Which lab has the lowest pass rate?\n"
        "• Who are the top 5 students?\n\n"
        "Or use commands:\n"
        "/help - Show help information\n"
        "/health - Check system status\n"
        "/labs - List available labs\n"
        "/scores [lab] - View your scores"
    )


def handle_help(args: str = "") -> str:
    """Handle the /help command.
    
    Args:
        args: Command arguments (unused for /help)
    
    Returns:
        Help message with available commands
    """
    return (
        "📚 LMS Bot Help\n\n"
        "You can ask me questions in natural language:\n"
        "• What labs are available?\n"
        "• Show me scores for lab 4\n"
        "• Which lab has the lowest pass rate?\n"
        "• Who are the top 5 students in lab 3?\n\n"
        "Or use slash commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - System status\n"
        "/labs - List all labs\n"
        "/scores [lab_name] - View scores for a specific lab"
    )


def handle_health(args: str = "") -> str:
    """Handle the /health command.
    
    Args:
        args: Command arguments (unused for /health)
    
    Returns:
        System health status
    """
    # Use LLM to check health
    return query_llm("Check if the backend is healthy and report status")


def handle_labs(args: str = "") -> str:
    """Handle the /labs command.
    
    Args:
        args: Command arguments (unused for /labs)
    
    Returns:
        List of available labs
    """
    return query_llm("What labs are available? List them all.")


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
            "Or just ask me: 'show me scores for lab 4'"
        )
    
    return query_llm(f"Show me scores for {args.strip()}")


def handle_message(text: str) -> str:
    """Handle natural language messages.
    
    Args:
        text: User's message text
    
    Returns:
        Response from the LLM
    """
    return query_llm(text)


def route_command(command: str) -> str:
    """Route a command or message to the appropriate handler.
    
    Args:
        command: The command string or message
    
    Returns:
        The handler's response text
    """
    # Check if it's a slash command
    if command.startswith("/"):
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        handlers = {
            "/start": handle_start,
            "/help": handle_help,
            "/health": handle_health,
            "/labs": handle_labs,
            "/scores": handle_scores,
        }
        
        handler = handlers.get(cmd)
        if handler:
            return handler(args)
        else:
            return f"❓ Unknown command: {cmd}\n\nUse /help to see available commands."
    else:
        # Natural language message
        return handle_message(command)
