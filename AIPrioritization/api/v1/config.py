"""
Configuration and Metrics Endpoints
"""
from fastapi import APIRouter, Query
from typing import Dict, Any
from models import TaskCategory, UserRole
from core.config import settings

router = APIRouter(prefix="/config", tags=["Configuration & Metrics"])

@router.get(
    "/categories",
    summary="Get Task Categories Configuration",
    description="Retrieve all available task categories with their priority multipliers",
    responses={
        200: {
            "description": "Category configuration",
            "content": {
                "application/json": {
                    "example": {
                        "categories": ["SECURITY", "INFRASTRUCTURE", "MEETING_PREP"],
                        "urgency_multipliers": {
                            "SECURITY": 1.5,
                            "INFRASTRUCTURE": 1.3,
                            "MEETING_PREP": 1.2
                        },
                        "descriptions": {
                            "SECURITY": "Security incidents and threats",
                            "INFRASTRUCTURE": "System and infrastructure issues"
                        }
                    }
                }
            }
        }
    }
)
async def get_category_configuration():
    """
    Get comprehensive task category configuration including priority multipliers.
    
    **Category Types:**
    - **SECURITY**: Security incidents, breaches, threats (1.5× multiplier)
    - **INFRASTRUCTURE**: System outages, server issues (1.3× multiplier)  
    - **MEETING_PREP**: Presentation, meeting support (1.2× multiplier)
    - **SUPPORT**: General user support (1.0× baseline)
    - **DEVELOPMENT**: Development tasks (0.8× multiplier)
    - **MAINTENANCE**: Routine maintenance (0.7× multiplier)
    - **TRAINING**: Training and documentation (0.6× multiplier)
    - **COMPLIANCE**: Compliance and audit tasks (0.9× multiplier)
    """
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
        },
        "descriptions": {
            "SECURITY": "Security incidents, breaches, and threats requiring immediate attention",
            "INFRASTRUCTURE": "Critical system outages, server failures, and infrastructure issues",
            "MEETING_PREP": "Executive presentations, board meetings, and time-sensitive preparations",
            "SUPPORT": "General user support requests and help desk tickets",
            "DEVELOPMENT": "Software development tasks, bug fixes, and feature requests",
            "MAINTENANCE": "Routine system maintenance, updates, and preventive tasks",
            "TRAINING": "Training materials, documentation, and knowledge sharing",
            "COMPLIANCE": "Regulatory compliance, audit requirements, and policy enforcement"
        }
    }

@router.get(
    "/roles",
    summary="Get User Roles Configuration", 
    description="Retrieve user roles with their authority weights and access levels",
    responses={
        200: {
            "description": "Role configuration",
            "content": {
                "application/json": {
                    "example": {
                        "roles": ["CEO", "CFO", "CTO", "MANAGER"],
                        "priority_weights": {
                            "CEO": 5.0,
                            "CFO": 4.5,
                            "CTO": 4.5,
                            "MANAGER": 3.5
                        },
                        "access_levels": {
                            "CEO": "executive",
                            "CFO": "executive",
                            "MANAGER": "management"
                        }
                    }
                }
            }
        }
    }
)
async def get_role_configuration():
    """
    Get comprehensive user role configuration with authority weights.
    
    **Role Hierarchy (Priority Weight):**
    - **CEO**: 5.0 - Highest executive authority
    - **CFO/CTO**: 4.5 - C-level executives  
    - **MANAGER**: 3.5 - Management level
    - **IT_ADMIN**: 3.0 - Technical administration
    - **CLIENT**: 2.5 - External customers
    - **DEVELOPER**: 2.5 - Technical staff
    - **EMPLOYEE**: 2.0 - General workforce
    
    Higher weights result in faster SLA targets and escalation preferences.
    """
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
        },
        "access_levels": {
            "CEO": "executive",
            "CFO": "executive", 
            "CTO": "executive",
            "MANAGER": "management",
            "IT_ADMIN": "technical",
            "DEVELOPER": "technical",
            "EMPLOYEE": "standard",
            "CLIENT": "external"
        },
        "escalation_rules": {
            "executive": "immediate_escalation",
            "management": "escalate_if_high_priority", 
            "technical": "standard_escalation",
            "standard": "standard_escalation",
            "external": "customer_escalation_path"
        }
    }

@router.get(
    "/priority-model",
    summary="Get Priority Calculation Model",
    description="Detailed explanation of the AI priority calculation algorithm"
)
async def get_priority_model():
    """
    Get detailed information about the priority calculation model and weights.
    
    **Calculation Formula:**
    ```
    Final Priority Score = 
      (Urgency Score × 0.30) +
      (Business Impact × 0.25) +
      (Risk Score × 0.20) +
      (Role Weight × 0.15) +
      (Time Sensitivity × 0.10)
    ```
    """
    return {
        "model_version": "2.0",
        "calculation_weights": {
            "urgency_score": 0.30,
            "business_impact": 0.25,
            "risk_score": 0.20,
            "role_weight": 0.15,
            "time_sensitivity": 0.10
        },
        "score_ranges": {
            "CRITICAL": {"min": 8.5, "max": 10.0, "sla_hours": 1},
            "HIGH": {"min": 6.5, "max": 8.4, "sla_hours": 4},
            "MEDIUM": {"min": 4.0, "max": 6.4, "sla_hours": 24},
            "LOW": {"min": 0.0, "max": 3.9, "sla_hours": 72}
        },
        "auto_calculation_features": {
            "business_value": "Derived from task content, requester role, and impact keywords",
            "risk_level": "Security, system, and operational risk analysis",
            "effort_estimation": "Complexity analysis based on task description patterns",
            "affected_users": "Scale indicators and impact scope detection",
            "workaround_availability": "Alternative solution likelihood assessment"
        },
        "gdpr_compliance": {
            "sensitive_data_detection": True,
            "local_processing_fallback": True,
            "no_external_ai_for_pii": True
        }
    }

@router.get(
    "/thresholds",
    summary="Get System Thresholds Configuration",
    description="Current system thresholds and limits for prioritization"
)
async def get_system_thresholds():
    """
    Get current system thresholds and configuration limits.
    
    **Configurable Thresholds:**
    - Priority score boundaries
    - SLA time limits  
    - Escalation triggers
    - Performance limits
    """
    return {
        "priority_thresholds": {
            "critical": getattr(settings, 'CRITICAL_THRESHOLD', 8.5),
            "high": getattr(settings, 'HIGH_THRESHOLD', 6.5),
            "medium": getattr(settings, 'MEDIUM_THRESHOLD', 4.0),
            "escalation": getattr(settings, 'ESCALATION_THRESHOLD', 8.0)
        },
        "performance_limits": {
            "max_concurrent_requests": getattr(settings, 'MAX_CONCURRENT_REQUESTS', 10),
            "request_timeout_seconds": getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 30),
            "max_processing_time_seconds": 120
        },
        "ai_configuration": {
            "model": getattr(settings, 'AI_MODEL', 'gpt-3.5-turbo'),
            "temperature": getattr(settings, 'AI_TEMPERATURE', 0.3),
            "max_tokens": getattr(settings, 'AI_MAX_TOKENS', 800),
            "confidence_threshold": getattr(settings, 'AI_CONFIDENCE_THRESHOLD', 0.7)
        }
    }
