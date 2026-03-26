"""Handler for /scores command."""


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
            "Use /labs to see all available labs."
        )
    
    # TODO: In Task 2, fetch from LMS API
    lab_name = args.strip()
    return (
        f"📊 Scores for {lab_name}\n\n"
        f"Status: Placeholder\n\n"
        "This will show your actual score once connected to the LMS API."
    )
