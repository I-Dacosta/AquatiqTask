"""
Global Service Registry
Provides centralized access to NATS and Redis services across the application
"""
from services.nats_service import NATSJetStreamService
from services.redis_cache import RedisCacheService

# Global service instances - initialized in main.py
nats_service: NATSJetStreamService = None
redis_cache: RedisCacheService = None

def initialize_services():
    """Initialize global service instances"""
    global nats_service, redis_cache
    nats_service = NATSJetStreamService()
    redis_cache = RedisCacheService()
    return nats_service, redis_cache

def get_nats_service() -> NATSJetStreamService:
    """Get the global NATS service instance"""
    if nats_service is None:
        raise RuntimeError("NATS service not initialized. Call initialize_services() first.")
    return nats_service

def get_redis_cache() -> RedisCacheService:
    """Get the global Redis cache service instance"""
    if redis_cache is None:
        raise RuntimeError("Redis cache service not initialized. Call initialize_services() first.")
    return redis_cache
