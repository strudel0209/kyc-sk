"""Utility functions for the KYC system."""

import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_json_loads(json_str: str, default_value: Any = None) -> Any:
    """Safely parse a JSON string without crashing on invalid JSON."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON: {json_str[:100]}...")
        return default_value

def normalize_client_name(name: str) -> str:
    """Normalize a client name for consistent matching."""
    if not name or name == "UNKNOWN":
        return "unknown"
    
    # Convert to lowercase and remove extra whitespace
    normalized = " ".join(name.lower().split())
    return normalized