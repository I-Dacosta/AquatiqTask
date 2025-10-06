# PrioritiAI Workflow Configuration Guide

## Overview
This document provides the complete configuration for the PrioritiAI Unified Workflow on your Hostinger VPS deployment.

## VPS Deployment Details
- **VPS IP**: 31.97.38.31
- **n8n URL**: http://31.97.38.31:5678
- **AI Service URL**: http://ai-prioritization:8000 (internal Docker network)
- **AI Service External**: http://31.97.38.31:8000
- **Frontend URL**: http://31.97.38.31:3000 (when frontend is deployed)
- **PostgreSQL**: postgres:5432 (internal Docker network)

## Updated Workflow Features

### 1. AI Service Integration
The workflow now correctly calls the PrioritiAI v2.0 API:

**Endpoint**: `http://ai-prioritization:8000/api/v1/prioritization/sync`

**Request Format** (TaskRequest):
```json
{
  "id": "task_1234567890_123",
  "title": "Task title",
  "description": "Full task description",
  "category": "SUPPORT",
  "requester_role": "EMPLOYEE",
  "requester_name": "User Name",
  "created_at": "2025-10-06T12:00:00Z",
  "estimated_effort_hours": 0.5,
  "context": "Additional context",
  "tags": ["channel-name"]
}
```

**Response Format** (AIPriorityResult):
```json
{
  "request_id": "task_1234567890_123",
  "urgency_level": "HIGH",
  "priority_metrics": {
    "urgency_score": 8.5,
    "business_impact_score": 7.2,
    "risk_score": 6.8,
    "role_weight": 3.0,
    "time_sensitivity_score": 8.0,
    "effort_complexity_score": 4.5,
    "final_priority_score": 7.8
  },
  "reasoning": "AI reasoning for priority",
  "ai_confidence": 0.89,
  "suggested_sla_hours": 4.0,
  "user_suggestions": [],
  "escalation_recommended": false,
  "workaround_suggestions": [],
  "next_actions": [],
  "risk_assessment": "Medium risk",
  "processed_at": "2025-10-06T12:00:01Z"
}
```

### 2. Database Schema
The workflow inserts into the `tasks` table in the `prioai_db` database:

**Table**: `tasks`
**Columns**:
- `id` (SERIAL PRIMARY KEY)
- `title` (TEXT) - Maps to `request_id` from AI response
- `description` (TEXT) - Original content from trigger
- `source` (VARCHAR) - 'outlook', 'teams', or 'manual'
- `source_ref` (TEXT) - Original message/email ID
- `requester` (VARCHAR) - Email address
- `role_hint` (VARCHAR) - User role from AI classification
- `due_at` (TIMESTAMP) - Calculated from `suggested_sla_hours`
- `est_minutes` (INTEGER) - From `effort_complexity_score * 60`
- `priority_score` (FLOAT) - From `final_priority_score`
- `urgency_level` (VARCHAR) - CRITICAL, HIGH, MEDIUM, LOW
- `reasoning` (TEXT) - AI reasoning
- `status` (VARCHAR) - Default 'incoming'
- `created_at` (TIMESTAMP) - NOW()

### 3. Webhook Configuration

**Production Webhook URL**: 
```
http://31.97.38.31:5678/webhook/prioai-tasks
```

**Test Webhook URL**:
```
http://31.97.38.31:5678/webhook-test/prioai-tasks
```

**Usage in Frontend** (.env):
```env
NEXT_PUBLIC_N8N_WEBHOOK_URL=http://31.97.38.31:5678/webhook/prioai-tasks
```

**Test with curl**:
```bash
curl -X POST http://31.97.38.31:5678/webhook/prioai-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task from API",
    "description": "This is a test task to verify webhook integration",
    "requester": "api@test.com",
    "est_minutes": 30,
    "due_text": "urgent",
    "role_hint": "employee"
  }'
```

## Required n8n Credentials

### 1. Microsoft Outlook OAuth2
**Name**: `M365 OAuth2`
**Credential Type**: Microsoft Outlook OAuth2 API

**Azure App Registration**:
- Go to: https://portal.azure.com
- Navigate to: App registrations → New registration
- Name: `PrioritiAI n8n Integration`
- Redirect URI: `http://31.97.38.31:5678/rest/oauth2-credential/callback`
- API Permissions:
  - `Mail.Read` (Delegated)
  - `Mail.ReadWrite` (Delegated)
  - `offline_access` (Delegated)

