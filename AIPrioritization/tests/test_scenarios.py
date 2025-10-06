"""Enhanced test scenarios for the AI Priority Engine with comprehensive metrics"""

import asyncio
import json
import redis.asyncio as redis
from datetime import datetime, timedelta
from models import TaskRequest, TaskCategory, UserRole
from services.ai_service import get_ai_priority

async def test_enhanced_prioritization_scenarios():
    """Test various prioritization scenarios with enhanced AI models"""
    
    redis_client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    
    # Test Case 1: Critical CFO PowerPoint issue (Meeting imminent)
    cfo_powerpoint_task = TaskRequest(
        id="task_001",
        title="CFO cannot open PowerPoint presentation",
        description="CFO has important board meeting in 45 minutes and cannot open the critical financial presentation file. File appears corrupted or incompatible.",
        category=TaskCategory.MEETING_PREP,
        requester_role=UserRole.CFO,
        requester_name="John Smith",
        meeting_time=datetime.now() + timedelta(minutes=45),
        context="Critical board meeting presentation, financial quarterly results",
        tags=["urgent", "executive", "presentation", "board-meeting"]
    )
    
    # Test Case 2: Infrastructure failure affecting multiple users
    webshop_failure_task = TaskRequest(
        id="task_002", 
        title="E-commerce platform and reporting system failure",
        description="Complete failure of webshop ordering system and PowerBI reporting dashboard affecting customer orders and business analytics",
        category=TaskCategory.INFRASTRUCTURE,
        requester_role=UserRole.MANAGER,
        requester_name="Sarah Johnson",
        deadline=datetime.now() + timedelta(hours=6),
        context="Peak shopping hours, potential revenue loss of $50K/hour",
        tags=["infrastructure", "revenue-impact", "customer-facing"]
    )
    
    # Test Case 3: CEO document synchronization (High-level user, moderate urgency)
    ceo_sync_task = TaskRequest(
        id="task_003",
        title="CEO document synchronization failure",
        description="CEO cannot sync important strategic documents across devices, affecting mobile productivity and access to confidential materials",
        category=TaskCategory.SUPPORT,
        requester_role=UserRole.CEO,
        requester_name="Michael Brown",
        context="Strategic planning documents, confidential materials",
        tags=["executive", "mobile", "confidential"]
    )
    
    # Test Case 4: Security incident (Highest risk category)
    security_incident_task = TaskRequest(
        id="task_004",
        title="Employee clicked phishing link - potential breach",
        description="Employee clicked suspicious phishing link on Friday evening. Potential security breach with possible credential compromise and malware installation",
        category=TaskCategory.SECURITY,
        requester_role=UserRole.IT_ADMIN,
        requester_name="Alice Cooper",
        context="After hours incident, potential network compromise, credential theft risk",
        tags=["security", "phishing", "after-hours", "breach"]
    )
    
    # Test Case 5: Developer environment issue (Lower priority)
    dev_environment_task = TaskRequest(
        id="task_005",
        title="Development environment build failure",
        description="Local development environment failing to build, blocking development work on non-critical features",
        category=TaskCategory.DEVELOPMENT,
        requester_role=UserRole.DEVELOPER,
        requester_name="Bob Wilson",
        deadline=datetime.now() + timedelta(days=2),
        context="Non-critical feature development, alternative environment available",
        tags=["development", "non-critical", "local-environment"]
    )
    
    # Test all scenarios
    tasks = [
        cfo_powerpoint_task, 
        webshop_failure_task, 
        ceo_sync_task, 
        security_incident_task,
        dev_environment_task
    ]
    
    print("🧠 Testing Enhanced AI Prioritization Engine")
    print("=" * 60)
    
    for task in tasks:
        print(f"\n📋 Processing: {task.title}")
        print(f"   Category: {task.category.value}")
        print(f"   Requester: {task.requester_role.value}")
        
        try:
            # Get AI prioritization result
            result = await get_ai_priority(task)
            
            print(f"\n🎯 AI Assessment Results:")
            print(f"   Final Priority Score: {result.priority_metrics.final_priority_score:.1f}/10")
            print(f"   Urgency Level: {result.urgency_level.value}")
            print(f"   Suggested SLA: {result.suggested_sla_hours:.1f} hours")
            print(f"   Escalation Recommended: {'Yes' if result.escalation_recommended else 'No'}")
            print(f"   AI Confidence: {result.ai_confidence:.1%}")
            
            print(f"\n📊 Detailed Metrics:")
            print(f"   - Time Sensitivity: {result.priority_metrics.time_sensitivity_score:.1f}/10")
            print(f"   - Business Impact: {result.priority_metrics.business_impact_score:.1f}/10")
            print(f"   - Risk Score: {result.priority_metrics.risk_score:.1f}/10")
            print(f"   - Role Weight: {result.priority_metrics.role_weight:.1f}/5")
            
            if result.user_suggestions:
                print(f"\n💡 User Suggestions ({len(result.user_suggestions)}):")
                for i, suggestion in enumerate(result.user_suggestions[:3], 1):
                    print(f"   {i}. {suggestion.title}")
                    print(f"      ├─ {suggestion.description}")
                    print(f"      ├─ Category: {suggestion.category}")
                    print(f"      └─ Est. Time: {suggestion.estimated_resolution_time}")
            
            print(f"\n🎯 Next Actions:")
            for action in result.next_actions:
                print(f"   • {action}")
            
            # Send to Redis for async processing demonstration
            await redis_client.publish("prioritize_events", task.model_dump_json())
            
        except Exception as e:
            print(f"❌ Error processing task {task.id}: {e}")
        
        print("-" * 60)
    
    await redis_client.close()
    print("\n✅ All test scenarios completed!")

async def test_api_endpoints():
    """Test the API endpoints"""
    import aiohttp
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        try:
            async with session.get("http://localhost:8000/api/v1/health") as response:
                health_data = await response.json()
                print(f"✅ Health Check: {health_data['status']}")
                print(f"   Services: {health_data.get('services', {})}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test metrics endpoints
        try:
            async with session.get("http://localhost:8000/api/v1/metrics/categories") as response:
                categories_data = await response.json()
                print(f"✅ Categories: {len(categories_data['categories'])} available")
                
            async with session.get("http://localhost:8000/api/v1/metrics/roles") as response:
                roles_data = await response.json()
                print(f"✅ Roles: {len(roles_data['roles'])} configured")
        except Exception as e:
            print(f"❌ Metrics endpoints failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Prioritization Engine Tests")
    asyncio.run(test_enhanced_prioritization_scenarios())
    print("\n🌐 Testing API endpoints (requires running server)...")
    # asyncio.run(test_api_endpoints())  # Uncomment when server is running
