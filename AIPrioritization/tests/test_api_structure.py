#!/usr/bin/env python3
"""
Quick API test script to verify the new endpoint structure
"""
import asyncio
import aiohttp
import json

async def test_new_api_structure():
    """Test the new API endpoints structure"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Enhanced AI Prioritization Engine API v1")
        print("=" * 60)
        
        # Test health endpoint
        try:
            async with session.get(f"{base_url}/api/v1/health/") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health Check: {health_data.get('status', 'Unknown')}")
                else:
                    print(f"❌ Health Check Failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
        
        # Test configuration endpoints
        endpoints = [
            "/api/v1/config/categories",
            "/api/v1/config/roles", 
            "/api/v1/config/priority-model",
            "/api/v1/config/thresholds"
        ]
        
        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        print(f"✅ {endpoint}: Available")
                    else:
                        print(f"❌ {endpoint}: HTTP {response.status}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
        
        # Test prioritization endpoint
        sample_task = {
            "id": "api_test_001",
            "title": "Test API endpoint functionality",
            "description": "Testing the new API structure with enhanced Swagger documentation",
            "category": "DEVELOPMENT",
            "requester_role": "DEVELOPER",
            "requester_name": "API Tester"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v1/prioritization/sync",
                json=sample_task,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Sync Prioritization: Priority Score {result.get('priority_metrics', {}).get('final_priority_score', 'Unknown')}")
                    print(f"   Urgency Level: {result.get('urgency_level', 'Unknown')}")
                    print(f"   SLA Hours: {result.get('suggested_sla_hours', 'Unknown')}")
                else:
                    print(f"❌ Sync Prioritization: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Sync Prioritization Error: {e}")
        
        print("\n🎯 API Testing Complete!")
        print(f"📖 View full documentation at: {base_url}/docs")
        print(f"📋 Alternative docs at: {base_url}/redoc")

if __name__ == "__main__":
    print("🚀 Starting API Structure Test")
    print("📝 Make sure the server is running: uvicorn main:app --reload")
    print()
    
    try:
        asyncio.run(test_new_api_structure())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Ensure the server is running and accessible")
