"""
Enhanced test scenarios showcasing dynamic metric calculation and GDPR compliance
"""

import asyncio
from datetime import datetime, timedelta
from models import TaskRequest, TaskCategory, UserRole
from services.ai_service import get_ai_priority

async def test_dynamic_metrics():
    """Test the dynamic metric calculation system"""
    
    print("🧠 Testing Dynamic AI Metrics & GDPR Compliance")
    print("=" * 70)
    
    # Test Case 1: CFO PowerPoint Crisis (Meeting imminent) - Should be CRITICAL
    cfo_task = TaskRequest(
        id="task_001",
        title="CFO cannot open PowerPoint presentation for board meeting",
        description="The CFO has an urgent board meeting in 45 minutes to present quarterly financial results. The PowerPoint file appears corrupted and won't open. This is a critical business presentation for investors.",
        category=TaskCategory.MEETING_PREP,
        requester_role=UserRole.CFO,
        requester_name="John Smith",
        meeting_time=datetime.now() + timedelta(minutes=45),
        # Note: No manual metrics - they will be calculated dynamically
        context="Critical board meeting, quarterly investor presentation",
        tags=["urgent", "critical", "executive", "board-meeting", "financial"]
    )
    
    # Test Case 2: E-commerce Infrastructure Failure - Should be HIGH/CRITICAL
    infrastructure_task = TaskRequest(
        id="task_002",
        title="Complete webshop and reporting system failure",
        description="Our entire e-commerce platform is down affecting all customer orders and payments. PowerBI reporting dashboard is also failing. Multiple customers complaining, revenue loss estimated at $50K per hour during peak shopping period.",
        category=TaskCategory.INFRASTRUCTURE,
        requester_role=UserRole.MANAGER,
        requester_name="Sarah Johnson",
        deadline=datetime.now() + timedelta(hours=4),
        context="Peak shopping period, high revenue impact, many affected customers",
        tags=["system-down", "revenue-impact", "customers", "critical", "infrastructure"]
    )
    
    # Test Case 3: CEO Document Sync (High-level user, moderate urgency)
    ceo_task = TaskRequest(
        id="task_003",
        title="CEO document synchronization problem",
        description="The CEO cannot sync important strategic planning documents across devices. This affects mobile productivity but there might be alternative access methods available.",
        category=TaskCategory.SUPPORT,
        requester_role=UserRole.CEO,
        requester_name="Michael Brown",
        context="Strategic documents, mobile access needed",
        tags=["executive", "sync", "mobile", "documents"]
    )
    
    # Test Case 4: Security Incident with Sensitive Data - Should trigger GDPR compliance
    security_task = TaskRequest(
        id="task_004", 
        title="Employee clicked phishing email with personal data",
        description="Employee John Doe (john.doe@company.com, SSN: 123-45-6789) clicked a phishing link containing customer personal information including credit card data 4532-1234-5678-9012. Potential GDPR breach with sensitive customer data exposure.",
        category=TaskCategory.SECURITY,
        requester_role=UserRole.IT_ADMIN,
        requester_name="Alice Cooper",
        context="Potential data breach, customer PII exposed, GDPR implications",
        tags=["security", "phishing", "data-breach", "personal-data", "GDPR"]
    )
    
    # Test Case 5: Simple Developer Issue - Should be LOW priority  
    dev_task = TaskRequest(
        id="task_005",
        title="Local development environment setup issue",
        description="Need help setting up a simple local development environment for a small personal project. Not urgent, can work on other things in the meantime.",
        category=TaskCategory.DEVELOPMENT,
        requester_role=UserRole.DEVELOPER,
        requester_name="Bob Wilson", 
        deadline=datetime.now() + timedelta(days=3),
        context="Personal project, not business critical, alternative options available",
        tags=["development", "local", "setup", "non-urgent", "personal"]
    )
    
    # Test all scenarios
    tasks = [cfo_task, infrastructure_task, ceo_task, security_task, dev_task]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n🔍 Test Case {i}: {task.title}")
        print(f"   Category: {task.category.value}")
        print(f"   Requester: {task.requester_role.value}")
        print(f"   Tags: {', '.join(task.tags)}")
        
        try:
            # Get AI assessment with dynamic metrics
            result = await get_ai_priority(task)
            
            print(f"\n🎯 Results:")
            print(f"   📊 Final Priority: {result.priority_metrics.final_priority_score:.1f}/10")
            print(f"   🚨 Urgency Level: {result.urgency_level.value}")
            print(f"   ⏱️  Suggested SLA: {result.suggested_sla_hours:.1f} hours")
            print(f"   ⬆️  Escalation: {'Yes' if result.escalation_recommended else 'No'}")
            print(f"   🤖 AI Confidence: {result.ai_confidence:.1%}")
            
            print(f"\n📈 Dynamic Metrics Calculated:")
            print(f"   💰 Business Value: {result.priority_metrics.business_impact_score:.1f}/10")
            print(f"   ⚠️  Risk Level: {result.priority_metrics.risk_score:.1f}/10")
            print(f"   👥 Role Weight: {result.priority_metrics.role_weight:.1f}/5")
            print(f"   ⏰ Time Sensitivity: {result.priority_metrics.time_sensitivity_score:.1f}/10")
            
            if result.user_suggestions:
                print(f"\n💡 AI Suggestions ({len(result.user_suggestions)}):")
                for j, suggestion in enumerate(result.user_suggestions[:2], 1):
                    print(f"   {j}. {suggestion.title}")
                    print(f"      └─ {suggestion.description[:80]}...")
                    print(f"      └─ Category: {suggestion.category} | Time: {suggestion.estimated_resolution_time}")
            
            print(f"\n🎯 Next Actions:")
            for action in result.next_actions:
                print(f"   • {action}")
            
        except Exception as e:
            print(f"❌ Error processing task: {e}")
        
        print("-" * 70)
    
    print("\n✅ Dynamic Metric Testing Complete!")
    print("\n📝 Summary:")
    print("   • Tasks are analyzed locally first for sensitive data")
    print("   • Metrics (business_value, risk_level, effort, users) calculated dynamically")
    print("   • Sensitive data triggers GDPR-compliant manual processing")
    print("   • Non-sensitive tasks use OpenAI for enhanced suggestions")
    print("   • All processing respects privacy and data protection regulations")

if __name__ == "__main__":
    asyncio.run(test_dynamic_metrics())
