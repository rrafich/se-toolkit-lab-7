#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test "/start"  # Test mode - print response to stdout
"""

import sys
from pathlib import Path

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
)


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
        The handler's response text
    """
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Look up handler
    handler = COMMANDS.get(cmd)
    
    if handler is None:
        return (
            f"❓ Unknown command: {cmd}\n\n"
            f"Use /help to see available commands."
        )
    
    # Call handler and return response
    return handler(args)


def run_test_mode(command: str) -> None:
    """Run in test mode - print response to stdout and exit.
    
    Args:
        command: The command to test (e.g., "/start")
    """
    response = run_command(command)
    print(response)
    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot.
    
    Note: This is a placeholder. Task 2 will implement the actual
    Telegram bot using python-telegram-bot library.
    """
    config = load_config()
    
    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)
    
    # TODO: Task 2 - Implement Telegram bot
    print("Telegram bot starting... (placeholder)")
    print(f"Config loaded: LMS_API={config['lms_api_base_url']}")
    print("Press Ctrl+C to stop")
    
    # Keep running (placeholder)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nBot stopped.")


def main() -> None:
    """Main entry point."""
    # Check for test mode
    if len(sys.argv) >= 2 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: bot.py --test <command>")
            print("Example: bot.py --test '/start'")
            sys.exit(1)
        
        command = sys.argv[2]
        run_test_mode(command)
    else:
        # Run as Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
