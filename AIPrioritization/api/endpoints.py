from fastapi import APIRouter, BackgroundTasks, HTTPException
from models import TaskRequest, HealthCheck, AIPriorityResult
from services.redis_service import redis_publisher
from services.ai_service import get_ai_priority
from core.config import settings
from datetime import datetime
import redis.asyncio as redis

router = APIRouter(prefix="/api/v1", tags=["AI Prioritization"])

@router.post("/prioritize", response_model=dict, status_code=202)
async def prioritize_request(task: TaskRequest, background_tasks: BackgroundTasks):
    """Submit a task for AI-powered prioritization"""
    try:
        # Publish to Redis for async processing
        background_tasks.add_task(
            redis_publisher, 
            settings.PRIORITIZATION_REQUEST_CHANNEL, 
            task.json()
        )
        return {
            "message": "Task submitted for prioritization",
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting task: {str(e)}")

@router.post("/prioritize/sync", response_model=AIPriorityResult)
async def prioritize_request_sync(task: TaskRequest):
    """Get immediate AI prioritization result (synchronous)"""
    try:
        result = await get_ai_priority(task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prioritization: {str(e)}")

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    services = {}
    
    # Check Redis connection
    try:
        redis_client = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
        await redis_client.ping()
        services["redis"] = "healthy"
        await redis_client.close()
    except Exception:
        services["redis"] = "unhealthy"
    
    # Check OpenAI API key
    if settings.OPENAI_API_KEY:
        services["openai"] = "configured"
    else:
        services["openai"] = "not_configured"
    
    return HealthCheck(
        status="OK" if all(v != "unhealthy" for v in services.values()) else "DEGRADED",
        services=services
    )

@router.get("/metrics/categories")
async def get_category_metrics():
    """Get category-based priority metrics"""
    from models import TaskCategory
    return {
        "categories": [category.value for category in TaskCategory],
        "urgency_multipliers": {
            "SECURITY": 1.5,
            "INFRASTRUCTURE": 1.3,
            "MEETING_PREP": 1.2,
            "SUPPORT": 1.0,
            "DEVELOPMENT": 0.8,
            "MAINTENANCE": 0.7,
            "TRAINING": 0.6,
            "COMPLIANCE": 0.9
        }
    }

@router.get("/metrics/roles")
async def get_role_metrics():
    """Get role-based priority weights"""
    from models import UserRole
    return {
        "roles": [role.value for role in UserRole],
        "priority_weights": {
            "CEO": 5.0,
            "CFO": 4.5,
            "CTO": 4.5,
            "MANAGER": 3.5,
            "IT_ADMIN": 3.0,
            "DEVELOPER": 2.5,
            "EMPLOYEE": 2.0,
            "CLIENT": 2.5
        }
    }
