"""API wrapper functions for LLM tool calling.

These functions wrap the LMS API endpoints and return JSON-serializable data
that can be fed back to the LLM after tool execution.
"""

from typing import Any
from .lms_client import LmsClient


def get_items(client: LmsClient) -> list[dict]:
    """Get list of all labs and tasks.
    
    Returns:
        List of items with type, id, and title information.
    """
    return client.get_items()


def get_learners(client: LmsClient) -> list[dict]:
    """Get list of enrolled learners and their groups.
    
    Returns:
        List of learners with name, group, and id information.
    """
    result = client._make_request("/learners/")
    return result if isinstance(result, list) else []


def get_scores(client: LmsClient, lab: str) -> list[dict]:
    """Get score distribution (4 buckets) for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        
    Returns:
        List of score distribution data.
    """
    result = client._make_request(f"/analytics/scores?lab={lab}")
    return result if isinstance(result, list) else []


def get_pass_rates(client: LmsClient, lab: str) -> list[dict]:
    """Get per-task average scores and attempt counts for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        
    Returns:
        List of pass rate data per task.
    """
    return client.get_pass_rates(lab)


def get_timeline(client: LmsClient, lab: str) -> list[dict]:
    """Get submissions per day for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        
    Returns:
        List of timeline data with dates and submission counts.
    """
    result = client._make_request(f"/analytics/timeline?lab={lab}")
    return result if isinstance(result, list) else []


def get_groups(client: LmsClient, lab: str) -> list[dict]:
    """Get per-group scores and student counts for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        
    Returns:
        List of group data with scores and student counts.
    """
    result = client._make_request(f"/analytics/groups?lab={lab}")
    return result if isinstance(result, list) else []


def get_top_learners(client: LmsClient, lab: str, limit: int = 5) -> list[dict]:
    """Get top N learners by score for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        limit: Number of top learners to return (default: 5)
        
    Returns:
        List of top learners with their scores.
    """
    result = client._make_request(f"/analytics/top-learners?lab={lab}&limit={limit}")
    return result if isinstance(result, list) else []


def get_completion_rate(client: LmsClient, lab: str) -> dict[str, Any]:
    """Get completion rate percentage for a lab.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
        
    Returns:
        Dictionary with completion rate data.
    """
    result = client._make_request(f"/analytics/completion-rate?lab={lab}")
    return result if isinstance(result, dict) else {}


def trigger_sync(client: LmsClient) -> dict[str, Any]:
    """Trigger a data sync from the autochecker.
    
    Returns:
        Dictionary with sync status information.
    """
    # POST request to trigger sync
    url = f"{client.base_url}/pipeline/sync"
    import httpx
    with httpx.Client() as http_client:
        response = http_client.post(url, headers=client._headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
