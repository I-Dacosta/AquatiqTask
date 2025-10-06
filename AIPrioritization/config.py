"""Configuration settings for the AI Priority Engine service"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    PRIORITIZE_CHANNEL: str = os.getenv("PRIORITIZE_CHANNEL", "prioritize_events")
    RESULTS_CHANNEL: str = os.getenv("RESULTS_CHANNEL", "prioritize_results")
    
    # Service Configuration
    SERVICE_NAME: str = "ai-priority-engine"
    SERVICE_VERSION: str = "1.0.0"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AI Engine Settings
    DEFAULT_BUSINESS_VALUE: int = 5
    DEFAULT_RISK_LEVEL: int = 5
    
    # Priority Thresholds
    CRITICAL_THRESHOLD: float = 8.5
    HIGH_THRESHOLD: float = 6.5
    MEDIUM_THRESHOLD: float = 4.0
    
    # Time Constants (in hours)
    CRITICAL_TIME_THRESHOLD: float = 1.0
    HIGH_TIME_THRESHOLD: float = 4.0
    MEDIUM_TIME_THRESHOLD: float = 24.0

settings = Settings()
