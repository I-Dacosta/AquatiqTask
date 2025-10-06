import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4.1")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.3"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "800"))
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7"))
    
    # NATS Configuration (Primary Event Stream)
    NATS_HOST: str = os.getenv("NATS_HOST", "localhost")
    NATS_PORT: int = int(os.getenv("NATS_PORT", "4222"))
    NATS_USERNAME: str = os.getenv("NATS_USERNAME", "")
    NATS_PASSWORD: str = os.getenv("NATS_PASSWORD", "")
    NATS_TLS_ENABLED: bool = os.getenv("NATS_TLS_ENABLED", "false").lower() == "true"
    
    # JetStream Configuration
    JETSTREAM_ENABLED: bool = os.getenv("JETSTREAM_ENABLED", "true").lower() == "true"
    JETSTREAM_DOMAIN: str = os.getenv("JETSTREAM_DOMAIN", "priority")
    JETSTREAM_MAX_MEMORY: str = os.getenv("JETSTREAM_MAX_MEMORY", "256MB")
    JETSTREAM_MAX_STORAGE: str = os.getenv("JETSTREAM_MAX_STORAGE", "1GB")
    
    # NATS Subjects
    PRIORITY_REQUEST_SUBJECT: str = os.getenv("PRIORITY_REQUEST_SUBJECT", "prioritization.request")
    PRIORITY_RESULT_SUBJECT: str = os.getenv("PRIORITY_RESULT_SUBJECT", "prioritization.result")
    PRIORITY_SYNC_SUBJECT: str = os.getenv("PRIORITY_SYNC_SUBJECT", "prioritization.sync")
    
    # Legacy Redis Channels (for backward compatibility - deprecated in favor of NATS)
    PRIORITIZATION_REQUEST_CHANNEL: str = os.getenv("PRIORITIZATION_REQUEST_CHANNEL", "prioritization_requests")
    PRIORITIZATION_RESULT_CHANNEL: str = os.getenv("PRIORITIZATION_RESULT_CHANNEL", "prioritization_results")
    PRIORITIZE_CHANNEL: str = os.getenv("PRIORITIZE_CHANNEL", "prioritize_events")
    RESULTS_CHANNEL: str = os.getenv("RESULTS_CHANNEL", "prioritize_results")
    
    # Redis Configuration (Caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "10000"))
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # Priority Settings
    MAX_PRIORITY_SCORE: float = float(os.getenv("MAX_PRIORITY_SCORE", "10.0"))
    DEFAULT_SLA_HOURS: float = float(os.getenv("DEFAULT_SLA_HOURS", "24.0"))
    ESCALATION_THRESHOLD: float = float(os.getenv("ESCALATION_THRESHOLD", "8.0"))
    CRITICAL_THRESHOLD: float = float(os.getenv("CRITICAL_THRESHOLD", "8.5"))
    HIGH_THRESHOLD: float = float(os.getenv("HIGH_THRESHOLD", "6.5"))
    MEDIUM_THRESHOLD: float = float(os.getenv("MEDIUM_THRESHOLD", "4.0"))
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Service Configuration
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "ai-priority-engine")
    SERVICE_VERSION: str = os.getenv("SERVICE_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
