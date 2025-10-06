#!/usr/bin/env python3
"""
Quick Test Script - AI Prioritization Engine
Tests basic functionality without Redis dependency
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import TaskRequest, UserRole, TaskCategory
from services.ai_service import get_ai_priority

async def test_ai_service():
    """Test AI service directly without Redis"""
    print("🧪 Testing AI Prioritization Service...")
    
    # Create a test task
    test_task = TaskRequest(
        id="TEST-001",
        title="Critical Database Connection Failure",
        description="Primary database server is unresponsive, affecting all customer-facing applications",
        category=TaskCategory.INFRASTRUCTURE,
        requester_role=UserRole.IT_ADMIN,
        requester_name="Database Admin",
        tags=["database", "critical", "outage"],
        deadline=datetime.now() + timedelta(hours=2),
        context="Production outage affecting 10,000+ users"
    )
    
    print(f"📋 Test Task: {test_task.title}")
    print(f"   Category: {test_task.category}")
    print(f"   Requester: {test_task.requester_role}")
    print(f"   Deadline: {test_task.deadline}")
    
    try:
        # Process with AI
        print("🤖 Processing with AI...")
        result = await get_ai_priority(test_task)
        
        print("✅ AI Processing Results:")
        print(f"   Priority Score: {result.priority_metrics.final_priority_score:.1f}/10")
        print(f"   Urgency Level: {result.urgency_level}")
        print(f"   SLA Hours: {result.suggested_sla_hours:.1f}")
        print(f"   Escalation Recommended: {result.escalation_recommended}")
        print(f"   AI Confidence: {result.ai_confidence:.1%}")
        print(f"   User Suggestions: {len(result.user_suggestions)}")
        
        if result.user_suggestions:
            print("   💡 Top Suggestion:", result.user_suggestions[0].title)
        
        print("\n✅ AI Service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False

def test_imports():
    """Test all critical imports"""
    print("📦 Testing imports...")
    
    try:
        from main import app
        print("   ✅ FastAPI app")
        
        from services.redis_service import redis_service
        print("   ✅ Redis service")
        
        from services.background_tasks import task_manager
        print("   ✅ Background tasks")
        
        from api.v1 import prioritization, health, config
        print("   ✅ API routers")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🎯 AI Prioritization Engine - Quick Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        return
    
    print("\n" + "-" * 50)
    
    # Test AI service
    if not await test_ai_service():
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The system is ready to run.")
    print("\n💡 Next steps:")
    print("   1. Start Redis: docker run -d -p 6379:6379 redis:latest")
    print("   2. Set OpenAI API key: export OPENAI_API_KEY='your-key'")
    print("   3. Start server: uvicorn main:app --reload")
    print("   4. Run demo: python scripts/enhanced_demo.py")

if __name__ == "__main__":
    asyncio.run(main())
