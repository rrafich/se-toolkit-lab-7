#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run python bot.py              # Run as Telegram bot
    uv run python bot.py --test "hello"  # Test mode - print response to stdout
"""

import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers.commands import route_command


def run_test_mode(message: str) -> None:
    """Run in test mode - print response to stdout and exit.
    
    Args:
        message: The message or command to test
    """
    response = route_command(message)
    print(response)
    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot.
    
    Note: This is a placeholder. Task 4 will implement the actual
    Telegram bot using aiogram library.
    """
    config = load_config()
    
    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)
    
    # TODO: Task 4 - Implement Telegram bot with aiogram
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
            print("Usage: bot.py --test <command|message>")
            print("Example: bot.py --test '/start'")
            print("Example: bot.py --test 'what labs are available'")
            sys.exit(1)
        
        # Everything after --test is the message
        message = " ".join(sys.argv[2:])
        run_test_mode(message)
    else:
        # Run as Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
