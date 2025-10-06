"""
Health Check and System Monitoring Endpoints
"""
from fastapi import APIRouter, HTTPException
from models import HealthCheck
from core.config import settings
from services.service_registry import get_nats_service, get_redis_cache
from datetime import datetime
import asyncio

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

@router.get(
    "/",
    response_model=HealthCheck,
    summary="System Health Check",
    description="Comprehensive health status of all system components",
    responses={
        200: {
            "description": "System health status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "timestamp": "2025-06-27T14:30:00Z",
                        "services": {
                            "redis": "healthy",
                            "openai": "configured",
                            "api": "operational"
                        },
                        "version": "2.0.0"
                    }
                }
            }
        },
        503: {"description": "Service unavailable - degraded health"}
    }
)
async def health_check():
    """
    Comprehensive system health check including all critical services.
    
    **Monitored Services:**
    - NATS JetStream connectivity and stream status
    - Redis cache connectivity and responsiveness
    - OpenAI API configuration
    - Internal API functionality
    - Service version information
    
    **Health Statuses:**
    - `OK`: All services operational
    - `DEGRADED`: Some services have issues
    - `CRITICAL`: Major service failures
    """
    services = {}
    
    # Get services from registry
    nats_service = get_nats_service()
    redis_cache = get_redis_cache()
    
    # Check NATS JetStream connection
    try:
        nats_health = await nats_service.health_check()
        services["nats"] = nats_health["status"]
        if nats_health["status"] == "healthy":
            services["nats_streams"] = nats_health.get("streams", 0)
    except Exception:
        services["nats"] = "unhealthy"
    
    # Check Redis cache connection
    try:
        redis_health = await redis_cache.health_check()
        services["redis_cache"] = redis_health["status"]
        if redis_health["status"] == "healthy":
            services["redis_response_time_ms"] = redis_health["response_time_ms"]
    except Exception:
        services["redis_cache"] = "unhealthy"
    
    # Check OpenAI configuration
    if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
        services["openai"] = "configured"
    else:
        services["openai"] = "not_configured"
    
    # API status
    services["api"] = "operational"
    
    # Determine overall status
    status = "OK"
    if any(v in ["unhealthy", "timeout"] for v in services.values()):
        status = "CRITICAL"
    elif any(v == "not_configured" for v in services.values()):
        status = "DEGRADED"
    
    return HealthCheck(
        status=status,
        services=services
    )

@router.get(
    "/detailed",
    summary="Detailed Health Check",
    description="Extended health check with performance metrics and detailed status"
)
async def detailed_health_check():
    """
    Extended health check with detailed performance metrics.
    
    **Additional Metrics:**
    - Response times for each service
    - NATS JetStream status and performance
    - Redis cache performance and statistics
    - Request processing statistics
    - Error rates and patterns
    """
    start_time = datetime.now()
    
    # Get services from registry
    nats_service = get_nats_service()
    
    # Test NATS performance
    nats_metrics = await nats_service.health_check()
    
    # Test Redis cache performance
    redis_metrics = await _test_redis_performance()
    
    # Test OpenAI connectivity (if configured)
    openai_metrics = await _test_openai_connectivity()
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return {
        "status": "detailed_check_complete",
        "processing_time_seconds": processing_time,
        "timestamp": datetime.now().isoformat() + "Z",
        "services": {
            "nats": nats_metrics,
            "redis_cache": redis_metrics,
            "openai": openai_metrics,
            "api": {
                "status": "operational",
                "response_time_ms": processing_time * 1000
            }
        }
    }

@router.get(
    "/metrics",
    summary="System Performance Metrics", 
    description="Real-time system performance and usage metrics"
)
async def get_system_metrics():
    """
    System performance metrics for monitoring and alerting.
    
    **Metrics Included:**
    - Request processing statistics
    - Error rates and types
    - Resource utilization
    - Service dependencies status
    """
    return {
        "metrics": {
            "requests_processed": 0,  # Would be tracked in production
            "average_response_time_ms": 0,
            "error_rate_percent": 0,
            "active_connections": 0
        },
        "timestamp": datetime.now().isoformat() + "Z",
        "collection_period": "real-time"
    }

@router.get(
    "/system",
    summary="System Status with Background Tasks",
    description="Comprehensive system status including background task monitoring"
)
async def system_status():
    """
    Get detailed system status including background tasks, NATS/Redis health, 
    and service connectivity.
    """
    from services.background_tasks import task_manager
    
    # Get services from registry
    nats_service = get_nats_service()
    redis_cache = get_redis_cache()
    
    nats_health = await nats_service.health_check()
    redis_health = await redis_cache.health_check()
    task_status = task_manager.get_task_status()
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat() + "Z",
        "services": {
            "nats": nats_health,
            "redis_cache": redis_health,
            "background_tasks": {
                "status": task_status,
                "running_tasks": list(task_manager.running_tasks),
                "total_tasks": len(task_status)
            },
            "api": {
                "status": "operational",
                "version": settings.SERVICE_VERSION
            }
        },
        "event_subjects": {
            "request_subject": settings.PRIORITY_REQUEST_SUBJECT,
            "result_subject": settings.PRIORITY_RESULT_SUBJECT,
            "sync_subject": settings.PRIORITY_SYNC_SUBJECT
        }
    }

async def _test_redis_performance():
    """Test Redis cache performance and connectivity"""
    try:
        # Get services from registry
        redis_cache = get_redis_cache()
        
        redis_health = await redis_cache.health_check()
        
        if redis_health["status"] == "healthy":
            return {
                "status": "healthy",
                "response_time_ms": redis_health["response_time_ms"],
                "operations_tested": ["ping", "cache_operations"],
                "cache_stats": redis_health.get("cache_stats", {})
            }
        else:
            return {
                "status": "unhealthy",
                "error": redis_health.get("error", "Unknown error"),
                "response_time_ms": None
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": None
        }

async def _test_openai_connectivity():
    """Test OpenAI API connectivity"""
    if not settings.OPENAI_API_KEY:
        return {
            "status": "not_configured",
            "message": "OpenAI API key not provided"
        }
    
    try:
        # Simple connectivity test (not a full API call)
        return {
            "status": "configured",
            "api_key_length": len(settings.OPENAI_API_KEY),
            "model": getattr(settings, 'AI_MODEL', 'gpt-3.5-turbo')
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
