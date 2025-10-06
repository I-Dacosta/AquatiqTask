import openai
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict
from core.config import settings
from models import (
    TaskRequest, AIPriorityResult, PriorityMetrics, UserSuggestion, 
    UrgencyLevel, UserRole, TaskCategory
)
from services.local_ai_analyzer import local_ai
from services.privacy_service import privacy_service

# Initialize OpenAI client (v1.0+ API)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class AIModel:
    def __init__(self):
        # Role weights for priority calculation
        self.role_weights = {
            UserRole.CEO: 5.0,
            UserRole.CFO: 4.5,
            UserRole.CTO: 4.5,
            UserRole.MANAGER: 3.5,
            UserRole.IT_ADMIN: 3.0,
            UserRole.DEVELOPER: 2.5,
            UserRole.EMPLOYEE: 2.0,
            UserRole.CLIENT: 2.5
        }
        
        # Category urgency multipliers
        self.category_urgency = {
            TaskCategory.SECURITY: 1.5,
            TaskCategory.INFRASTRUCTURE: 1.3,
            TaskCategory.MEETING_PREP: 1.2,
            TaskCategory.SUPPORT: 1.0,
            TaskCategory.DEVELOPMENT: 0.8,
            TaskCategory.MAINTENANCE: 0.7,
            TaskCategory.TRAINING: 0.6,
            TaskCategory.COMPLIANCE: 0.9
        }

    def calculate_time_sensitivity(self, task: TaskRequest) -> float:
        """Calculate time sensitivity score based on deadlines and meeting times"""
        now = datetime.now()
        
        # Check for meeting time
        if task.meeting_time:
            time_diff = (task.meeting_time - now).total_seconds() / 3600  # hours
            if time_diff <= 1:  # Less than 1 hour
                return 10.0
            elif time_diff <= 4:  # Less than 4 hours
                return 8.0
            elif time_diff <= 24:  # Less than 24 hours
                return 6.0
            else:
                return 4.0
        
        # Check for deadline
        if task.deadline:
            time_diff = (task.deadline - now).total_seconds() / 3600  # hours
            if time_diff <= 2:  # Less than 2 hours
                return 9.0
            elif time_diff <= 8:  # Less than 8 hours
                return 7.0
            elif time_diff <= 48:  # Less than 48 hours
                return 5.0
            else:
                return 3.0
        
        return 2.0  # No specific time constraint

    def calculate_priority_metrics(self, task: TaskRequest) -> PriorityMetrics:
        """Calculate comprehensive priority metrics"""
        
        # Time sensitivity
        time_sensitivity_score = self.calculate_time_sensitivity(task)
        
        # Role weight
        role_weight = self.role_weights.get(task.requester_role, 2.0)
        
        # Business impact (considering affected users and business value)
        business_impact_score = min(10.0, task.business_value + math.log10(task.affected_users_count))
        
        # Risk score (direct from task + category multiplier)
        risk_score = min(10.0, task.risk_level * self.category_urgency.get(task.category, 1.0))
        
        # Urgency score (combination of time sensitivity and risk)
        urgency_score = min(10.0, (time_sensitivity_score * 0.6) + (risk_score * 0.4))
        
        # Effort complexity (inverse relationship - higher effort = lower immediate priority)
        effort_complexity_score = max(1.0, 10.0 - (task.estimated_effort_hours * 0.5))
        
        # Final priority calculation with weighted average
        weights = {
            'urgency': 0.3,
            'business_impact': 0.25,
            'risk': 0.2,
            'role_weight': 0.15,
            'time_sensitivity': 0.1
        }
        
        final_priority_score = (
            urgency_score * weights['urgency'] +
            business_impact_score * weights['business_impact'] +
            risk_score * weights['risk'] +
            role_weight * weights['role_weight'] +
            time_sensitivity_score * weights['time_sensitivity']
        )
        
        return PriorityMetrics(
            urgency_score=urgency_score,
            business_impact_score=business_impact_score,
            risk_score=risk_score,
            role_weight=role_weight,
            time_sensitivity_score=time_sensitivity_score,
            effort_complexity_score=effort_complexity_score,
            final_priority_score=min(10.0, final_priority_score)
        )

    def determine_urgency_level(self, priority_score: float) -> UrgencyLevel:
        """Determine urgency level based on priority score"""
        if priority_score >= 8.0:
            return UrgencyLevel.CRITICAL
        elif priority_score >= 6.0:
            return UrgencyLevel.HIGH
        elif priority_score >= 3.0:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    def calculate_sla_hours(self, urgency_level: UrgencyLevel, category: TaskCategory) -> float:
        """Calculate suggested SLA hours based on urgency and category"""
        base_sla = {
            UrgencyLevel.CRITICAL: 1.0,
            UrgencyLevel.HIGH: 4.0,
            UrgencyLevel.MEDIUM: 24.0,
            UrgencyLevel.LOW: 72.0
        }
        
        category_multiplier = {
            TaskCategory.SECURITY: 0.5,
            TaskCategory.INFRASTRUCTURE: 0.7,
            TaskCategory.MEETING_PREP: 0.3,
            TaskCategory.SUPPORT: 1.0,
            TaskCategory.DEVELOPMENT: 1.5,
            TaskCategory.MAINTENANCE: 2.0,
            TaskCategory.TRAINING: 3.0,
            TaskCategory.COMPLIANCE: 1.2
        }
        
        return base_sla[urgency_level] * category_multiplier.get(category, 1.0)

    async def generate_ai_suggestions(self, task: TaskRequest) -> List[UserSuggestion]:
        """Generate AI-powered user suggestions (only if not sensitive data)"""
        try:
            prompt = f"""
            Analyze this IT support request and provide specific, actionable suggestions for the user:
            
            Title: {task.title}
            Description: {task.description}
            User Role: {task.requester_role}
            Category: {task.category}
            
            Provide 3-5 suggestions in JSON format with this structure:
            [
                {{
                    "title": "Quick suggestion title",
                    "description": "Detailed step-by-step instructions",
                    "category": "self_help|workaround|escalation|prevention",
                    "estimated_resolution_time": "5 minutes|30 minutes|1 hour|etc",
                    "confidence_level": 0.8
                }}
            ]
            
            Focus on practical, immediate solutions the user can try themselves first.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert IT support specialist providing practical, actionable solutions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            if content:
                suggestions_data = json.loads(content)
                return [UserSuggestion(**suggestion) for suggestion in suggestions_data]
            else:
                return self._get_fallback_suggestions(task)
            
        except Exception as e:
            print(f"Error generating AI suggestions: {e}")
            # Fallback suggestions based on category
            return self._get_fallback_suggestions(task)

    def _get_fallback_suggestions(self, task: TaskRequest) -> List[UserSuggestion]:
        """Provide fallback suggestions when AI service fails"""
        common_suggestions = {
            TaskCategory.SUPPORT: [
                UserSuggestion(
                    title="Restart the application",
                    description="Close the application completely and reopen it",
                    category="self_help",
                    estimated_resolution_time="2 minutes",
                    confidence_level=0.7
                ),
                UserSuggestion(
                    title="Check network connection",
                    description="Verify your internet connection is stable",
                    category="self_help",
                    estimated_resolution_time="1 minute",
                    confidence_level=0.6
                )
            ],
            TaskCategory.SECURITY: [
                UserSuggestion(
                    title="Change passwords immediately",
                    description="Update all related account passwords",
                    category="escalation",
                    estimated_resolution_time="10 minutes",
                    confidence_level=0.9
                ),
                UserSuggestion(
                    title="Disconnect from network",
                    description="Temporarily disconnect the affected device from network",
                    category="workaround",
                    estimated_resolution_time="1 minute",
                    confidence_level=0.8
                )
            ]
        }
        
        return common_suggestions.get(task.category, [])

    async def generate_risk_assessment(self, task: TaskRequest, metrics: PriorityMetrics) -> str:
        """Generate AI-powered risk assessment (only if not sensitive data)"""
        try:
            prompt = f"""
            Provide a brief risk assessment for this IT issue:
            
            Title: {task.title}
            Description: {task.description}
            Risk Level: {task.risk_level}/10
            Business Value: {task.business_value}/10
            Affected Users: {task.affected_users_count}
            Category: {task.category}
            
            Provide a 2-3 sentence risk assessment focusing on potential business impact and recommended mitigation approach.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a risk assessment specialist for IT operations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "Unable to generate risk assessment."
            
        except Exception as e:
            print(f"Error generating risk assessment: {e}")
            if metrics.risk_score >= 8:
                return "High risk situation requiring immediate attention to prevent business disruption."
            elif metrics.risk_score >= 5:
                return "Moderate risk that should be addressed promptly to avoid escalation."
            else:
                return "Low risk issue that can be handled through standard support channels."

