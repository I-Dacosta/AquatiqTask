#!/usr/bin/env python3
"""
Enhanced AI Prioritization Engine Demo
Demonstrates the complete Redis Pub/Sub workflow with improved error handling and monitoring
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import TaskRequest, UserRole, TaskCategory, UrgencyLevel
from services.redis_service import redis_service
from services.ai_service import get_ai_priority
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DemoManager:
    """Manages the demo workflow"""
    
    def __init__(self):
        self.processed_tasks = []
        self.demo_running = False
    
    async def initialize(self):
        """Initialize services"""
        logger.info("🚀 Initializing Enhanced AI Prioritization Engine Demo")
        await redis_service.initialize()
        logger.info("✅ Redis service initialized")
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up demo resources")
        await redis_service.close()
        logger.info("✅ Demo cleanup complete")
    
    async def create_demo_tasks(self) -> list[TaskRequest]:
        """Create a variety of demo tasks"""
        now = datetime.now()
        
        demo_tasks = [
            TaskRequest(
                id="DEMO-001",
                title="Critical Security Breach - Unauthorized Access Detected",
                description="Multiple failed login attempts from suspicious IP addresses. Possible brute force attack in progress.",
                category=TaskCategory.SECURITY,
                requester_role=UserRole.IT_ADMIN,
                requester_name="Security Admin",
                tags=["security", "breach", "urgent", "unauthorized-access"],
                deadline=now + timedelta(hours=1),
                context="Production environment affected, multiple user accounts at risk"
            ),
            TaskRequest(
                id="DEMO-002", 
                title="CEO Presentation Setup - Board Meeting",
                description="Need to configure the main conference room for CEO's quarterly board presentation. Includes AV setup, network testing, and backup systems.",
                category=TaskCategory.MEETING_PREP,
                requester_role=UserRole.CEO,
                requester_name="CEO Office",
                tags=["presentation", "board-meeting", "ceo", "conference-room"],
                meeting_time=now + timedelta(hours=3),
                context="Quarterly board meeting with external stakeholders"
            ),
            TaskRequest(
                id="DEMO-003",
                title="Database Performance Optimization",
                description="Main customer database experiencing slow query performance during peak hours affecting customer experience.",
                category=TaskCategory.INFRASTRUCTURE,
                requester_role=UserRole.DEVELOPER,
                requester_name="Database Team",
                tags=["database", "performance", "optimization", "customer-impact"],
                deadline=now + timedelta(days=2),
                context="Customer complaints increasing, performance degraded by 40%"
            ),
            TaskRequest(
                id="DEMO-004",
                title="New Employee Laptop Setup",
                description="Standard laptop configuration for new marketing hire starting Monday. Install required software and configure access permissions.",
                category=TaskCategory.SUPPORT,
                requester_role=UserRole.MANAGER,
                requester_name="HR Manager", 
                tags=["new-employee", "laptop", "setup", "onboarding"],
                deadline=now + timedelta(days=3),
                context="New hire orientation scheduled for Monday morning"
            ),
            TaskRequest(
                id="DEMO-005",
                title="Compliance Audit Preparation - GDPR Documentation",
                description="Prepare all GDPR compliance documentation for upcoming external audit. Review data processing procedures and privacy policies.",
                category=TaskCategory.COMPLIANCE,
                requester_role=UserRole.CTO,
                requester_name="Legal & Compliance",
                tags=["gdpr", "compliance", "audit", "documentation"],
                deadline=now + timedelta(weeks=1),
                context="External auditor scheduled for next week, potential regulatory fines if non-compliant"
            )
        ]
        
        return demo_tasks
    
    async def process_task_handler(self, data: Dict[str, Any]):
        """Handle processed tasks (simulate result consumer)"""
        logger.info(f"📥 Demo received result for task: {data.get('request_id', 'unknown')}")
        self.processed_tasks.append(data)
        
        # Pretty print the result
        priority_score = data.get('priority_metrics', {}).get('final_priority_score', 0)
        urgency = data.get('urgency_level', 'unknown')
        sla_hours = data.get('suggested_sla_hours', 0)
        
        logger.info(f"   ⭐ Priority: {priority_score:.1f}/10 | Urgency: {urgency} | SLA: {sla_hours:.1f}h")
    
    async def run_demo(self):
        """Run the complete demo workflow"""
        try:
            self.demo_running = True
            
            # Create demo tasks
            logger.info("📋 Creating demo tasks...")
            demo_tasks = await self.create_demo_tasks()
            logger.info(f"✅ Created {len(demo_tasks)} demo tasks")
            
            # Start listening for results
            logger.info("🎧 Starting result listener...")
            listener_task = asyncio.create_task(self._listen_for_results())
            
            # Give listener time to start
            await asyncio.sleep(1)
            
            # Submit tasks for processing  
            logger.info("📤 Submitting tasks for AI processing...")
            for task in demo_tasks:
                success = await redis_service.publish(
                    settings.PRIORITIZATION_REQUEST_CHANNEL,
                    task.model_dump()
                )
                if success:
                    logger.info(f"   ✅ Submitted: {task.id} - {task.title[:50]}...")
                else:
                    logger.error(f"   ❌ Failed to submit: {task.id}")
                
                # Small delay between submissions
                await asyncio.sleep(0.5)
            
            # Wait for processing
            logger.info("⏳ Waiting for AI processing results...")
            timeout = 30  # 30 seconds timeout
            start_time = asyncio.get_event_loop().time()
            
            while len(self.processed_tasks) < len(demo_tasks):
                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.warning(f"⚠️  Timeout: Only {len(self.processed_tasks)}/{len(demo_tasks)} tasks processed")
                    break
                await asyncio.sleep(1)
            
            # Stop listener
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
            
            # Display results summary
            await self._display_results_summary()
            
        except Exception as e:
            logger.error(f"❌ Demo error: {e}")
        finally:
            self.demo_running = False
    
    async def _listen_for_results(self):
        """Listen for processing results"""
        try:
            await redis_service.start_listening(self.process_task_handler)
        except asyncio.CancelledError:
            logger.info("🛑 Result listener stopped")
    
    async def _display_results_summary(self):
        """Display a summary of all processing results"""
        logger.info("\n" + "="*80)
        logger.info("📊 DEMO RESULTS SUMMARY")
        logger.info("="*80)
        
        if not self.processed_tasks:
            logger.info("❌ No tasks were processed")
            return
        
        # Sort by priority score (highest first)
        sorted_tasks = sorted(
            self.processed_tasks, 
            key=lambda x: x.get('priority_metrics', {}).get('final_priority_score', 0),
            reverse=True
        )
        
        for i, result in enumerate(sorted_tasks, 1):
            metrics = result.get('priority_metrics', {})
            logger.info(f"\n{i}. Task: {result.get('request_id', 'unknown')}")
            logger.info(f"   Priority Score: {metrics.get('final_priority_score', 0):.1f}/10")
            logger.info(f"   Urgency Level: {result.get('urgency_level', 'unknown')}")
            logger.info(f"   SLA Hours: {result.get('suggested_sla_hours', 0):.1f}")
            logger.info(f"   Escalation: {'Yes' if result.get('escalation_recommended') else 'No'}")
            logger.info(f"   AI Confidence: {result.get('ai_confidence', 0):.1%}")
        
        logger.info("\n" + "="*80)

async def main():
    """Main demo function"""
    demo = DemoManager()
    
    try:
        await demo.initialize()
        await demo.run_demo()
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    logger.info("🎯 Starting Enhanced AI Prioritization Engine Demo")
    logger.info("📡 This demo requires Redis to be running on localhost:6379")
    logger.info("🤖 OpenAI API key should be configured for full AI features")
    logger.info("-" * 80)
    
    asyncio.run(main())
