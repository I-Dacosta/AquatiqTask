"""
GDPR-compliant privacy service
Handles sensitive data detection and ensures compliance with data protection regulations
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from models import TaskRequest, AIPriorityResult, PriorityMetrics, UrgencyLevel, UserSuggestion
from services.local_ai_analyzer import local_ai

class PrivacyComplianceService:
    def __init__(self):
        self.sensitive_data_log = []
        
    def log_sensitive_data_detection(self, task_id: str, reasons: List[str]):
        """Log when sensitive data is detected for audit purposes"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'reasons': reasons,
            'action': 'routed_to_manual_processing'
        }
        self.sensitive_data_log.append(log_entry)
        print(f"🔒 GDPR COMPLIANCE: Task {task_id} contains sensitive data - routing to manual processing")
        
    def create_manual_priority_result(self, task: TaskRequest, metrics: Dict) -> AIPriorityResult:
        """
        Create a priority result for tasks with sensitive data without using external AI
        Uses local analysis only
        """
        # Calculate priority metrics using local AI only
        priority_metrics = PriorityMetrics(
            urgency_score=min(10.0, metrics['risk_level'] * 1.2),
            business_impact_score=float(metrics['business_value']),
            risk_score=float(metrics['risk_level']),
            role_weight=self._get_role_weight(task.requester_role),
            time_sensitivity_score=self._calculate_time_sensitivity_local(task),
            effort_complexity_score=max(1.0, 10.0 - metrics['estimated_effort_hours']),
            final_priority_score=self._calculate_final_priority_local(task, metrics)
        )
        
        urgency_level = self._determine_urgency_level_local(priority_metrics.final_priority_score)
        
        # Generate local suggestions without external AI
        user_suggestions = self._generate_local_suggestions(task, metrics)
        
        # Create GDPR-compliant result
        return AIPriorityResult(
            request_id=task.id,
            urgency_level=urgency_level,
            priority_metrics=priority_metrics,
            reasoning=self._generate_local_reasoning(task, metrics, priority_metrics),
            ai_confidence=0.75,  # Local analysis confidence
            suggested_sla_hours=self._calculate_sla_local(urgency_level, task.category),
            user_suggestions=user_suggestions,
            escalation_recommended=self._should_escalate_local(task, priority_metrics),
            workaround_suggestions=self._generate_workaround_suggestions_local(task),
            next_actions=self._generate_next_actions_local(task, priority_metrics),
            risk_assessment=self._generate_risk_assessment_local(task, metrics)
        )
    
    def _get_role_weight(self, role) -> float:
        """Get role weight for priority calculation"""
        from models import UserRole
        weights = {
            UserRole.CEO: 5.0,
            UserRole.CFO: 4.5,
            UserRole.CTO: 4.5,
            UserRole.MANAGER: 3.5,
            UserRole.IT_ADMIN: 3.0,
            UserRole.DEVELOPER: 2.5,
            UserRole.EMPLOYEE: 2.0,
            UserRole.CLIENT: 2.5
        }
        return weights.get(role, 2.0)
    
    def _calculate_time_sensitivity_local(self, task: TaskRequest) -> float:
        """Calculate time sensitivity without external AI"""
        if task.meeting_time:
            time_diff = (task.meeting_time - datetime.now()).total_seconds() / 3600
            if time_diff <= 1:
                return 10.0
            elif time_diff <= 4:
                return 8.0
            elif time_diff <= 24:
                return 6.0
            else:
                return 4.0
        
        if task.deadline:
            time_diff = (task.deadline - datetime.now()).total_seconds() / 3600
            if time_diff <= 2:
                return 9.0
            elif time_diff <= 8:
                return 7.0
            elif time_diff <= 48:
                return 5.0
            else:
                return 3.0
        
        return 2.0
    
    def _calculate_final_priority_local(self, task: TaskRequest, metrics: Dict) -> float:
        """Calculate final priority score using local analysis"""
        urgency = min(10.0, metrics['risk_level'] * 1.2)
        business_impact = float(metrics['business_value'])
        risk = float(metrics['risk_level'])
        role_weight = self._get_role_weight(task.requester_role)
        time_sensitivity = self._calculate_time_sensitivity_local(task)
        
        # Weighted calculation
        final_score = (
            urgency * 0.3 +
            business_impact * 0.25 +
            risk * 0.2 +
            role_weight * 0.15 +
            time_sensitivity * 0.1
        )
        
        return min(10.0, final_score)
    
    def _determine_urgency_level_local(self, priority_score: float) -> UrgencyLevel:
        """Determine urgency level based on priority score"""
        if priority_score >= 8.0:
            return UrgencyLevel.CRITICAL
        elif priority_score >= 6.0:
            return UrgencyLevel.HIGH
        elif priority_score >= 3.0:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW
    
    def _calculate_sla_local(self, urgency_level: UrgencyLevel, category) -> float:
        """Calculate SLA hours without external AI"""
        from models import TaskCategory
        
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
    
    def _generate_local_suggestions(self, task: TaskRequest, metrics: Dict) -> List[UserSuggestion]:
        """Generate user suggestions without external AI (GDPR compliant)"""
        suggestions = []
        
        # Category-based suggestions
        from models import TaskCategory
        
        if task.category == TaskCategory.SUPPORT:
            suggestions.extend([
                UserSuggestion(
                    title="Restart the application",
                    description="Close the application completely and restart it",
                    category="self_help",
                    estimated_resolution_time="2 minutes",
                    confidence_level=0.7
                ),
                UserSuggestion(
                    title="Check network connectivity",
                    description="Verify your internet connection is stable and working",
                    category="self_help",
                    estimated_resolution_time="1 minute",
                    confidence_level=0.6
                )
            ])
        
        elif task.category == TaskCategory.SECURITY:
            suggestions.extend([
                UserSuggestion(
                    title="Disconnect from network immediately",
                    description="Disconnect the affected device from network to prevent spread",
                    category="escalation",
                    estimated_resolution_time="30 seconds",
                    confidence_level=0.9
                ),
                UserSuggestion(
                    title="Document the incident",
                    description="Take screenshots and note exact times for security team",
                    category="prevention",
                    estimated_resolution_time="5 minutes",
                    confidence_level=0.8
                )
            ])
        
        elif task.category == TaskCategory.MEETING_PREP:
            suggestions.extend([
                UserSuggestion(
                    title="Try alternative presentation software",
                    description="Open the file with Google Slides, Apple Keynote, or LibreOffice",
                    category="workaround",
                    estimated_resolution_time="3 minutes",
                    confidence_level=0.8
                ),
                UserSuggestion(
                    title="Use backup device",
                    description="Try opening the presentation on a different computer",
                    category="workaround",
                    estimated_resolution_time="5 minutes",
                    confidence_level=0.7
                )
            ])
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _should_escalate_local(self, task: TaskRequest, metrics: PriorityMetrics) -> bool:
        """Determine if escalation is needed without external AI"""
        from models import UserRole, TaskCategory
        
        return (
            metrics.final_priority_score >= 8.0 or
            task.category == TaskCategory.SECURITY or
            task.requester_role in [UserRole.CEO, UserRole.CFO, UserRole.CTO] or
            metrics.risk_score >= 8.0
        )
    
    def _generate_workaround_suggestions_local(self, task: TaskRequest) -> List[str]:
        """Generate workaround suggestions without external AI"""
        suggestions = []
        
        if task.workaround_available:
            from models import TaskCategory
            
            category_workarounds = {
                TaskCategory.SUPPORT: [
                    "Try using a different browser or device",
                    "Clear browser cache and cookies",
                    "Use incognito/private browsing mode"
                ],
                TaskCategory.INFRASTRUCTURE: [
                    "Use backup systems if available",
                    "Implement manual processes temporarily",
                    "Redirect traffic to alternative servers"
                ],
                TaskCategory.MEETING_PREP: [
                    "Use alternative presentation software",
                    "Convert file to different format",
                    "Present from backup device"
                ]
            }
            
            suggestions = category_workarounds.get(task.category, [
                "Check system status page for known issues",
                "Try alternative access methods"
            ])
        
        return suggestions[:2]  # Limit to top 2 workarounds
    
    def _generate_next_actions_local(self, task: TaskRequest, metrics: PriorityMetrics) -> List[str]:
        """Generate next actions without external AI"""
        actions = []
        
        if self._should_escalate_local(task, metrics):
            actions.append("Escalate to senior IT staff immediately")
        
        if task.workaround_available:
            actions.append("Provide workaround solution to minimize impact")
        
        sla_hours = self._calculate_sla_local(
            self._determine_urgency_level_local(metrics.final_priority_score),
            task.category
        )
        actions.append(f"Begin resolution within {sla_hours:.1f} hours")
        
        if metrics.risk_score >= 7.0:
            actions.append("Monitor for additional impact or escalation")
        
        return actions
    
    def _generate_risk_assessment_local(self, task: TaskRequest, metrics: Dict) -> str:
        """Generate risk assessment without external AI"""
        risk_level = metrics['risk_level']
        
        if risk_level >= 8:
            return f"High risk situation requiring immediate attention. Risk level {risk_level}/10 indicates potential for significant business disruption."
        elif risk_level >= 5:
            return f"Moderate risk that should be addressed promptly. Risk level {risk_level}/10 suggests potential for escalation if not resolved."
        else:
            return f"Low to moderate risk issue. Risk level {risk_level}/10 can be handled through standard support channels."
    
    def _generate_local_reasoning(self, task: TaskRequest, metrics: Dict, priority_metrics: PriorityMetrics) -> str:
        """Generate reasoning without external AI"""
        return f"""
        GDPR-Compliant Local Analysis - Priority Score: {priority_metrics.final_priority_score:.1f}/10
        
        Key Factors (Local Analysis):
        - Time Sensitivity: {priority_metrics.time_sensitivity_score:.1f}/10
        - Business Impact: {priority_metrics.business_impact_score:.1f}/10  
        - Risk Level: {priority_metrics.risk_score:.1f}/10
        - Requester Role Weight: {priority_metrics.role_weight:.1f}/5
        - Confidence: {metrics.get('confidence_score', 0.75):.1%}
        
        Classification: {self._determine_urgency_level_local(priority_metrics.final_priority_score).value} priority
        
        Note: This task contained sensitive data and was processed locally without 
        external AI services to ensure GDPR compliance.
        """.strip()

# Global instance
privacy_service = PrivacyComplianceService()