ai_model = AIModel()

async def get_ai_priority(task: TaskRequest) -> AIPriorityResult:
    """
    Main function to get AI-powered priority assessment
    GDPR-compliant with automatic sensitive data detection
    """
    try:
        # First, analyze the task with local AI to get dynamic metrics
        full_text = f"{task.title} {task.description} {task.context or ''} {' '.join(task.tags)}"
        local_analysis = local_ai.analyze_task_metrics(
            task.title, 
            task.description, 
            task.requester_role, 
            task.category, 
            task.tags, 
            task.context or ""
        )
        
        # Check for sensitive data
        if local_analysis['is_sensitive']:
            # Log the detection for audit purposes
            privacy_service.log_sensitive_data_detection(task.id, local_analysis['sensitive_reasons'])
            
            # Route to manual processing (GDPR compliant)
            return privacy_service.create_manual_priority_result(task, local_analysis)
        
        # Update task with dynamically calculated metrics
        task.business_value = local_analysis['business_value']
        task.risk_level = local_analysis['risk_level'] 
        task.estimated_effort_hours = local_analysis['estimated_effort_hours']
        task.workaround_available = local_analysis['workaround_available']
        task.affected_users_count = local_analysis['affected_users_count']
        
        print(f"📊 Dynamic metrics calculated for task {task.id}:")
        print(f"   Business Value: {task.business_value}/10")
        print(f"   Risk Level: {task.risk_level}/10") 
        print(f"   Effort Hours: {task.estimated_effort_hours}")
        print(f"   Affected Users: {task.affected_users_count}")
        print(f"   Workaround Available: {task.workaround_available}")
        print(f"   Analysis Confidence: {local_analysis['confidence_score']:.1%}")
        
        # Calculate priority metrics
        metrics = ai_model.calculate_priority_metrics(task)
        
        # Determine urgency level
        urgency_level = ai_model.determine_urgency_level(metrics.final_priority_score)
        
        # Calculate SLA
        suggested_sla = ai_model.calculate_sla_hours(urgency_level, task.category)
        
        # Generate AI suggestions (safe, no sensitive data)
        user_suggestions = await ai_model.generate_ai_suggestions(task)
        
        # Generate risk assessment (safe, no sensitive data)
        risk_assessment = await ai_model.generate_risk_assessment(task, metrics)
        
        # Generate reasoning
        reasoning = f"""
        Enhanced AI Analysis - Priority Score: {metrics.final_priority_score:.1f}/10
        
        Dynamic Metrics (Local Analysis):
        - Business Value: {task.business_value}/10 (calculated from content)
        - Risk Level: {task.risk_level}/10 (calculated from keywords/category)
        - Effort Estimate: {task.estimated_effort_hours}h (calculated from complexity)
        - Affected Users: {task.affected_users_count} (estimated from context)
        
        Priority Calculation:
        - Time Sensitivity: {metrics.time_sensitivity_score:.1f}/10
        - Business Impact: {metrics.business_impact_score:.1f}/10
        - Risk Score: {metrics.risk_score:.1f}/10
        - Requester Role Weight: {metrics.role_weight:.1f}/5
        
        Classification: {urgency_level.value} priority based on comprehensive analysis
        Analysis Confidence: {local_analysis['confidence_score']:.1%}
        """
        
        # Determine if escalation is recommended
        escalation_recommended = (
            metrics.final_priority_score >= 8.0 or 
            task.category == TaskCategory.SECURITY or
            task.requester_role in [UserRole.CEO, UserRole.CFO, UserRole.CTO]
        )
        
        # Generate next actions
        next_actions = []
        if escalation_recommended:
            next_actions.append("Escalate to senior IT staff immediately")
        if task.workaround_available:
            next_actions.append("Provide workaround solution to minimize impact")
        next_actions.append(f"Begin resolution within {suggested_sla:.1f} hours")
        
        return AIPriorityResult(
            request_id=task.id,
            urgency_level=urgency_level,
            priority_metrics=metrics,
            reasoning=reasoning.strip(),
            ai_confidence=min(0.95, 0.85 + local_analysis['confidence_score'] * 0.1),
            suggested_sla_hours=suggested_sla,
            user_suggestions=user_suggestions,
            escalation_recommended=escalation_recommended,
            workaround_suggestions=["Check system status page", "Try alternative access method"] if task.workaround_available else [],
            next_actions=next_actions,
            risk_assessment=risk_assessment
        )
        
    except Exception as e:
        print(f"Error in AI priority calculation: {e}")
        # Return a safe default result
        return AIPriorityResult(
            request_id=task.id,
            urgency_level=UrgencyLevel.MEDIUM,
            priority_metrics=PriorityMetrics(
                urgency_score=5.0,
                business_impact_score=5.0,
                risk_score=5.0,
                role_weight=2.0,
                time_sensitivity_score=5.0,
                effort_complexity_score=5.0,
                final_priority_score=5.0
            ),
            reasoning="Error in AI processing, using default priority assessment.",
            ai_confidence=0.1,
            suggested_sla_hours=24.0,
            user_suggestions=[],
            escalation_recommended=False,
            workaround_suggestions=[],
            next_actions=["Standard support process"],
            risk_assessment="Unable to assess risk due to processing error."
        )
