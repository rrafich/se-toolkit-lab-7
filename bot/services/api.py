"""LMS API client functions.

All functions return JSON data or a dict with "error" key on failure.
"""

import requests
from config import load_config


def _get_config():
    """Get API configuration."""
    config = load_config()
    return {
        "base_url": config["lms_api_base_url"].rstrip("/"),
        "api_key": config["lms_api_key"],
    }


def _make_request(method: str, endpoint: str, **kwargs) -> dict | list:
    """Make an authenticated request to the LMS API.
    
    Args:
        method: HTTP method ("GET" or "POST")
        endpoint: API endpoint
        **kwargs: Additional arguments for requests
    
    Returns:
        JSON response or {"error": "message"} on failure
    """
    config = _get_config()
    url = f"{config['base_url']}{endpoint}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {config['api_key']}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10, **kwargs)
        else:
            response = requests.post(url, headers=headers, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_items() -> list:
    """Get list of all labs and tasks."""
    result = _make_request("GET", "/items/")
    return result if isinstance(result, list) else []


def get_learners() -> list:
    """Get list of enrolled students."""
    result = _make_request("GET", "/learners/")
    return result if isinstance(result, list) else []


def get_scores(lab: str) -> dict | list:
    """Get score distribution for a lab."""
    return _make_request("GET", f"/analytics/scores?lab={lab}")


def get_pass_rates(lab: str) -> list:
    """Get per-task pass rates for a lab."""
    result = _make_request("GET", f"/analytics/pass-rates?lab={lab}")
    return result if isinstance(result, list) else []


def get_timeline(lab: str) -> list:
    """Get submission timeline for a lab."""
    result = _make_request("GET", f"/analytics/timeline?lab={lab}")
    return result if isinstance(result, list) else []


def get_groups(lab: str) -> list:
    """Get per-group performance for a lab."""
    result = _make_request("GET", f"/analytics/groups?lab={lab}")
    return result if isinstance(result, list) else []


def get_top_learners(lab: str, limit: int = 5) -> list:
    """Get top N learners for a lab."""
    result = _make_request("GET", f"/analytics/top-learners?lab={lab}&limit={limit}")
    return result if isinstance(result, list) else []


def get_completion_rate(lab: str) -> dict:
    """Get completion rate for a lab."""
    return _make_request("GET", f"/analytics/completion-rate?lab={lab}")


def trigger_sync() -> dict:
    """Trigger ETL pipeline sync."""
    return _make_request("POST", "/pipeline/sync", json={})
