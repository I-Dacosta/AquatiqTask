"""
Local AI analyzer for metrics calculation and sensitive data detection
GDPR-compliant - no data leaves the system
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from models import TaskCategory, UserRole

class LocalAIAnalyzer:
    def __init__(self):
        # Keywords for business value assessment
        self.high_business_value_keywords = [
            'revenue', 'customer', 'client', 'sales', 'order', 'payment', 'billing',
            'production', 'critical', 'essential', 'business', 'ceo', 'cfo', 'board',
            'meeting', 'presentation', 'financial', 'quarterly', 'annual', 'report'
        ]
        
        self.medium_business_value_keywords = [
            'manager', 'team', 'project', 'deadline', 'important', 'urgent',
            'workflow', 'process', 'efficiency', 'productivity'
        ]
        
        # Keywords for risk level assessment
        self.high_risk_keywords = [
            'security', 'breach', 'hack', 'virus', 'malware', 'phishing', 'attack',
            'data', 'database', 'server', 'network', 'infrastructure', 'system',
            'failure', 'down', 'crash', 'corruption', 'loss', 'deleted'
        ]
        
        self.medium_risk_keywords = [
            'error', 'bug', 'issue', 'problem', 'broken', 'not working',
            'slow', 'performance', 'timeout', 'connection'
        ]
        
        # Keywords for effort estimation
        self.high_effort_keywords = [
            'complete', 'total', 'entire', 'rebuild', 'reinstall', 'migration',
            'upgrade', 'implementation', 'development', 'complex', 'multiple'
        ]
        
        self.low_effort_keywords = [
            'quick', 'simple', 'restart', 'reset', 'toggle', 'enable', 'disable',
            'click', 'check', 'verify', 'password', 'login', 'access'
        ]
        
        # Sensitive data patterns (GDPR compliance)
        self.sensitive_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP Address
            r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',  # IBAN
            r'password[\s:=]+\S+',  # Password mentions
            r'key[\s:=]+\S+',  # API keys
        ]
        
        self.sensitive_keywords = [
            'personal', 'private', 'confidential', 'secret', 'classified',
            'gdpr', 'privacy', 'sensitive', 'restricted', 'internal only',
            'salary', 'wage', 'medical', 'health', 'social security',
            'passport', 'driver license', 'national id'
        ]

    def contains_sensitive_data(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if text contains sensitive data that should not be sent to third parties
        Returns: (is_sensitive, reasons)
        """
        reasons = []
        text_lower = text.lower()
        
        # Check for sensitive patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                reasons.append(f"Contains pattern: {pattern[:20]}...")
        
        # Check for sensitive keywords
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                reasons.append(f"Contains keyword: {keyword}")
        
        return len(reasons) > 0, reasons

    def calculate_business_value(self, title: str, description: str, 
                               requester_role: UserRole, category: TaskCategory,
                               tags: List[str]) -> int:
        """Calculate business value score 1-10"""
        score = 5  # Base score
        
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Role-based adjustment
        role_adjustments = {
            UserRole.CEO: +3,
            UserRole.CFO: +3,
            UserRole.CTO: +3,
            UserRole.MANAGER: +2,
            UserRole.CLIENT: +2,
            UserRole.IT_ADMIN: +1,
            UserRole.DEVELOPER: 0,
            UserRole.EMPLOYEE: 0
        }
        score += role_adjustments.get(requester_role, 0)
        
        # Category-based adjustment
        category_adjustments = {
            TaskCategory.INFRASTRUCTURE: +2,
            TaskCategory.SECURITY: +2,
            TaskCategory.MEETING_PREP: +2,
            TaskCategory.SUPPORT: +1,
            TaskCategory.COMPLIANCE: +1,
            TaskCategory.DEVELOPMENT: 0,
            TaskCategory.MAINTENANCE: -1,
            TaskCategory.TRAINING: -1
        }
        score += category_adjustments.get(category, 0)
        
        # Keyword-based adjustment
        high_value_matches = sum(1 for keyword in self.high_business_value_keywords if keyword in text)
        medium_value_matches = sum(1 for keyword in self.medium_business_value_keywords if keyword in text)
        
        score += min(high_value_matches * 1.5, 3)  # Max +3 from high value keywords
        score += min(medium_value_matches * 0.5, 2)  # Max +2 from medium value keywords
        
        # Time-sensitive tags
        urgent_tags = ['urgent', 'critical', 'asap', 'emergency', 'immediate']
        if any(tag.lower() in urgent_tags for tag in tags):
            score += 2
        
        return max(1, min(10, int(score)))

    def calculate_risk_level(self, title: str, description: str, 
                           category: TaskCategory, tags: List[str]) -> int:
        """Calculate risk level score 1-10"""
        score = 3  # Base score
        
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Category-based risk
        category_risks = {
            TaskCategory.SECURITY: +4,
            TaskCategory.INFRASTRUCTURE: +3,
            TaskCategory.COMPLIANCE: +2,
            TaskCategory.SUPPORT: +1,
            TaskCategory.MEETING_PREP: +1,
            TaskCategory.DEVELOPMENT: 0,
            TaskCategory.MAINTENANCE: 0,
            TaskCategory.TRAINING: -1
        }
        score += category_risks.get(category, 0)
        
        # Keyword-based risk assessment
        high_risk_matches = sum(1 for keyword in self.high_risk_keywords if keyword in text)
        medium_risk_matches = sum(1 for keyword in self.medium_risk_keywords if keyword in text)
        
        score += min(high_risk_matches * 2, 5)  # Max +5 from high risk keywords
        score += min(medium_risk_matches * 1, 3)  # Max +3 from medium risk keywords
        
        # High-risk tags
        risk_tags = ['security', 'breach', 'down', 'failure', 'critical', 'emergency']
        if any(tag.lower() in risk_tags for tag in tags):
            score += 2
        
        return max(1, min(10, int(score)))

    def estimate_effort_hours(self, title: str, description: str, 
                            category: TaskCategory, tags: List[str]) -> float:
        """Estimate effort in hours based on content analysis"""
        base_hours = 2.0  # Default 2 hours
        
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Category-based effort estimates
        category_efforts = {
            TaskCategory.SECURITY: 3.0,
            TaskCategory.INFRASTRUCTURE: 4.0,
            TaskCategory.DEVELOPMENT: 6.0,
            TaskCategory.COMPLIANCE: 2.0,
            TaskCategory.MEETING_PREP: 0.5,
            TaskCategory.SUPPORT: 1.0,
            TaskCategory.MAINTENANCE: 3.0,
            TaskCategory.TRAINING: 1.5
        }
        base_hours = category_efforts.get(category, base_hours)
        
        # Keyword-based effort adjustment
        high_effort_matches = sum(1 for keyword in self.high_effort_keywords if keyword in text)
        low_effort_matches = sum(1 for keyword in self.low_effort_keywords if keyword in text)
        
        if high_effort_matches > 0:
            base_hours *= (1 + high_effort_matches * 0.5)  # Increase effort
        
        if low_effort_matches > 0:
            base_hours *= max(0.3, 1 - low_effort_matches * 0.2)  # Decrease effort
        
        # Complexity indicators
        complexity_keywords = ['multiple', 'several', 'many', 'all', 'entire', 'complete']
        complexity_matches = sum(1 for keyword in complexity_keywords if keyword in text)
        base_hours *= (1 + complexity_matches * 0.3)
        
        return round(max(0.1, min(20.0, base_hours)), 1)

    def detect_workaround_availability(self, title: str, description: str, 
                                     category: TaskCategory) -> bool:
        """Determine if workaround might be available"""
        text = f"{title} {description}".lower()
        
        # Categories that typically have workarounds
        workaround_categories = [
            TaskCategory.SUPPORT,
            TaskCategory.DEVELOPMENT,
            TaskCategory.MAINTENANCE
        ]
        
        # Keywords suggesting workarounds exist
        workaround_keywords = [
            'alternative', 'backup', 'temporary', 'manual', 'different',
            'another', 'other', 'instead', 'bypass', 'substitute'
        ]
        
        # Keywords suggesting no workarounds
        no_workaround_keywords = [
            'only', 'sole', 'single', 'critical', 'essential', 'required',
            'mandatory', 'must', 'need', 'broken', 'corrupted', 'deleted'
        ]
        
        workaround_mentions = sum(1 for keyword in workaround_keywords if keyword in text)
        blocking_mentions = sum(1 for keyword in no_workaround_keywords if keyword in text)
        
        if blocking_mentions > workaround_mentions:
            return False
        
        if category in workaround_categories:
            return True
        
        return workaround_mentions > 0

    def estimate_affected_users(self, title: str, description: str, 
                              requester_role: UserRole, category: TaskCategory,
                              tags: List[str]) -> int:
        """Estimate number of affected users"""
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Look for explicit numbers
        number_patterns = [
            r'(\d+)\s*users?',
            r'(\d+)\s*people',
            r'(\d+)\s*employees?',
            r'(\d+)\s*customers?',
            r'(\d+)\s*clients?'
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, text)
            if match:
                return min(1000, int(match.group(1)))
        
        # Keywords indicating scale
        scale_keywords = {
            'everyone': 100,
            'all': 50,
            'entire': 30,
            'whole': 30,
            'company': 100,
            'organization': 100,
            'department': 20,
            'team': 8,
            'group': 5,
            'multiple': 3,
            'several': 3,
            'many': 5
        }
        
        max_affected = 1
        for keyword, count in scale_keywords.items():
            if keyword in text:
                max_affected = max(max_affected, count)
        
        # Category-based estimates
        category_defaults = {
            TaskCategory.INFRASTRUCTURE: 50,
            TaskCategory.SECURITY: 25,
            TaskCategory.SUPPORT: 1,
            TaskCategory.MEETING_PREP: 1,
            TaskCategory.DEVELOPMENT: 3,
            TaskCategory.MAINTENANCE: 10,
            TaskCategory.TRAINING: 5,
            TaskCategory.COMPLIANCE: 15
        }
        
        return max(max_affected, category_defaults.get(category, 1))

    def analyze_task_metrics(self, title: str, description: str, 
                           requester_role: UserRole, category: TaskCategory,
                           tags: List[str] = None, context: str = None) -> Dict:
        """
        Main function to analyze and calculate all task metrics locally
        """
        if tags is None:
            tags = []
        
        full_text = f"{title} {description} {context or ''} {' '.join(tags)}"
        
        # Check for sensitive data first
        is_sensitive, sensitive_reasons = self.contains_sensitive_data(full_text)
        
        # Calculate metrics
        business_value = self.calculate_business_value(title, description, requester_role, category, tags)
        risk_level = self.calculate_risk_level(title, description, category, tags)
        estimated_effort_hours = self.estimate_effort_hours(title, description, category, tags)
        workaround_available = self.detect_workaround_availability(title, description, category)
        affected_users_count = self.estimate_affected_users(title, description, requester_role, category, tags)
        
        return {
            'business_value': business_value,
            'risk_level': risk_level,
            'estimated_effort_hours': estimated_effort_hours,
            'workaround_available': workaround_available,
            'affected_users_count': affected_users_count,
            'is_sensitive': is_sensitive,
            'sensitive_reasons': sensitive_reasons,
            'confidence_score': self._calculate_confidence(title, description, tags)
        }
    
    def _calculate_confidence(self, title: str, description: str, tags: List[str]) -> float:
        """Calculate confidence in the analysis based on available information"""
        score = 0.5  # Base confidence
        
        # More detailed description increases confidence
        if len(description) > 100:
            score += 0.2
        elif len(description) > 50:
            score += 0.1
        
        # Clear title increases confidence
        if len(title.split()) >= 3:
            score += 0.1
        
        # Tags provide additional context
        score += min(len(tags) * 0.05, 0.2)
        
        return round(min(1.0, score), 2)

# Global instance
local_ai = LocalAIAnalyzer()
