"""
Priority Management Endpoints
Handles task prioritization requests and responses
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Optional
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
                    "example": {
                        "request_id": "task_001",
                        "urgency_level": "HIGH",
                        "priority_metrics": {
                            "final_priority_score": 7.5,
                            "business_impact_score": 8.0,
                            "risk_score": 6.0
                        },
                        "suggested_sla_hours": 4.0,
                        "escalation_recommended": True
                    }
                }
            }
        },
        400: {"description": "Invalid task request"},
        500: {"description": "Processing error"}
    }
)
async def get_immediate_prioritization(
    task: TaskRequest = Body(..., description="Task details for immediate assessment")
):
    """
    Get immediate AI prioritization result with synchronous processing.
    
    **Processing Features:**
    - Instant priority calculation
    - AI-generated user suggestions
    - Risk assessment analysis
    - SLA recommendations
    - Escalation logic
    
    **Use Cases:**
    - Critical issues requiring immediate assessment
    - Real-time priority validation
    - Interactive support tools
    """
    try:
        result = await get_ai_priority(task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prioritization: {str(e)}")

@router.get(
    "/status/{task_id}",
    summary="Get Task Processing Status", 
    description="Check the processing status and results of a submitted task",
    responses={
        200: {"description": "Task status retrieved"},
        404: {"description": "Task not found"},
        500: {"description": "Server error"}
    }
)
async def get_task_status(
    task_id: str = Path(..., description="Unique task identifier")
):
    """
    Check the processing status of a submitted prioritization task.
    
    **Status Types:**
    - `processing`: Task is being analyzed
    - `completed`: Priority assessment finished
    - `failed`: Processing encountered an error
    - `not_found`: Task ID not recognized
    """
    try:
        # Get services from registry
        redis_cache = get_redis_cache()
        
        # Check if result exists in cache
        cached_result = await redis_cache.get_cached_priority_result(task_id)
        
        if cached_result:
            return {
                "task_id": task_id,
                "status": "completed",
                "result": cached_result,
                "completed_at": datetime.now().isoformat()
            }
        else:
            return {
                "task_id": task_id,
                "status": "processing",
                "message": "Task is still being processed or not found"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task status: {str(e)}")

@router.get(
    "/history",
    summary="Get Prioritization History",
    description="Retrieve historical prioritization data with filtering options"
)
async def get_prioritization_history(
    limit: int = Query(50, description="Maximum number of records to return", ge=1, le=1000),
    category: Optional[TaskCategory] = Query(None, description="Filter by task category"),
    urgency_level: Optional[str] = Query(None, description="Filter by urgency level"),
    requester_role: Optional[UserRole] = Query(None, description="Filter by requester role"),
    days: Optional[int] = Query(7, description="Number of days to look back", ge=1, le=365)
):
    """
    Retrieve historical prioritization data for analytics and reporting.
    
    **Analytics Features:**
    - Priority score trends
    - Category distribution
    - SLA performance metrics
    - User role patterns
    """
    try:
        # This would typically query a database
        # For now, return mock data structure
        return {
            "total_records": 0,
            "filters": {
                "limit": limit,
                "category": category.value if category else None,
                "urgency_level": urgency_level,
                "requester_role": requester_role.value if requester_role else None,
                "days_back": days
            },
            "data": [],
            "message": "History endpoint - database integration required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")
