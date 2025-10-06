from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CEO = "CEO"
    CFO = "CFO"
    CTO = "CTO"
    MANAGER = "MANAGER"
    DEVELOPER = "DEVELOPER"
    IT_ADMIN = "IT_ADMIN"
    CLIENT = "CLIENT"
    EMPLOYEE = "EMPLOYEE"

class TaskCategory(str, Enum):
    MEETING_PREP = "MEETING_PREP"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    SECURITY = "SECURITY"
    SUPPORT = "SUPPORT"
    DEVELOPMENT = "DEVELOPMENT"
    MAINTENANCE = "MAINTENANCE"
    TRAINING = "TRAINING"
    COMPLIANCE = "COMPLIANCE"

class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TaskRequest(BaseModel):
    id: str
    title: str
    description: str
    category: TaskCategory
    requester_role: UserRole
    requester_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    meeting_time: Optional[datetime] = None
    business_value: Optional[int] = Field(default=None, ge=1, le=10)  # Will be calculated dynamically
    risk_level: Optional[int] = Field(default=None, ge=1, le=10)  # Will be calculated dynamically
    estimated_effort_hours: Optional[float] = Field(default=None, gt=0.0, le=1000.0)  # Will be calculated dynamically (allows minutes: 0.05 hours = 3 min)
    workaround_available: Optional[bool] = None  # Will be calculated dynamically
    affected_users_count: Optional[int] = Field(default=None, ge=1)  # Will be calculated dynamically
    context: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class PriorityMetrics(BaseModel):
    urgency_score: float = Field(..., ge=0.0, le=10.0)
    business_impact_score: float = Field(..., ge=0.0, le=10.0)
    risk_score: float = Field(..., ge=0.0, le=10.0)
    role_weight: float = Field(..., ge=0.0, le=5.0)
    time_sensitivity_score: float = Field(..., ge=0.0, le=10.0)
    effort_complexity_score: float = Field(..., ge=0.0, le=10.0)
    final_priority_score: float = Field(..., ge=0.0, le=10.0)

class UserSuggestion(BaseModel):
    title: str
    description: str
    category: str  # "self_help", "workaround", "escalation", "prevention"
    estimated_resolution_time: Optional[str] = None
    confidence_level: float = Field(..., ge=0.0, le=1.0)

class AIPriorityResult(BaseModel):
    request_id: str
    urgency_level: UrgencyLevel
    priority_metrics: PriorityMetrics
    reasoning: str
    ai_confidence: float = Field(..., ge=0.0, le=1.0)
    suggested_sla_hours: float
    user_suggestions: List[UserSuggestion] = Field(default_factory=list)
    escalation_recommended: bool = False
    workaround_suggestions: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    risk_assessment: str
    processed_at: datetime = Field(default_factory=datetime.now)

class PrioritizationRequest(BaseModel):
    request_id: str
    description: str
    user_role: str
    context: Optional[str] = None

class HealthCheck(BaseModel):
    status: str = "OK"
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict)
