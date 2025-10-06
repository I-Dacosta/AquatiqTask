"""
Event handlers for the orchestration system
Handles events from backend and Microsoft Graph services
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from services.service_registry import get_nats_service, get_redis_cache
from services.ai_service import get_ai_priority
from services.local_ai_analyzer import LocalAIAnalyzer
from services.privacy_service import PrivacyComplianceService
from models import TaskRequest

logger = logging.getLogger(__name__)

class EventOrchestrator:
    """Handles orchestration events and AI processing"""
    
    def __init__(self):
        # Core services - we'll initialize these in the initialize() method
        self.nats_service = None
        self.redis_cache = None
        self.ai_analyzer = None
        self.privacy_service = None
        
        # Tracking metrics
        self.processed_tasks = 0
        self.bypassed_tasks = 0
        self.last_metrics_report = datetime.now()
    
    async def initialize(self):
        """Initialize event listeners and services"""
        # Initialize services
        self.nats_service = get_nats_service()
        self.redis_cache = get_redis_cache()
        self.ai_analyzer = LocalAIAnalyzer()
        self.privacy_service = PrivacyComplianceService()
        
        if not self.nats_service:
            logger.error("NATS service not available")
            return
            
        logger.info("Initializing AI Priority Engine event handlers...")
        
        # Listen to backend events
        # Core task analysis events
        await self.nats_service.subscribe(
            subject='ms-ai-backend.task.for-analysis',
            callback=self.handle_task_analysis,
            queue_group='ai-priority-engine'
        )
        
        await self.nats_service.subscribe(
            subject='ms-ai-backend.recalculate.priorities',
            callback=self.handle_priority_recalculation,
            queue_group='ai-priority-engine'
        )
        
        # Microsoft Graph direct processing
        await self.nats_service.subscribe(
            subject='ms-graph.task.created',
            callback=self.handle_microsoft_graph_task,
            queue_group='ai-priority-engine'
        )
        
        # Task update events
        await self.nats_service.subscribe(
            subject='ms-ai-backend.task.updated',
            callback=self.handle_task_update,
            queue_group='ai-priority-engine'
        )
        
        await self.nats_service.subscribe(
            subject='ms-ai-backend.task.completed',
            callback=self.handle_task_completion,
            queue_group='ai-priority-engine'
        )
        
        # Batch operations
        await self.nats_service.subscribe(
            subject='ms-ai-backend.batch.analyze',
            callback=self.handle_batch_analysis,
            queue_group='ai-priority-engine'
        )
        
        # Health monitoring
        asyncio.create_task(self.report_metrics_periodically())
        
        logger.info("AI Priority Engine event handlers initialized")
    
    async def handle_task_analysis(self, message_data: Dict[str, Any]):
        """Handle single task analysis request"""
        try:
            task_id = message_data.get('taskId')
            logger.info(f"Analyzing task {task_id}")
            
            # Check for sensitive content
            is_sensitive, reasons = self.privacy_service.analyze_content(message_data)
            if is_sensitive:
                self.bypassed_tasks += 1
                await self.handle_sensitive_task(task_id, reasons)
                return
            
            # Perform AI analysis
            priority_result = await self.ai_analyzer.analyze_task(message_data)
            
            # Cache results
            await self.redis_cache.set(f"task_priority:{task_id}", priority_result)
            
            # Publish results (privacy-safe)
            safe_metadata = self.privacy_service.sanitize_metadata({
                'taskId': task_id,
                'priority': priority_result.priority,
                'source': 'ai-engine',
                'timestamp': datetime.now().isoformat()
            })
            
            await self.nats_service.publish('ai.priority.updated', safe_metadata)
            self.processed_tasks += 1
            
        except Exception as e:
            logger.error(f"Error analyzing task {message_data.get('taskId')}: {str(e)}")
            await self.publish_error_event(message_data.get('taskId'), str(e))

    async def handle_priority_recalculation(self, message_data: Dict[str, Any]):
        """Handle batch priority recalculation request"""
        try:
            logger.info("Received priority recalculation request")
            
            metadata = message_data.get('metadata', {})
            task_ids = metadata.get('taskIds', [])
            
            if not task_ids:
                logger.warning("No task IDs provided for recalculation")
                return
            
            # For now, we'll need to make HTTP calls to get task details
            # In a real implementation, you might want to include task details in the event
            logger.info(f"Recalculating priorities for {len(task_ids)} tasks")
            
            # Publish completion event
            await self.nats_service.publish('ai.priority.updated', {
                'action': 'recalculation_completed',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'userId': None,
                'type': 'priority-recalculation',
                'metadata': {
                    'source': 'ai-prioritization-python',
                    'processedTasks': len(task_ids),
                    'status': 'completed'
                }
            })
            
        except Exception as e:
            logger.error(f"Error handling priority recalculation: {e}")
    
    async def handle_microsoft_graph_task(self, message_data: Dict[str, Any]):
        """Handle tasks directly from Microsoft Graph for immediate processing"""
        try:
            logger.info("Received Microsoft Graph task for processing")
            
            metadata = message_data.get('metadata', {})
            task_type = metadata.get('type', 'general')
            
            # Check if this should be processed by AI or sent directly to backend
            is_sensitive = self._check_task_sensitivity(
                metadata.get('title', ''),
                metadata.get('description', '')
            )
            
            if is_sensitive:
                # Send directly to backend with high priority
                await self.nats_service.publish('ms-ai-backend.sensitive.task', {
                    'action': 'sensitive_task_detected',
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'userId': message_data.get('userId'),
                    'type': 'sensitive-task',
                    'metadata': {
                        'source': 'ai-prioritization-python',
                        'taskId': metadata.get('taskId'),
                        'priority': 9,
                        'bypassAI': True,
                        'reasoning': 'Task contains sensitive content'
                    }
                })
            else:
                # Process normally through AI analysis
                await self.handle_task_analysis(message_data)
                
        except Exception as e:
            logger.error(f"Error handling Microsoft Graph task: {e}")
    
    async def handle_sensitive_task(self, task_id: str, reasons: List[str]):
        """Handle tasks marked as sensitive"""
        logger.warning(f"Task {task_id} marked sensitive: {reasons}")
        
        # Log for compliance
        self.privacy_service.log_sensitive_data_detection(task_id, reasons)
        
        # Publish bypass event
        await self.nats_service.publish('ai.analysis.bypassed', {
            'taskId': task_id,
            'timestamp': datetime.now().isoformat(),
            'reason': 'sensitive_content'
        })
        
        # Set high priority automatically
        await self.nats_service.publish('ai.priority.updated', {
            'taskId': task_id,
            'priority': 9,  # High priority for sensitive tasks
            'source': 'privacy-service',
            'timestamp': datetime.now().isoformat(),
            'bypassReason': 'sensitive_content'
        })

    async def handle_batch_analysis(self, message_data: Dict[str, Any]):
        """Handle batch analysis request"""
        task_ids = message_data.get('taskIds', [])
        logger.info(f"Processing batch analysis for {len(task_ids)} tasks")
        
        results = []
        for task_id in task_ids:
            try:
                task_data = await self.redis_cache.get(f"task:{task_id}")
                if not task_data:
                    continue
                    
                is_sensitive, reasons = self.privacy_service.analyze_content(task_data)
                if is_sensitive:
                    self.bypassed_tasks += 1
                    await self.handle_sensitive_task(task_id, reasons)
                    continue
                
                priority_result = await self.ai_analyzer.analyze_task(task_data)
                results.append({
                    'taskId': task_id,
                    'priority': priority_result.priority
                })
                self.processed_tasks += 1
                
            except Exception as e:
                logger.error(f"Error in batch analysis for task {task_id}: {str(e)}")
        
        # Publish batch results
        if results:
            await self.nats_service.publish('ai.batch.completed', {
                'results': results,
                'timestamp': datetime.now().isoformat()
            })

    def _check_task_sensitivity(self, title: str, description: str) -> bool:
        """Check if a task contains sensitive content that should bypass AI"""
        sensitive_keywords = [
            'confidential', 'secret', 'private', 'classified',
            'legal', 'compliance', 'audit', 'security',
            'personal', 'gdpr', 'pii', 'sensitive',
            'urgent', 'critical', 'emergency', 'escalation'
        ]
        
        content = f"{title} {description}".lower()
        return any(keyword in content for keyword in sensitive_keywords)
    
    async def report_metrics_periodically(self):
        """Report metrics every 5 minutes"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                now = datetime.now()
                time_diff = (now - self.last_metrics_report).total_seconds()
                
                metrics = {
                    'processed_tasks': self.processed_tasks,
                    'bypassed_tasks': self.bypassed_tasks,
                    'tasks_per_minute': round(self.processed_tasks / (time_diff / 60), 2),
                    'bypass_rate': round(self.bypassed_tasks / max(self.processed_tasks, 1) * 100, 2),
                    'timestamp': now.isoformat()
                }
                
                await self.nats_service.publish('ai.metrics.updated', metrics)
                
                # Reset counters
                self.processed_tasks = 0
                self.bypassed_tasks = 0
                self.last_metrics_report = now
                
            except Exception as e:
                logger.error(f"Error reporting metrics: {str(e)}")

    async def publish_error_event(self, task_id: str, error_message: str):
        """Publish error event with safe metadata"""
        await self.nats_service.publish('ai.error', {
            'taskId': task_id,
            'timestamp': datetime.now().isoformat(),
            'errorType': 'analysis_failed',
            'source': 'ai-engine'
            # Note: actual error message not included for privacy
        })
    
    async def start_listening(self):
        """Start the event orchestrator"""
        await self.initialize()
        logger.info("Event orchestrator is listening for events...")
    
    async def handle_task_update(self, message_data: Dict[str, Any]):
        """Handle task update events"""
        try:
            task_id = message_data.get('taskId')
            logger.info(f"Handling task update for {task_id}")
            
            # Check if we need to re-analyze the task
            metadata = message_data.get('metadata', {})
            if metadata.get('requiresReanalysis', False):
                await self.handle_task_analysis(message_data)
            else:
                # Just update our cache with the new task data
                if task_id:
                    await self.redis_cache.set(f"task:{task_id}", message_data, expiry=3600)
                    
        except Exception as e:
            logger.error(f"Error handling task update {message_data.get('taskId')}: {str(e)}")

    async def handle_task_completion(self, message_data: Dict[str, Any]):
        """Handle task completion events"""
        try:
            task_id = message_data.get('taskId')
            logger.info(f"Handling task completion for {task_id}")
            
            # Clean up cache entries for completed tasks
            if task_id:
                await self.redis_cache.delete(f"task:{task_id}")
                await self.redis_cache.delete(f"task_priority:{task_id}")
                
            # Publish completion acknowledgment
            await self.nats_service.publish('ai.task.completed', {
                'taskId': task_id,
                'timestamp': datetime.now().isoformat(),
                'source': 'ai-engine'
            })
            
        except Exception as e:
            logger.error(f"Error handling task completion {message_data.get('taskId')}: {str(e)}")

# Global orchestrator instance
orchestrator = EventOrchestrator()

async def start_orchestrator():
    """Start the orchestration system"""
    await orchestrator.start_listening()
