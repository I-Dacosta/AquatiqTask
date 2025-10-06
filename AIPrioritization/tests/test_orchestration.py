"""
Integration tests for the AI Prioritization Engine
Tests all major event flows and privacy features
"""
import asyncio
import json
import pytest
import pytest_asyncio
import redis.asyncio as redis
from nats.aio.client import Client as NATS
from datetime import datetime, timedelta
from typing import Dict, Any

# Mock task data
SAMPLE_TASKS = {
    "normal_task": {
        "taskId": "task-001",
        "title": "Update documentation",
        "description": "Update the API documentation with new endpoints",
        "category": "Development",
        "requester": "dev@company.com"
    },
    "sensitive_task": {
        "taskId": "task-002",
        "title": "CONFIDENTIAL: Review legal documents",
        "description": "Review legal compliance documents for audit",
        "category": "Legal",
        "requester": "legal@company.com"
    },
    "urgent_task": {
        "taskId": "task-003",
        "title": "URGENT: Fix production outage",
        "description": "Critical system failure in production environment",
        "category": "Infrastructure",
        "requester": "ops@company.com"
    }
}

# Test cases for batch processing
BATCH_TASKS = [
    {"taskId": f"batch-{i}", 
     "title": f"Task {i}", 
     "description": "Regular task for batch processing"} 
    for i in range(1, 4)
]

# Connection configuration
NATS_URL = "nats://localhost:4222"
REDIS_URL = "redis://localhost:6379"
DEFAULT_TIMEOUT = 5.0
METRICS_TIMEOUT = 10.0

class TestAIPrioritization:
    @pytest_asyncio.fixture(scope="class")
    async def nats_client(self):
        """Setup NATS client for testing"""
        nc = NATS()
        try:
            await nc.connect(NATS_URL)
            yield nc
        finally:
            try:
                await nc.drain()
            except:
                pass
            await nc.close()

    @pytest_asyncio.fixture(scope="class")
    async def redis_client(self):
        """Setup Redis client for testing"""
        try:
            r = redis.Redis.from_url(REDIS_URL)
            yield r
        finally:
            await r.close()

    async def wait_for_message(self, nats_client: NATS, subject: str, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Wait for a message on a specific subject"""
        future = asyncio.Future()
        
        async def cb(msg):
            nonlocal future
            if not future.done():  # Only set result if future hasn't completed
                try:
                    data = json.loads(msg.data.decode())
                    future.set_result(data)
                except Exception as e:
                    if not future.done():
                        future.set_exception(e)
        
        sid = await nats_client.subscribe(subject, cb=cb)
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"No message received on {subject} within {timeout} seconds") from e
        finally:
            await nats_client.unsubscribe(sid)

    @pytest.mark.asyncio
    async def test_normal_task_analysis(self, nats_client):
        """Test normal task analysis flow"""
        # Publish task for analysis
        await nats_client.publish(
            "ms-ai-backend.task.for-analysis",
            json.dumps(SAMPLE_TASKS["normal_task"]).encode()
        )
        
        # Wait for priority result
        result = await self.wait_for_message(nats_client, "ai.priority.updated")
        
        assert "taskId" in result
        assert "priority" in result
        assert "source" in result
        assert result["source"] == "ai-engine"

    @pytest.mark.asyncio
    async def test_sensitive_task_detection(self, nats_client):
        """Test sensitive task detection and bypass"""
        # Publish sensitive task
        await nats_client.publish(
            "ms-ai-backend.task.for-analysis",
            json.dumps(SAMPLE_TASKS["sensitive_task"]).encode()
        )
        
        # Wait for bypass notification
        bypass_result = await self.wait_for_message(nats_client, "ai.analysis.bypassed")
        assert bypass_result["reason"] == "sensitive_content"
        
        # Wait for priority update (should be high priority)
        priority_result = await self.wait_for_message(nats_client, "ai.priority.updated")
        assert priority_result["priority"] == 9
        assert priority_result["source"] == "privacy-service"

    @pytest.mark.asyncio
    async def test_batch_analysis(self, nats_client, redis_client):
        """Test batch task analysis"""
        # Store tasks in Redis first
        try:
            for task in BATCH_TASKS:
                await redis_client.set(f"task:{task['taskId']}", json.dumps(task))
            
            # Request batch analysis
            await nats_client.publish(
                "ms-ai-backend.batch.analyze",
                json.dumps({"taskIds": [t["taskId"] for t in BATCH_TASKS]}).encode()
            )
            
            # Wait for batch completion
            result = await self.wait_for_message(nats_client, "ai.batch.completed")
            
            assert "results" in result
            assert len(result["results"]) == len(BATCH_TASKS)
            assert all("priority" in r for r in result["results"])
        finally:
            # Cleanup Redis after test
            for task in BATCH_TASKS:
                await redis_client.delete(f"task:{task['taskId']}")

    @pytest.mark.asyncio
    async def test_metrics_reporting(self, nats_client):
        """Test metrics reporting with longer timeout"""
        # Process a few tasks to generate metrics
        for task in [SAMPLE_TASKS["normal_task"], SAMPLE_TASKS["urgent_task"]]:
            await nats_client.publish(
                "ms-ai-backend.task.for-analysis",
                json.dumps(task).encode()
            )
        
        # Wait for metrics update with extended timeout
        metrics = await self.wait_for_message(nats_client, "ai.metrics.updated", timeout=METRICS_TIMEOUT)
        
        assert "processed_tasks" in metrics
        assert "bypassed_tasks" in metrics
        assert "tasks_per_minute" in metrics
        assert "bypass_rate" in metrics
        assert "timestamp" in metrics

    @pytest.mark.asyncio
    async def test_error_handling(self, nats_client):
        """Test error handling and safe error reporting"""
        # Send malformed task data
        await nats_client.publish(
            "ms-ai-backend.task.for-analysis",
            json.dumps({"taskId": "error-task"}).encode()  # Missing required fields
        )
        
        # Wait for error event
        error_result = await self.wait_for_message(nats_client, "ai.error")
        
        assert error_result["taskId"] == "error-task"
        assert error_result["errorType"] == "analysis_failed"
        assert "error_message" not in error_result  # Ensure error details are not leaked

    @pytest.mark.asyncio
    async def test_microsoft_graph_integration(self, nats_client):
        """Test Microsoft Graph task integration"""
        # Send task from MS Graph
        await nats_client.publish(
            "ms-graph.task.created",
            json.dumps({
                "userId": "user123",
                "metadata": {
                    "taskId": "msg-task-001",
                    "title": "Review presentation",
                    "description": "Review Q2 presentation for board meeting",
                    "type": "calendar"
                }
            }).encode()
        )
        
        # Wait for priority result
        result = await self.wait_for_message(nats_client, "ai.priority.updated")
        
        assert result["taskId"] == "msg-task-001"
        assert "priority" in result
