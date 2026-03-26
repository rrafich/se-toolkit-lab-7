"""Handler for natural language messages."""

from typing import Any
from ...services.lms_client import LmsClient
from ...services.llm_client import LlmClient


def handle_message(text: str, llm_client: LlmClient, lms_client: LmsClient) -> str:
    """Handle a natural language message from the user.
    
    This function passes the user's message to the LLM for intent-based routing.
    The LLM will decide which tools to call and generate a response.
    
    Args:
        text: The user's message text
        llm_client: LLM client for querying the language model
        lms_client: LMS client for API calls
        
    Returns:
        The LLM's response text
    """
    return llm_client.query_llm(text, lms_client)


def handle_callback(callback_data: str, llm_client: LlmClient, lms_client: LmsClient) -> str:
    """Handle a callback query from an inline keyboard button.
    
    Args:
        callback_data: The callback data from the button
        llm_client: LLM client for querying the language model
        lms_client: LMS client for API calls
        
    Returns:
        Response text for the callback
    """
    # Map callback data to natural language queries
    callback_queries = {
        "show_labs": "What labs are available?",
        "top_learners": "Show me the top 5 learners overall.",
        "pass_rates": "Show me the pass rates for the latest lab.",
        "help": "What can you do? Explain your capabilities.",
    }
    
    query = callback_queries.get(callback_data, f"User clicked: {callback_data}. What does this do?")
    return llm_client.query_llm(query, lms_client)
