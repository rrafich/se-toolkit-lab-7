"""LLM client for intent-based routing."""

import httpx
import json
from typing import Optional


class LlmClient:
    """Client for LLM API with tool calling support.
    
    Sends messages to the LLM with tool definitions and handles
    tool call responses.
    """
    
    def __init__(self, base_url: str, api_key: str, model: str):
        """Initialize the LLM client.
        
        Args:
            base_url: Base URL of the LLM API
            api_key: API key for authentication
            model: Model name to use
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None
    ) -> dict:
        """Send a chat message to the LLM.
        
        Args:
            messages: List of message dicts with role and content
            tools: Optional list of tool definitions
        
        Returns:
            LLM response dict with choices
        
        Raises:
            httpx.RequestError: On connection/network errors
            httpx.HTTPStatusError: On HTTP error responses
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self._headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    
    def extract_tool_calls(self, response: dict) -> list[dict]:
        """Extract tool calls from LLM response.
        
        Args:
            response: LLM response dict
        
        Returns:
            List of tool call dicts with name and arguments
        """
        choices = response.get("choices", [])
        if not choices:
            return []
        
        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        result = []
        for call in tool_calls:
            func = call.get("function", {})
            try:
                arguments = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}
            
            result.append({
                "id": call.get("id"),
                "name": func.get("name"),
                "arguments": arguments
            })
        
        return result
    
    def get_response_text(self, response: dict) -> str:
        """Extract response text from LLM response.
        
        Args:
            response: LLM response dict
        
        Returns:
            Response text content
        """
        choices = response.get("choices", [])
        if not choices:
            return ""
        
        message = choices[0].get("message", {})
        return message.get("content", "")
