"""Command handlers for the LMS Telegram Bot."""

from handlers.commands import route_command

from .commands.start import handle_start
from .commands.help import handle_help
from .commands.health import handle_health
from .commands.labs import handle_labs
from .commands.scores import handle_scores
from .commands.message import handle_message, handle_callback

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_message",
    "handle_callback",
]
