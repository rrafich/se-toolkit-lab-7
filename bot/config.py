"""Configuration loading for the bot."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.

    Looks for .env.bot.secret in the bot directory or parent directory.

    Returns:
        Dictionary with configuration values
    """
    # Try to load from .env.bot.secret
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"

    if not env_file.exists():
        # Try parent directory
        env_file = bot_dir.parent / ".env.bot.secret"

    if env_file.exists():
        load_dotenv(env_file)

    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_base_url": os.getenv("LMS_API_BASE_URL", ""),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_model": os.getenv("LLM_API_MODEL", "qwen3-coder-flash"),
    }
