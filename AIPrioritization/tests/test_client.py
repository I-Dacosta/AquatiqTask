#!/usr/bin/env python3
"""Simple test client for the AI Priority Engine"""

import asyncio
import aioredis
import json
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

async def test_redis_integration():
    """Test Redis pub/sub integration"""
    print("🔍 Testing Redis integration...")
    
    # Connect to Redis
    redis = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    
    # Subscribe to results channel
    pubsub = redis.pubsub()
    await pubsub.subscribe("prioritize_results")
    
    # Test task data
    test_task = {
        "id": "test_001",
        "title": "Test urgent task",
        "description": "Testing the AI priority engine",
        "category": "support",
        "requester_role": "cfo",
        "requester_name": "Test User",
        "meeting_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "business_value": 9,
        "risk_level": 8,
        "estimated_effort_hours": 1.0,
        "workaround_available": False
    }
    
    # Publish test task
    await redis.publish("prioritize_events", json.dumps(test_task))
    print(f"✅ Published test task: {test_task['id']}")
    
    # Wait for result
    print("⏳ Waiting for prioritization result...")
    timeout = 10  # seconds
    start_time = asyncio.get_event_loop().time()
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            result = json.loads(message["data"])
            print(f"✅ Received result: {result}")
            break
        
        # Timeout check
        if asyncio.get_event_loop().time() - start_time > timeout:
            print("❌ Timeout waiting for result")
            break
    
    await redis.close()

def test_health_endpoint():
    """Test health check endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Is it running?")

def test_prioritize_endpoint():
    """Test manual prioritization endpoint"""
    print("🔍 Testing prioritize endpoint...")
    
    test_task = {
        "id": "api_test_001",
        "title": "API test task",
        "description": "Testing the REST API",
        "category": "security",
        "requester_role": "ceo",
        "requester_name": "API Test",
        "business_value": 7,
        "risk_level": 9,
        "estimated_effort_hours": 2.0,
        "workaround_available": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/prioritize", json=test_task)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prioritization successful:")
            print(f"   Priority: {result['priority']}")
            print(f"   Score: {result['score']}")
            print(f"   Reasoning: {result['reasoning']}")
            print(f"   Action: {result['recommended_action']}")
        else:
            print(f"❌ Prioritization failed: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Is it running?")

async def main():
    """Run all tests"""
    print("🚀 Starting AI Priority Engine tests...\n")
    
    # Test health endpoint
    test_health_endpoint()
    print()
    
    # Test REST API
    test_prioritize_endpoint()
    print()
    
    # Test Redis integration
    await test_redis_integration()
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
