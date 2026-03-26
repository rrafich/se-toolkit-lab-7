"""LLM client with tool calling support for intent-based routing.

This module provides the LlmClient class that wraps the OpenAI-compatible
LLM API and handles tool calling for intent-based natural language routing.
"""

import sys
import json
from typing import Any
from openai import OpenAI

from .lms_client import LmsClient
from . import api as api_funcs


# Tool definitions for the LLM
# Each tool maps a function name to its schema and implementation
TOOL_MAP = {
    "get_items": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks available in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        "func": lambda client: api_funcs.get_items(client),
    },
    "get_learners": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled learners and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        "func": lambda client: api_funcs.get_learners(client),
    },
    "get_scores": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab: api_funcs.get_scores(client, lab),
    },
    "get_pass_rates": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab: api_funcs.get_pass_rates(client, lab),
    },
    "get_timeline": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab: api_funcs.get_timeline(client, lab),
    },
    "get_groups": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab: api_funcs.get_groups(client, lab),
    },
    "get_top_learners": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab, limit=5: api_funcs.get_top_learners(client, lab, limit),
    },
    "get_completion_rate": {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        "func": lambda client, lab: api_funcs.get_completion_rate(client, lab),
    },
    "trigger_sync": {
        "schema": {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh data",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        "func": lambda client: api_funcs.trigger_sync(client),
    },
}

# System prompt for the LLM to guide tool usage
SYSTEM_PROMPT = """You are an intelligent assistant for an LMS (Learning Management System) analytics bot.
Your job is to help users get information about labs, learners, scores, and analytics.

You have access to tools that can fetch data from the backend API. When a user asks a question:
1. Think about what data you need to answer the question
2. Call the appropriate tool(s) to fetch that data
3. Once you have the data, provide a clear, helpful answer

If the user's message is a greeting or casual conversation, respond naturally without using tools.
If the user's message is unclear or ambiguous, ask for clarification about what they want to know.

Available tools:
- get_items: List all labs and tasks
- get_learners: List all enrolled students
- get_scores: Get score distribution for a lab
- get_pass_rates: Get pass rates per task for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get per-group analytics for a lab
- get_top_learners: Get top students for a lab
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker

Always use tools when the user asks about specific data. For multi-step questions (e.g., "which lab has the lowest pass rate"), 
you may need to call multiple tools and compare results.
"""


class LlmClient:
    """Client for LLM API with tool calling support.
    
    Handles communication with the OpenAI-compatible LLM API,
    including tool calling loops for intent-based routing.
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM service
            base_url: Base URL of the LLM API (e.g., http://localhost:42005)
            model: Model name to use (e.g., "qwen3-coder-flash")
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    
    def _get_tool_schemas(self) -> list[dict]:
        """Get the list of tool schemas for the LLM."""
        return [tool["schema"] for tool in TOOL_MAP.values()]
    
    def _execute_tool(self, tool_name: str, arguments: dict[str, Any], lms_client: LmsClient) -> Any:
        """Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            lms_client: LMS client for API calls
            
        Returns:
            The tool execution result
        """
        if tool_name not in TOOL_MAP:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool = TOOL_MAP[tool_name]
        try:
            # Execute the tool function with the LMS client and any arguments
            result = tool["func"](lms_client, **arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def query_llm(self, user_message: str, lms_client: LmsClient) -> str:
        """Query the LLM with a user message and handle tool calling.
        
        This method implements the tool calling loop:
        1. Send user message + tool definitions to LLM
        2. If LLM returns tool_calls, execute them and feed results back
        3. Continue until LLM returns a final text response
        
        Args:
            user_message: The user's input message
            lms_client: LMS client for API calls
            
        Returns:
            The final text response from the LLM
        """
        # Initialize conversation history
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        tool_schemas = self._get_tool_schemas()
        max_iterations = 5  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            try:
                # Call the LLM
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tool_schemas,
                    tool_choice="auto",
                )
                
                choice = response.choices[0]
                message = choice.message
                
                # Check if LLM wants to call tools
                if message.tool_calls:
                    # Debug output to stderr
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                        
                        # Execute the tool
                        result = self._execute_tool(tool_name, tool_args, lms_client)
                        print(f"[tool] Result: {json.dumps(result) if isinstance(result, (dict, list)) else result}", file=sys.stderr)
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                        })
                    
                    print(f"[summary] Feeding {len(message.tool_calls)} tool result(s) back to LLM", file=sys.stderr)
                    # Continue the loop - LLM will process tool results
                else:
                    # No tool calls, return the final response
                    return message.content or "I don't have a response for that."
                    
            except Exception as e:
                print(f"[llm_error] {type(e).__name__}: {e}", file=sys.stderr)
                return f"LLM error: {str(e)}"
        
        # Max iterations reached
        return "I'm having trouble processing your request. Please try again."
