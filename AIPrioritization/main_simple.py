from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from api.v1.prioritization import router as prioritization_router
from api.v1.health import router as health_router
from api.v1.config import router as config_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S.%f'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PrioritiAI Engine",
    description="Intelligent task prioritization service using advanced AI analysis",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(prioritization_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")

# Legacy endpoint for n8n compatibility
@app.post("/classify")
async def classify_legacy(task_data: dict):
    """Legacy endpoint for backward compatibility with n8n workflow"""
    from api.v1.prioritization import prioritize_task_sync
    from models import TaskRequest, TaskCategory, UserRole
    
    # Convert legacy format to new TaskRequest format
    try:
        # Map legacy fields to new format
        task_request = TaskRequest(
            id=f"task_{datetime.now().timestamp()}",
            title=task_data.get("subject", "Untitled Task"),
            description=task_data.get("body", ""),
            category=TaskCategory.SUPPORT,  # Default category
            requester_role=UserRole.EMPLOYEE,  # Default role
            requester_name=task_data.get("sender", "Unknown"),
            estimated_effort_hours=task_data.get("est_minutes", 30) / 60 if task_data.get("est_minutes") else None
        )
        
        # Get AI priority result
        result = await prioritize_task_sync(task_request)
        
        # Convert back to legacy format for n8n compatibility
        return {
            "title": result.request_id,
            "description": task_request.description,
            "due_at": task_data.get("due_text"),
            "value_score": int(result.priority_metrics.business_impact_score),
            "risk_score": int(result.priority_metrics.risk_score),
            "role_score": int(result.priority_metrics.role_weight * 2),  # Scale to 0-10
            "haste_score": int(result.priority_metrics.time_sensitivity_score),
            "ai_score": int(result.priority_metrics.final_priority_score * 10),  # Scale to 0-100
            "ai_reason": result.reasoning
        }
    except Exception as e:
        logger.error(f"Error in legacy classify endpoint: {e}")
        # Fallback to simple scoring
        return {
            "title": task_data.get("subject", "Untitled Task"),
            "description": task_data.get("body", ""),
            "due_at": task_data.get("due_text"),
            "value_score": 5,
            "risk_score": 5,
            "role_score": 5,
            "haste_score": 5,
            "ai_score": 50,
            "ai_reason": "Fallback scoring due to processing error"
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PrioritiAI Engine",
        "version": "2.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PrioritiAI Engine",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "classify": "/classify (legacy n8n compatibility)",
            "prioritize": "/api/v1/prioritization/sync",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)