**In n8n**:
1. Go to Credentials → Add Credential
2. Select "Microsoft Outlook OAuth2 API"
3. Name: `M365 OAuth2`
4. Paste Client ID and Client Secret from Azure
5. Click "Connect my account"
6. Authorize access

### 2. Microsoft Teams OAuth2
**Name**: `Teams OAuth2`
**Credential Type**: Microsoft Teams OAuth2 API

**Azure App Registration** (same app or new):
- Redirect URI: `http://31.97.38.31:5678/rest/oauth2-credential/callback`
- API Permissions:
  - `ChannelMessage.Read.All` (Delegated)
  - `Group.Read.All` (Delegated)
  - `Tasks.ReadWrite` (Delegated)
  - `offline_access` (Delegated)

**In n8n**:
1. Go to Credentials → Add Credential
2. Select "Microsoft Teams OAuth2 API"
3. Name: `Teams OAuth2`
4. Paste Client ID and Client Secret
5. Click "Connect my account"
6. Authorize access

### 3. PostgreSQL Database
**Name**: `PG PrioAI`
**Credential Type**: Postgres

**Configuration**:
- Host: `postgres` (Docker network name)
- Port: `5432`
- Database: `prioai_db`
- User: `prioai_user`
- Password: Check `.env` file on VPS at `/opt/TaskPriority/.env`
- SSL Mode: `disable` (internal Docker network)

**Get Password**:
```bash
ssh root@31.97.38.31 "grep DB_PASSWORD /opt/TaskPriority/.env"
```

## Optional Environment Variables

Add these in n8n Settings → Environments:

```env
# Teams Incoming Webhook (for notifications)
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR-WEBHOOK-URL

# Microsoft Planner IDs (if using Planner integration)
TEAMS_PLAN_ID=your-plan-id
TEAMS_BUCKET_ID=your-bucket-id
```

**To get Teams Webhook URL**:
1. Go to your Teams channel
2. Click ⋯ → Connectors → Incoming Webhook
3. Name: `PrioritiAI Notifications`
4. Copy the webhook URL

**To get Planner IDs** (optional):
1. Open Microsoft Planner in browser
2. Navigate to your plan
3. Plan ID is in the URL: `https://tasks.office.com/.../{planId}/...`
4. Bucket ID: Use Graph Explorer or n8n "Microsoft Teams: Get Buckets" node

## Workflow Nodes Overview

### Triggers (3 sources)
1. **Outlook Email Trigger**: Monitors inbox for new emails
2. **Teams Message Trigger**: Listens for channel messages
3. **Webhook Create Task**: Manual task creation via API

### Processing Pipeline
1. **Normalize Input Data**: Converts all trigger formats to standard structure
2. **Build PrioritiAI Payload**: Creates TaskRequest format for AI service
3. **Call PrioritiAI**: POST to `/api/v1/prioritization/sync`
4. **IF Is Task**: Checks if AI classified it as a task (`urgency_level` not empty)
5. **Insert Task**: Saves to PostgreSQL database
6. **Notify New Task**: Sends Teams notification (if webhook configured)
7. **Create in Planner**: Creates task in Microsoft Planner (if IDs configured)

## Field Mapping Reference

### Trigger → Normalized Data
```javascript
{
  title: "Email subject" | "Teams: Message preview",
  content: "Email body" | "Teams message content",
  sender: "email@address.com",
  sender_name: "Display Name",
  source: "outlook" | "teams" | "manual",
  source_ref: "message-id",
  raw_data: "{...}"
}
```

### Normalized → AI Request
```javascript
{
  id: "task_" + timestamp + "_" + random,
  title: normalized.title,
  description: normalized.content,
  category: "SUPPORT",
  requester_role: "MANAGER" | "EMPLOYEE",
  requester_name: normalized.sender_name,
  created_at: "ISO timestamp",
  tags: [channel_name]
}
```

### AI Response → Database
```javascript
{
  title: ai_response.request_id,
  description: normalized.content,
  priority_score: ai_response.priority_metrics.final_priority_score,
  urgency_level: ai_response.urgency_level,
  reasoning: ai_response.reasoning,
  due_at: NOW() + (suggested_sla_hours * 60 minutes),
  est_minutes: effort_complexity_score * 60
}
```

