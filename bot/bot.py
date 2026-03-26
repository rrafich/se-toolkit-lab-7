#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run python bot.py              # Run as Telegram bot
    uv run python bot.py --test "hello"  # Test mode - print response to stdout
"""

import sys
from pathlib import Path
from typing import Any

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_message,
    handle_callback,
)
from services import route_query


# Command registry - maps commands to handler functions
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def run_command(command: str) -> str:
    """Run a command and return the response.

    Args:
        command: The command string (e.g., "/start" or "/scores lab-04")

    Returns:
        The handler's response (string or tuple of text + keyboard)
    """
    command = command.strip()
    
    # If not a command (doesn't start with /), treat as natural language
    if not command.startswith("/"):
        if llm_client is None or lms_client is None:
            return "Error: LLM/LMS clients not available for natural language processing."
        return handle_message(command, llm_client, lms_client)
    
    # Parse command and arguments
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Look up handler
    handler = COMMANDS.get(cmd)

    if handler is None:
        return f"❓ Unknown command: {cmd}\n\nUse /help to see available commands."

    # Call handler and return response
    return handler(args)


def run_test_mode(message: str, llm_client: LlmClient, lms_client: LmsClient) -> None:
    """Run in test mode - print response to stdout and exit.

    Args:
        command: The command or message to test
    """
    response = route_command(message, llm_client, lms_client)
    
    # Handle tuple response (text + keyboard)
    if isinstance(response, tuple):
        text, _keyboard = response
        print(text)
    else:
        print(response)
    
    sys.exit(0)


def handle_natural_language(message: str) -> str:
    """Handle natural language messages via LLM routing.

    Args:
        message: User's natural language message

    Returns:
        Response from the intent router
    """
    return route_query(message)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot.

    Note: This is a placeholder. Task 4 will implement the actual
    Telegram bot using python-telegram-bot library.
    """
    config = load_config()

    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    # TODO: Task 4 - Implement Telegram bot
    print("Telegram bot starting... (placeholder)")
    print(f"Config loaded: LMS_API={config['lms_api_base_url']}")
    print("Press Ctrl+C to stop")

    # Keep running (placeholder)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
    finally:
        asyncio.run(bot.close())


def main() -> None:
    """Main entry point."""
    config = load_config()
    
    # Check for test mode
    if len(sys.argv) >= 2 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: bot.py --test <command|message>")
            print("Example: bot.py --test '/start'")
            print("Example: bot.py --test 'what labs are available'")
            sys.exit(1)

        message = sys.argv[2]

        # Check if it's a slash command or natural language
        if message.startswith("/"):
            run_test_mode(message)
        else:
            # Natural language query - use intent router
            response = handle_natural_language(message)
            print(response)
            sys.exit(0)
    else:
        # Run as Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
