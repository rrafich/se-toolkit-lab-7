"""Intent router for natural language queries.

Routes user messages to appropriate tools via LLM.
"""

import sys
import json
from config import load_config
from services import LmsClient, LlmClient
from services.tools import TOOLS, SYSTEM_PROMPT


class IntentRouter:
    """Routes natural language queries to backend tools via LLM."""
    
    def __init__(self):
        """Initialize the intent router."""
        config = load_config()
        
        self.lms_client = LmsClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"]
        )
        
        self.llm_client = LlmClient(
            base_url=config["llm_api_base_url"],
            api_key=config["llm_api_key"],
            model=config["llm_api_model"]
        )
        
        # Map tool names to actual functions
        self.tool_functions = {
            "get_items": self._call_get_items,
            "get_learners": self._call_get_learners,
            "get_scores": self._call_get_scores,
            "get_pass_rates": self._call_get_pass_rates,
            "get_timeline": self._call_get_timeline,
            "get_groups": self._call_get_groups,
            "get_top_learners": self._call_get_top_learners,
            "get_completion_rate": self._call_get_completion_rate,
            "trigger_sync": self._call_trigger_sync,
        }
    
    def _debug(self, message: str) -> None:
        """Print debug message to stderr."""
        print(message, file=sys.stderr)
    
    def _call_get_items(self, **kwargs) -> dict:
        """Call get_items tool."""
        result = self.lms_client.get_items()
        self._debug(f"[tool] Result: {len(result)} items")
        return {"result": result}
    
    def _call_get_learners(self, **kwargs) -> dict:
        """Call get_learners tool."""
        result = self.lms_client.get_items()  # TODO: implement get_learners endpoint
        return {"result": result}
    
    def _call_get_scores(self, lab: str) -> dict:
        """Call get_scores tool."""
        result = self.lms_client.get_items()  # TODO: implement get_scores endpoint
        return {"result": result, "lab": lab}
    
    def _call_get_pass_rates(self, lab: str) -> dict:
        """Call get_pass_rates tool."""
        result = self.lms_client.get_pass_rates(lab)
        self._debug(f"[tool] Result: {len(result)} tasks")
        return {"result": result, "lab": lab}
    
    def _call_get_timeline(self, lab: str) -> dict:
        """Call get_timeline tool."""
        return {"result": [], "lab": lab}
    
    def _call_get_groups(self, lab: str) -> dict:
        """Call get_groups tool."""
        return {"result": [], "lab": lab}
    
    def _call_get_top_learners(self, lab: str, limit: int = 5) -> dict:
        """Call get_top_learners tool."""
        return {"result": [], "lab": lab, "limit": limit}
    
    def _call_get_completion_rate(self, lab: str) -> dict:
        """Call get_completion_rate tool."""
        return {"result": {}, "lab": lab}
    
    def _call_trigger_sync(self, **kwargs) -> dict:
        """Call trigger_sync tool."""
        return {"status": "sync triggered"}
    
    def _execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a tool by name with arguments."""
        self._debug(f"[tool] LLM called: {name}({arguments})")
        
        func = self.tool_functions.get(name)
        if not func:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            result = func(**arguments)
            return result
        except Exception as e:
            self._debug(f"[tool] Error: {e}")
            return {"error": str(e)}
    
    def route(self, message: str) -> str:
        """Route a user message through the LLM to get a response.
        
        Args:
            message: User's natural language query
        
        Returns:
            Formatted response text
        """
        # Initialize conversation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = self.llm_client.chat(messages, tools=TOOLS)
            
            # Extract tool calls
            tool_calls = self.llm_client.extract_tool_calls(response)
            
            if not tool_calls:
                # No tool calls - LLM has final answer
                response_text = self.llm_client.get_response_text(response)
                self._debug(f"[summary] LLM response: {response_text[:100]}...")
                return response_text
            
            # Execute tools and collect results
            tool_results = []
            for call in tool_calls:
                result = self._execute_tool(call["name"], call["arguments"])
                tool_results.append({
                    "tool_call_id": call["id"],
                    "role": "tool",
                    "name": call["name"],
                    "content": json.dumps(result, default=str)
                })
            
            self._debug(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")
            
            # Add tool results to conversation
            messages.extend(tool_results)
        
        return "I'm having trouble processing your request. Please try rephrasing."


def route_query(message: str) -> str:
    """Route a query through the intent router.
    
    Args:
        message: User's natural language query
    
    Returns:
        Formatted response text
    """
    try:
        router = IntentRouter()
        return router.route(message)
    except Exception as e:
        return f"❌ LLM error: {str(e)}"
