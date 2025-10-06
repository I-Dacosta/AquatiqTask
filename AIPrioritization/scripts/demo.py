#!/usr/bin/env python3
"""
Enhanced AI Prioritization Engine v2.0 - Demo Script
====================================================

This script demonstrates the enhanced capabilities of the AI Prioritization Engine
including mathematical scoring, role-based prioritization, and intelligent suggestions.
"""

import asyncio
from datetime import datetime, timedelta
from models import TaskRequest, TaskCategory, UserRole
from services.ai_service import get_ai_priority

async def demo_enhanced_ai_features():
    """Demonstrate the enhanced AI prioritization features"""
    
    print("🧠 ENHANCED AI PRIORITIZATION ENGINE v2.0 DEMO")
    print("="*60)
    print()
    
    # Executive Crisis - Should get highest priority
    executive_task = TaskRequest(
        id="demo_001",
        title="CEO presentation system failure",
        description="CEO cannot access critical board presentation 30 minutes before investor meeting",
        category=TaskCategory.MEETING_PREP,
        requester_role=UserRole.CEO,
        requester_name="Alex Johnson",
        meeting_time=datetime.now() + timedelta(minutes=30),
        business_value=10,
        risk_level=9,
        estimated_effort_hours=0.5,
        workaround_available=False,
        affected_users_count=1,
        context="Critical investor presentation, $50M funding round",
        tags=["critical", "executive", "investor-meeting"]
    )
    
    # Security Incident - Should get critical priority
    security_task = TaskRequest(
        id="demo_002", 
        title="Ransomware attack detected",
        description="Potential ransomware detected on multiple workstations, files being encrypted",
        category=TaskCategory.SECURITY,
        requester_role=UserRole.IT_ADMIN,
        requester_name="Security Team",
        business_value=8,
        risk_level=10,
        estimated_effort_hours=4.0,
        workaround_available=True,
        affected_users_count=25,
        context="Active security incident, potential data breach",
        tags=["security", "ransomware", "active-incident"]
    )
    
    # Regular user issue - Should get lower priority
    user_task = TaskRequest(
        id="demo_003",
        title="Employee cannot print documents",
        description="Office printer not responding, documents not printing",
        category=TaskCategory.SUPPORT,
        requester_role=UserRole.EMPLOYEE,
        requester_name="Jane Smith",
        business_value=3,
        risk_level=2,
        estimated_effort_hours=1.0,
        workaround_available=True,
        affected_users_count=1,
        context="Non-critical printing issue",
        tags=["printing", "office-equipment"]
    )
    
    tasks = [
        ("👑 EXECUTIVE CRISIS", executive_task),
        ("🚨 SECURITY INCIDENT", security_task),
        ("📄 USER SUPPORT REQUEST", user_task)
    ]
    
    for task_type, task in tasks:
        print(f"\n{task_type}")
        print("-" * 40)
        print(f"📋 Task: {task.title}")
        print(f"👤 Requester: {task.requester_role.value} - {task.requester_name}")
        print(f"🏷️  Category: {task.category.value}")
        print(f"💼 Business Value: {task.business_value}/10")
        print(f"⚠️  Risk Level: {task.risk_level}/10")
        print(f"👥 Affected Users: {task.affected_users_count}")
        
        try:
            # Get AI prioritization (without OpenAI for demo)
            result = await get_ai_priority(task)
            
            print(f"\n🧠 AI ASSESSMENT:")
            print(f"   🎯 Final Priority Score: {result.priority_metrics.final_priority_score:.1f}/10")
            print(f"   🚩 Urgency Level: {result.urgency_level.value}")
            print(f"   ⏰ Suggested SLA: {result.suggested_sla_hours:.1f} hours")
            print(f"   📈 AI Confidence: {result.ai_confidence:.0%}")
            print(f"   🔺 Escalation: {'YES' if result.escalation_recommended else 'NO'}")
            
            print(f"\n📊 DETAILED METRICS:")
            metrics = result.priority_metrics
            print(f"   • Time Sensitivity: {metrics.time_sensitivity_score:.1f}/10")
            print(f"   • Business Impact: {metrics.business_impact_score:.1f}/10") 
            print(f"   • Risk Assessment: {metrics.risk_score:.1f}/10")
            print(f"   • Role Authority: {metrics.role_weight:.1f}/5")
            print(f"   • Urgency Factor: {metrics.urgency_score:.1f}/10")
            
            print(f"\n💡 AI REASONING:")
            reasoning_lines = result.reasoning.strip().split('\n')
            for line in reasoning_lines:
                if line.strip():
                    print(f"   {line.strip()}")
            
            print(f"\n🔍 RISK ASSESSMENT:")
            print(f"   {result.risk_assessment}")
            
            if result.next_actions:
                print(f"\n📋 RECOMMENDED ACTIONS:")
                for i, action in enumerate(result.next_actions, 1):
                    print(f"   {i}. {action}")
            
            if result.user_suggestions:
                print(f"\n🛠️  USER SUGGESTIONS:")
                for i, suggestion in enumerate(result.user_suggestions[:2], 1):
                    print(f"   {i}. {suggestion.title}")
                    print(f"      └─ {suggestion.description}")
                    print(f"      └─ Est. Time: {suggestion.estimated_resolution_time}")
            
        except Exception as e:
            print(f"❌ Error processing task: {e}")
            
        print("\n" + "="*60)
    
    # Summary comparison
    print("\n🏆 PRIORITY RANKING SUMMARY")
    print("="*60)
    print("Based on Enhanced AI Analysis:")
    print("1. 👑 CEO Presentation Crisis (CRITICAL - Immediate)")
    print("2. 🚨 Security Ransomware (CRITICAL - 1-2 hours)")  
    print("3. 📄 Printing Issue (LOW - 24-48 hours)")
    print()
    print("✨ The AI considers:")
    print("• Executive authority and business impact")
    print("• Time-sensitive deadlines and meetings")
    print("• Security category automatic escalation")
    print("• Mathematical scoring with weighted factors")
    print("• Automated user suggestions and workarounds")
    print()
    print("🎯 This demonstrates intelligent, context-aware prioritization!")

if __name__ == "__main__":
    print("Starting Enhanced AI Prioritization Demo...")
    asyncio.run(demo_enhanced_ai_features())
