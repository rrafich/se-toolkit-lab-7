#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test "message"  # Test mode - print response to stdout
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
from services import LmsClient, LlmClient


# Command registry - maps commands to handler functions
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def route_command(command: str, llm_client: LlmClient | None = None, lms_client: LmsClient | None = None) -> str | tuple[str, Any]:
    """Route a command to the appropriate handler.
    
    If the command doesn't start with '/', treat it as natural language
    and pass it to the LLM for intent-based routing.
    
    Args:
        command: The command string (e.g., "/start" or "what labs are available")
        llm_client: LLM client for natural language queries
        lms_client: LMS client for API calls
        
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
        return (
            f"❓ Unknown command: {cmd}\n\n"
            f"Use /help to see available commands.\n\n"
            f"Or just ask me a question in natural language!"
        )
    
    # Call handler and return response
    return handler(args)


def run_test_mode(message: str, llm_client: LlmClient, lms_client: LmsClient) -> None:
    """Run in test mode - print response to stdout and exit.
    
    Args:
        message: The message to test (command or natural language)
        llm_client: LLM client for natural language queries
        lms_client: LMS client for API calls
    """
    response = route_command(message, llm_client, lms_client)
    
    # Handle tuple response (text + keyboard)
    if isinstance(response, tuple):
        text, _keyboard = response
        print(text)
    else:
        print(response)
    
    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the bot as a Telegram bot using aiogram."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart, Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)
    
    config = load_config()
    
    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)
    
    # Initialize clients
    lms_client = LmsClient(config["lms_api_base_url"], config["lms_api_key"])
    llm_client = LlmClient(config["llm_api_key"], config["llm_api_base_url"], config["llm_api_model"])
    
    # Initialize bot and dispatcher
    bot = Bot(token=config["bot_token"])
    dp = Dispatcher()
    
    print("Telegram bot starting...")
    print(f"Config loaded: LMS_API={config['lms_api_base_url']}, LLM={config['llm_api_base_url']}")
    print("Press Ctrl+C to stop")
    
    # Handler for /start command
    @dp.message(CommandStart())
    async def handle_start_command(message: types.Message):
        """Handle /start command with inline keyboard."""
        try:
            response = handle_start("")
            
            if isinstance(response, tuple):
                text, keyboard_data = response
                # Convert keyboard data to aiogram InlineKeyboardMarkup
                keyboard = types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text=btn["text"],
                                callback_data=btn["callback_data"],
                            )
                            for btn in row
                        ]
                        for row in keyboard_data["buttons"]
                    ]
                )
                await message.answer(text, reply_markup=keyboard)
            else:
                await message.answer(response)
        except Exception as e:
            print(f"[error] handle_start: {e}", file=sys.stderr)
            await message.answer(f"Error: {str(e)}")
    
    # Handler for other commands
    @dp.message(Command("help", "health", "labs", "scores"))
    async def handle_command(message: types.Message):
        """Handle standard commands."""
        try:
            command = message.text or ""
            response = route_command(command, llm_client, lms_client)
            
            if isinstance(response, tuple):
                text, _keyboard = response
                await message.answer(text)
            else:
                await message.answer(response)
        except Exception as e:
            print(f"[error] handle_command: {e}", file=sys.stderr)
            await message.answer(f"Error: {str(e)}")
    
    # Handler for natural language messages
    @dp.message()
    async def handle_text_message(message: types.Message):
        """Handle natural language messages."""
        try:
            text = message.text or ""
            
            # Skip if it's a command (handled by other handlers)
            if text.startswith("/"):
                return
            
            # Send typing action
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Query LLM for response
            response = llm_client.query_llm(text, lms_client)
            await message.answer(response)
        except Exception as e:
            print(f"[error] handle_text_message: {e}", file=sys.stderr)
            await message.answer(f"Error: {str(e)}")
    
    # Handler for callback queries (inline keyboard buttons)
    @dp.callback_query()
    async def handle_callback_query(callback_query: types.CallbackQuery):
        """Handle callback queries from inline keyboard buttons."""
        try:
            callback_data = callback_query.data
            response = handle_callback(callback_data, llm_client, lms_client)
            
            await callback_query.message.answer(response)
            await callback_query.answer()
        except Exception as e:
            print(f"[error] handle_callback_query: {e}", file=sys.stderr)
            await callback_query.answer(f"Error: {str(e)}")
    
    # Run the bot
    import asyncio
    
    async def main():
        await dp.start_polling(bot)
    
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
            print("Usage: bot.py --test <message>")
            print("Example: bot.py --test 'what labs are available'")
            sys.exit(1)
        
        message = sys.argv[2]
        
        # Initialize clients for test mode
        lms_client = LmsClient(config["lms_api_base_url"], config["lms_api_key"])
        llm_client = LlmClient(config["llm_api_key"], config["llm_api_base_url"], config["llm_api_model"])
        
        run_test_mode(message, llm_client, lms_client)
    else:
        # Run as Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
