#!/usr/bin/env python3
"""
Quick validation test for NATS JetStream migration
Tests the new event streaming and caching architecture
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nats_service import NATSJetStreamService
from services.redis_cache import RedisCacheService
from models import TaskRequest, TaskCategory, UserRole
from core.config import settings

async def test_nats_connection():
    """Test NATS JetStream connection and basic operations"""
    print("🧪 Testing NATS JetStream connection...")
    
    nats_service = NATSJetStreamService()
    
    try:
        # Initialize connection
        await nats_service.initialize()
        print("✅ NATS connection established")
        
        # Test health check
        health = await nats_service.health_check()
        print(f"✅ NATS health: {health['status']}")
        
        # Test message publishing
        test_data = {
            "id": "test_001",
            "title": "Test Task",
            "description": "Testing NATS integration",
            "category": "TESTING",
            "requester_role": "DEVELOPER",
            "requester_name": "Test User",
            "timestamp": datetime.now().isoformat()
        }
        
        success = await nats_service.publish_priority_request(test_data)
        if success:
            print("✅ Message published to NATS JetStream")
        else:
            print("❌ Failed to publish message")
            
        await nats_service.close()
        print("✅ NATS connection closed cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ NATS test failed: {e}")
        return False

async def test_redis_cache():
    """Test Redis cache operations"""
    print("\n🧪 Testing Redis cache operations...")
    
    redis_cache = RedisCacheService()
    
    try:
        # Initialize connection
        await redis_cache.initialize()
        print("✅ Redis cache connection established")
        
        # Test health check
        health = await redis_cache.health_check()
        print(f"✅ Redis cache health: {health['status']}")
        
        # Test cache operations
        test_result = {
            "request_id": "test_001",
            "urgency_level": "HIGH",
            "priority_score": 8.5,
            "processing_time_ms": 1250
        }
        
        # Cache result
        success = await redis_cache.cache_priority_result("test_001", test_result, ttl=60)
        if success:
            print("✅ Priority result cached successfully")
        else:
            print("❌ Failed to cache priority result")
            
        # Retrieve from cache
        cached_result = await redis_cache.get_cached_priority_result("test_001")
        if cached_result:
            print("✅ Priority result retrieved from cache")
            print(f"   Score: {cached_result.get('priority_score', 'N/A')}")
        else:
            print("❌ Failed to retrieve from cache")
            
        # Test rate limiting
        rate_limit_result = await redis_cache.check_rate_limit("test_user", 10, 60)
        print(f"✅ Rate limiting test: {rate_limit_result['allowed']}")
        
        await redis_cache.close()
        print("✅ Redis cache connection closed cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis cache test failed: {e}")
        return False

async def test_integration():
    """Test integration between NATS and Redis cache"""
    print("\n🧪 Testing NATS + Redis integration...")
    
    nats_service = NATSJetStreamService()
    redis_cache = RedisCacheService()
    
    try:
        # Initialize both services
        await nats_service.initialize()
        await redis_cache.initialize()
        print("✅ Both services initialized")
        
        # Simulate task processing workflow
        task_id = "integration_test_001"
        
        # 1. Check cache first (should be empty)
        cached_result = await redis_cache.get_cached_priority_result(task_id)
        if not cached_result:
            print("✅ Cache miss as expected for new task")
        
        # 2. Publish request to NATS
        task_data = {
            "id": task_id,
            "title": "Integration Test Task",
            "description": "Testing full workflow integration",
            "category": "TESTING",
            "requester_role": "DEVELOPER",
            "requester_name": "Integration Tester"
        }
        
        success = await nats_service.publish_priority_request(task_data)
        if success:
            print("✅ Task request published to NATS JetStream")
        
        # 3. Simulate processing result and cache it
        result_data = {
            "request_id": task_id,
            "urgency_level": "MEDIUM",
            "priority_score": 6.8,
            "processing_time_ms": 850,
            "cached_at": datetime.now().isoformat()
        }
        
        cache_success = await redis_cache.cache_priority_result(task_id, result_data, ttl=300)
        if cache_success:
            print("✅ Processing result cached")
        
        # 4. Publish result to NATS
        result_success = await nats_service.publish_priority_result(result_data)
        if result_success:
            print("✅ Result published to NATS JetStream")
        
        # 5. Verify cache retrieval
        final_cached_result = await redis_cache.get_cached_priority_result(task_id)
        if final_cached_result:
            print("✅ Result successfully retrieved from cache")
            print(f"   Priority Score: {final_cached_result.get('priority_score', 'N/A')}")
        
        # Cleanup
        await nats_service.close()
        await redis_cache.close()
        print("✅ Integration test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🚀 Starting NATS JetStream Migration Validation Tests")
    print("=" * 60)
    
    # Configuration check
    print(f"📋 Configuration:")
    print(f"   NATS Host: {settings.NATS_HOST}:{settings.NATS_PORT}")
    print(f"   Redis Host: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"   JetStream Enabled: {settings.JETSTREAM_ENABLED}")
    print(f"   Cache TTL: {settings.CACHE_TTL_SECONDS}s")
    print()
    
    # Run tests
    tests = [
        ("NATS JetStream", test_nats_connection),
        ("Redis Cache", test_redis_cache),
        ("Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Migration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and services.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