## Testing the Workflow

### 1. Test AI Service Directly
```bash
ssh root@31.97.38.31
curl -X POST http://localhost:8000/api/v1/prioritization/sync \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "title": "Server ikke tilgjengelig",
    "description": "Produksjonsserver svarer ikke. Brukere kan ikke logge inn.",
    "category": "INFRASTRUCTURE",
    "requester_role": "IT_ADMIN",
    "requester_name": "John Doe",
    "created_at": "2025-10-06T12:00:00Z"
  }'
```

### 2. Test Webhook Endpoint
```bash
curl -X POST http://31.97.38.31:5678/webhook-test/prioai-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Webhook test task",
    "description": "Testing the webhook integration",
    "requester": "test@aquatiq.no"
  }'
```

### 3. Test in n8n Interface
1. Open workflow in n8n
2. Click on "Webhook Create Task" node
3. Click "Listen for test event"
4. Send POST request (see above)
5. Verify data flows through all nodes

### 4. Test Email Trigger
1. Ensure Outlook OAuth2 credentials are configured
2. Activate the workflow
3. Send email to the configured inbox
4. Check n8n execution log

## Troubleshooting

### AI Service Returns Error
**Check logs**:
```bash
ssh root@31.97.38.31
docker logs prioai-ai-service --tail 50
```

**Verify OpenAI API key**:
```bash
ssh root@31.97.38.31 "grep OPENAI_API_KEY /opt/TaskPriority/.env"
```

### Database Insert Fails
**Check database exists**:
```bash
ssh root@31.97.38.31
docker exec -it prioai-postgres psql -U prioai_user -d prioai_db -c "\dt"
```

**Check table schema**:
```bash
docker exec -it prioai-postgres psql -U prioai_user -d prioai_db -c "\d tasks"
```

### Webhook Not Responding
**Check n8n is running**:
```bash
curl http://31.97.38.31:5678/healthz
```

**Check workflow is active**:
- Open n8n UI
- Verify workflow toggle is ON
- Check webhook node has green indicator

### OAuth Connection Issues
**Check redirect URI**:
- Must be exactly: `http://31.97.38.31:5678/rest/oauth2-credential/callback`
- No trailing slash
- HTTP not HTTPS (for IP-only deployment)

**Re-authorize credentials**:
1. Go to Credentials in n8n
2. Open the credential
3. Click "Reconnect"
4. Complete OAuth flow again

## Performance Optimization

### 1. AI Service Response Time
- Typical: 2-5 seconds
- Timeout set to: 30 seconds
- If slower, check OpenAI API status

### 2. Database Connection Pooling
n8n maintains persistent connections to PostgreSQL. No additional configuration needed.

### 3. Webhook Timeout
Webhook responds immediately (202 Accepted) and processes async. Frontend sees instant response.

## Security Considerations

### 1. API Keys
- OpenAI API key stored in VPS .env file
- Not exposed in workflow
- Rotate regularly via Azure Key Vault (future enhancement)

### 2. Webhook Authentication
Currently public. To add authentication:
```javascript
// In Webhook node → Header Auth
Authorization: Bearer YOUR-SECRET-TOKEN
```

### 3. Database Access
- PostgreSQL only exposed on localhost
- Not accessible from outside VPS
- n8n connects via internal Docker network

## Next Steps

1. ✅ Import workflow to n8n
2. ✅ Configure PostgreSQL credentials
3. ⏳ Set up Microsoft OAuth credentials
4. ⏳ Test webhook endpoint
5. ⏳ Test email trigger
6. ⏳ Configure Teams notifications (optional)
7. ⏳ Set up Planner integration (optional)
8. ⏳ Deploy frontend and test full stack

## Support & Documentation

- **n8n Docs**: https://docs.n8n.io
- **PrioritiAI API**: http://31.97.38.31:8000/docs
- **AI Service Health**: http://31.97.38.31:8000/health
- **VPS Deployment Guide**: `docs/DEPLOYMENT_IP_ONLY.md`
- **GitHub Actions Setup**: `.github/SETUP_SECRETS.md`
