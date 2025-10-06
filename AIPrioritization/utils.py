"""Utility functions for the AI Priority Engine"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def serialize_datetime(obj: Any) -> str:
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON data with error handling"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return None

def calculate_business_hours_between(start: datetime, end: datetime) -> float:
    """Calculate business hours between two datetime objects"""
    # Simplified calculation - assumes 8 hour business days, Mon-Fri
    total_hours = (end - start).total_seconds() / 3600
    
    # This is a simplified version - a more complete implementation would
    # account for weekends, holidays, and specific business hours
    business_days = total_hours / 24 * (5/7)  # Approximate business days
    business_hours = business_days * 8  # 8 hours per business day
    
    return max(0, business_hours)

def format_priority_message(task_id: str, priority: str, score: float, reasoning: str) -> str:
    """Format a priority message for Teams/notifications"""
    priority_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "📋",
        "low": "📝"
    }
    
    emoji = priority_emoji.get(priority.lower(), "📋")
    
    return f"""
{emoji} **Priority Alert: {priority.upper()}**

**Task ID:** {task_id}
**Priority Score:** {score}/10
**Reasoning:** {reasoning}

Please review and take appropriate action.
    """.strip()

class PriorityEngineError(Exception):
    """Custom exception for Priority Engine errors"""
    pass

class RedisConnectionError(PriorityEngineError):
    """Exception raised when Redis connection fails"""
    pass

class TaskValidationError(PriorityEngineError):
    """Exception raised when task validation fails"""
    pass
