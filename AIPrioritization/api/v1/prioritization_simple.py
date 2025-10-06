"""
Simplified Priority Management Endpoints
Handles task prioritization requests and responses without NATS
"""
from fastapi import APIRouter, HTTPException, Body
from models import TaskRequest, AIPriorityResult
from services.ai_service import get_ai_priority
from datetime import datetime

router = APIRouter(prefix="/prioritization", tags=["Priority Management"])

@router.post(
    "/sync", 
    response_model=AIPriorityResult,
    summary="Get Immediate Priority Assessment",
    description="Get synchronous AI prioritization result with instant processing"
)
async def prioritize_task_sync(
    task: TaskRequest = Body(..., description="Task details for prioritization")
) -> AIPriorityResult:
    """
    Get immediate AI prioritization result.
    
    **Features:**
    - Synchronous processing
    - Automatic metric calculation from task description
    - GDPR-compliant sensitive data handling
    - Advanced AI priority scoring
    """
    try:
        # Get AI priority assessment
        result = await get_ai_priority(task)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prioritization: {str(e)}")

@router.get("/health")
async def prioritization_health():
    """Health check for prioritization service"""
    return {
        "service": "prioritization",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }