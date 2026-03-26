"""Command handlers for the LMS Telegram Bot.

Handlers are plain functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or the Telegram bot.
"""

from .commands.start import handle_start
from .commands.help import handle_help
from .commands.health import handle_health
from .commands.labs import handle_labs
from .commands.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
