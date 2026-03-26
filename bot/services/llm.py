"""LLM router with tool calling support."""

import sys
import json
from openai import OpenAI
from config import load_config
from services.api import (
    get_items,
    get_learners,
    get_scores,
    get_pass_rates,
    get_timeline,
    get_groups,
    get_top_learners,
    get_completion_rate,
    trigger_sync,
)

# Initialize OpenAI client for Qwen proxy
_config = load_config()
client = OpenAI(
    api_key=_config["llm_api_key"],
    base_url=_config["llm_api_base_url"]
)

# Tool definitions for all 9 API functions
TOOLS = [
    {
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
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, default 5"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# Map tool names to actual Python functions
TOOL_MAP = {
    "get_items": get_items,
    "get_learners": get_learners,
    "get_scores": get_scores,
    "get_pass_rates": get_pass_rates,
    "get_timeline": get_timeline,
    "get_groups": get_groups,
    "get_top_learners": get_top_learners,
    "get_completion_rate": get_completion_rate,
    "trigger_sync": trigger_sync,
}

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to backend API tools that provide data about labs, tasks, students, and scores.

IMPORTANT: Use the provided tool functions to get data. The system will call tools automatically when you request them.

When a user asks a question:
1. Understand what information they need
2. Use the appropriate tool(s) to get that data
3. Analyze the results
4. Provide a clear, helpful answer based on the actual data

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submission timeline for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

For questions like "which lab has the lowest pass rate":
1. First use get_items to get all labs
2. Then use get_pass_rates for each lab
3. Compare the results and identify the lowest
4. Report the answer with the specific lab name and pass rate

Always be specific and include numbers from the data. If you don't have enough information, 
ask the user to clarify which lab they're interested in.

If the user's message is a greeting or doesn't relate to LMS data, respond naturally 
without calling tools."""


def query_llm(user_message: str) -> str:
    """Query the LLM with tool calling support.
    
    Args:
        user_message: User's natural language query
    
    Returns:
        Formatted response text
    """
    # Initialize conversation
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM with tools
        try:
            response = client.chat.completions.create(
                model=_config["llm_api_model"],
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            return f"❌ LLM error: {str(e)}"
        
        # Check for tool calls
        message = response.choices[0].message
        tool_calls = message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else None
        
        if not tool_calls:
            # No tool calls - LLM has final answer
            response_text = message.content or ""
            print(f"[summary] LLM response: {response_text[:100]}...", file=sys.stderr)
            return response_text
        
        # Add assistant message with tool calls to conversation
        assistant_message = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in tool_calls
            ]
        }
        messages.append(assistant_message)
        
        # Execute tools and collect results
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            
            print(f"[tool] LLM called: {func_name}({func_args})", file=sys.stderr)
            
            # Call the mapped function
            func = TOOL_MAP.get(func_name)
            if func:
                try:
                    result = func(**func_args)
                    print(f"[tool] Result: {str(result)[:100]}...", file=sys.stderr)
                except Exception as e:
                    result = {"error": str(e)}
                    print(f"[tool] Error: {e}", file=sys.stderr)
            else:
                result = {"error": f"Unknown function: {func_name}"}
            
            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str),
            })
        
        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
    
    return "I'm having trouble processing your request. Please try rephrasing."
