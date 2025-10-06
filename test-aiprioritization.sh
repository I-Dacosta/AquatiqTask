#!/bin/bash

echo "🧪 Testing AIPrioritization Service Integration"
echo "============================================="

# Test if Docker services are running
echo "📋 Checking Docker services..."
docker-compose ps

echo ""
echo "🤖 Testing AIPrioritization service endpoints..."

# Test health endpoint
echo "1. Health check..."
curl -s http://localhost:8080/health | jq '.'

echo ""
echo "2. Testing legacy /classify endpoint (n8n compatibility)..."
curl -s -X POST http://localhost:8080/classify \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent: PowerPoint won'\''t open before CEO meeting",
    "body": "PowerPoint is crashing when I try to open my presentation. Meeting with CEO in 30 minutes. Need immediate help!",
    "sender": "john.doe@company.com",
    "role_hint": "manager",
    "due_text": "in 30 minutes",
    "est_minutes": 5
  }' | jq '.'

echo ""
echo "3. Testing modern API endpoint..."
curl -s -X POST http://localhost:8080/api/v1/prioritization/sync \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_001",
    "title": "Database connection issues",
    "description": "Our production database is experiencing intermittent connection drops affecting 100+ users",
    "category": "INFRASTRUCTURE",
    "requester_role": "IT_ADMIN",
    "requester_name": "Sarah Tech"
  }' | jq '.'

echo ""
echo "✅ Test completed! Check outputs above for any errors."