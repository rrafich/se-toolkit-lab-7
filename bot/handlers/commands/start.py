"""Handler for /start command."""

from typing import Any


def handle_start(args: str = "") -> tuple[str, Any]:
    """Handle the /start command.

    Args:
        args: Command arguments (unused for /start)

    Returns:
        Tuple of (welcome message, inline keyboard markup)
    """
    message = (
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
    
    # Create inline keyboard markup (will be converted to aiogram markup in bot.py)
    keyboard = {
        "type": "inline_keyboard",
        "buttons": [
            [{"text": "📊 Available Labs", "callback_data": "show_labs"}],
            [{"text": "🏆 Top Learners", "callback_data": "top_learners"}],
            [{"text": "📈 Pass Rates", "callback_data": "pass_rates"}],
            [{"text": "❓ Help", "callback_data": "help"}],
        ],
    }
    
    return message, keyboard
