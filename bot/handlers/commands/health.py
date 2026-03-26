"""Handler for /health command."""


def handle_health(args: str = "") -> str:
    """Handle the /health command.
    
    Args:
        args: Command arguments (unused for /health)
    
    Returns:
        System health status
    """
    # TODO: In Task 2, check actual backend health
    return "✅ System Status:\n\n• Bot: Running\n• Backend: Connected\n• LLM Service: Available\n\nAll systems operational!"
