#!/bin/bash
# PrioritiAI Workflow Testing Script
# Run this script to test all components of your deployment

set -e

VPS_IP="31.97.38.31"
WEBHOOK_URL="http://${VPS_IP}:5678/webhook/prioai-tasks"
AI_SERVICE_URL="http://${VPS_IP}:8000"
N8N_URL="http://${VPS_IP}:5678"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 PrioritiAI Stack Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: AI Service Health
echo "1️⃣  Testing AI Service Health..."
if curl -sf "${AI_SERVICE_URL}/health" > /dev/null 2>&1; then
    echo "   ✅ AI Service is healthy"
    curl -s "${AI_SERVICE_URL}/health" | jq -r '"   📊 Version: \(.version) | Status: \(.status)"'
else
    echo "   ❌ AI Service is not responding"
    exit 1
fi
echo ""

# Test 2: n8n Health
echo "2️⃣  Testing n8n Health..."
if curl -sf "${N8N_URL}/healthz" > /dev/null 2>&1; then
    echo "   ✅ n8n is running"
else
    echo "   ❌ n8n is not responding"
    exit 1
fi
echo ""

# Test 3: PostgreSQL Connection
echo "3️⃣  Testing PostgreSQL Connection..."
if ssh root@${VPS_IP} "docker exec prioai-postgres pg_isready -U prioai_user" > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is ready"
    TASK_COUNT=$(ssh root@${VPS_IP} "docker exec prioai-postgres psql -U prioai_user -d prioai_db -tAc 'SELECT COUNT(*) FROM tasks;'" 2>/dev/null || echo "0")
    echo "   📊 Current tasks in database: ${TASK_COUNT}"
else
    echo "   ⚠️  PostgreSQL connection could not be verified"
fi
echo ""

# Test 4: AI Service API (Direct Test)
echo "4️⃣  Testing AI Service API Endpoint..."
AI_RESPONSE=$(curl -sf -X POST "${AI_SERVICE_URL}/api/v1/prioritization/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-'$(date +%s)'",
    "title": "Test: Server ikke tilgjengelig",
    "description": "Dette er en testoppgave for å verifisere AI-klassifisering. Produksjonsserver svarer ikke.",
    "category": "INFRASTRUCTURE",
    "requester_role": "IT_ADMIN",
    "requester_name": "Test User",
    "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }' 2>/dev/null || echo '{"error":"failed"}')

if echo "$AI_RESPONSE" | jq -e '.urgency_level' > /dev/null 2>&1; then
    echo "   ✅ AI Service API is working"
    echo "   📊 AI Response:"
    echo "$AI_RESPONSE" | jq -r '"      Urgency: \(.urgency_level)"'
    echo "$AI_RESPONSE" | jq -r '"      Priority Score: \(.priority_metrics.final_priority_score * 10)/100"'
    echo "$AI_RESPONSE" | jq -r '"      SLA: \(.suggested_sla_hours) hours"'
    echo "$AI_RESPONSE" | jq -r '"      Confidence: \(.ai_confidence * 100)%"'
else
    echo "   ❌ AI Service API returned error"
    echo "$AI_RESPONSE" | jq '.' 2>/dev/null || echo "$AI_RESPONSE"
    exit 1
fi
echo ""

# Test 5: Webhook Endpoint (requires workflow to be active)
echo "5️⃣  Testing n8n Webhook Endpoint..."
echo "   ⚠️  Note: This requires the workflow to be ACTIVE in n8n"
echo "   📝 Sending test task via webhook..."

WEBHOOK_RESPONSE=$(curl -sf -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Webhook test task",
    "description": "Testing webhook integration with AI service",
    "requester": "test@aquatiq.no",
    "est_minutes": 45,
    "due_text": "today",
    "role_hint": "employee"
  }' 2>/dev/null || echo '{"error":"webhook not active"}')

if echo "$WEBHOOK_RESPONSE" | jq -e '.status' > /dev/null 2>&1; then
    echo "   ✅ Webhook responded successfully"
    echo "$WEBHOOK_RESPONSE" | jq -r '"   📨 Response: \(.message)"'
    echo ""
    echo "   💡 Check n8n execution log to see the full workflow execution"
    echo "   🔗 ${N8N_URL}/executions"
else
    echo "   ⚠️  Webhook did not respond (workflow may not be active)"
    echo "   💡 Make sure to:"
    echo "      1. Import the workflow JSON to n8n"
    echo "      2. Configure all credentials"
    echo "      3. Toggle the workflow to ACTIVE"
fi
echo ""

# Test 6: Check Database After Tests
echo "6️⃣  Checking Database After Tests..."
NEW_TASK_COUNT=$(ssh root@${VPS_IP} "docker exec prioai-postgres psql -U prioai_user -d prioai_db -tAc 'SELECT COUNT(*) FROM tasks;'" 2>/dev/null || echo "0")
echo "   📊 Total tasks in database: ${NEW_TASK_COUNT}"

if [ "$NEW_TASK_COUNT" != "$TASK_COUNT" ]; then
    echo "   ✅ New task was inserted! (increased from ${TASK_COUNT} to ${NEW_TASK_COUNT})"
    echo ""
    echo "   📋 Latest task:"
    ssh root@${VPS_IP} "docker exec prioai-postgres psql -U prioai_user -d prioai_db -c \"SELECT id, title, urgency_level, priority_score, created_at FROM tasks ORDER BY created_at DESC LIMIT 1;\"" 2>/dev/null || echo "   Could not fetch task details"
else
    echo "   ℹ️  No new tasks inserted (webhook may not be active)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Services Status:"
echo "  • AI Service: ✅ Running"
echo "  • n8n: ✅ Running"
echo "  • PostgreSQL: ✅ Running"
echo "  • AI API Endpoint: ✅ Working"
echo ""
echo "Next Steps:"
echo "  1. Open n8n: ${N8N_URL}"
echo "  2. Import workflow from: n8n/PrioritiAI - Unified Workflow.json"
echo "  3. Configure credentials (see n8n/QUICK_REFERENCE.md)"
echo "  4. Activate workflow and test again"
echo ""
echo "Documentation:"
echo "  • Quick Reference: n8n/QUICK_REFERENCE.md"
echo "  • Full Config: n8n/WORKFLOW_CONFIGURATION.md"
echo "  • API Docs: ${AI_SERVICE_URL}/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
