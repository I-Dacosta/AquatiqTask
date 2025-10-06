# Workflow Update Summary - What Changed

## 🔄 Changes Made to n8n Workflow

### 1. AI Service HTTP Request Node (`Call PrioritiAI`)

**BEFORE:**
```json
{
  "url": "={{ ($env.AI_SERVICE_URL || 'http://ai-prioritization:8000') + '/api/v1/prioritization/sync' }}",
  "options": {}
}
```

**AFTER:**
```json
{
  "url": "http://ai-prioritization:8000/api/v1/prioritization/sync",
  "options": {
    "timeout": 30000
  }
}
```

**Why?** Hardcoded correct endpoint, added timeout for stability.

---

### 2. IF Condition Node (`IF Is Task`)

**BEFORE:**
```json
{
  "conditions": [{
    "leftValue": "={{ $json.is_task }}",
    "rightValue": "yes",
    "operator": "equals"
  }]
}
```

**AFTER:**
```json
{
  "conditions": [{
    "leftValue": "={{ $json.urgency_level }}",
    "rightValue": "",
    "operator": "notEmpty"
  }]
}
```

**Why?** AI service v2.0 returns `urgency_level` (CRITICAL/HIGH/MEDIUM/LOW), not `is_task`.

---

### 3. PostgreSQL Insert Node (`Insert Task`)

**BEFORE:**
```sql
INSERT INTO prioai_task (
  title, description, source, source_ref, requester, role_hint, due_at,
  est_minutes, value_score, risk_score, role_score, haste_score,
  ai_score, ai_reason, status
) VALUES (
  '{{ $json.task_title }}',
  '{{ $json.task_description }}',
  ...
  {{ $json.priority_score }},
  '{{ $json.priority_reasoning }}',
  'incoming'
)
```

**AFTER:**
```sql
INSERT INTO tasks (
  title, description, source, source_ref, requester, role_hint, due_at,
  est_minutes, priority_score, urgency_level, reasoning, status, created_at
) VALUES (
  '{{ $json.request_id }}',
  '{{ $('Normalize Input Data').item.json.content }}',
  ...
  {{ $json.priority_metrics.final_priority_score }},
  '{{ $json.urgency_level }}',
  '{{ $json.reasoning }}',
  'incoming',
  NOW()
)
```

**Why?** 
- Table name changed: `prioai_task` → `tasks`
- Field mapping updated to match AI v2.0 response:
  - `task_title` → `request_id`
  - `task_description` → original `content`
  - `priority_score` → `priority_metrics.final_priority_score`
  - `priority_reasoning` → `reasoning`
  - Added `urgency_level` field
  - Removed separate score fields, using unified score
  - Added `created_at` with NOW()

---

### 4. Teams Notification Node (`Notify New Task`)

**BEFORE:**
```json
{
  "body": [
    { "title": "AI Score:", "value": "{{ $('Call PrioritiAI').item.json.priority_score }}" },
    { "title": "Estimert tid:", "value": "{{ $('Call PrioritiAI').item.json.estimated_minutes }} min" },
    { "title": "Frist:", "value": "{{ $('Call PrioritiAI').item.json.due_date || '-' }}" }
  ],
  "actions": [
    { "url": "http://localhost:3000/task/{{ $json.id }}" }
  ]
}
```

**AFTER:**
```json
{
  "body": [
    { "title": "Prioritet:", "value": "{{ Math.round($('Call PrioritiAI').item.json.priority_metrics.final_priority_score * 10) }}/100" },
    { "title": "Hastegrad:", "value": "{{ $('Call PrioritiAI').item.json.urgency_level }}" },
    { "title": "Estimert SLA:", "value": "{{ Math.round($('Call PrioritiAI').item.json.suggested_sla_hours) }} timer" }
  ],
  "actions": [
    { "url": "http://31.97.38.31:3000/task/{{ $json.id }}" }
  ]
}
```

**Why?**
- Updated to use v2.0 response fields
- Changed score scale: 0-10 → 0-100 for display
- Added urgency level display
- Changed "Estimert tid" to "Estimert SLA" (suggested_sla_hours)
- Updated frontend URL: localhost → VPS IP (31.97.38.31:3000)

---

### 5. Planner Task Node (`Create in Planner`)

**BEFORE:**
```json
{
  "title": "={{ $('Call PrioritiAI').item.json.task_title }}",
  "additionalFields": {
    "notes": "AI Priority Score: {{ $('Call PrioritiAI').item.json.priority_score }}",
    "dueDateTime": "={{ $('Call PrioritiAI').item.json.due_date ? new Date(...).toISOString() : null }}",
    "priority": "={{ $('Call PrioritiAI').item.json.priority_score >= 80 ? 'urgent' : ... }}"
  }
}
```

**AFTER:**
```json
{
  "title": "={{ $('Call PrioritiAI').item.json.request_id }}",
  "additionalFields": {
    "notes": "AI Priority Score: {{ Math.round($('Call PrioritiAI').item.json.priority_metrics.final_priority_score * 10) }}/100\nHastegrad: {{ $('Call PrioritiAI').item.json.urgency_level }}",
    "dueDateTime": "={{ $('Call PrioritiAI').item.json.suggested_sla_hours ? new Date(Date.now() + ... * 3600000).toISOString() : null }}",
    "priority": "={{ $('Call PrioritiAI').item.json.urgency_level === 'CRITICAL' ? 'urgent' : ... }}"
  }
}
```

**Why?**
- Title now uses `request_id` from AI response
- Priority mapping based on `urgency_level` enum instead of numeric score
- Due date calculated from `suggested_sla_hours` (relative to NOW)
- Enhanced notes with urgency level and reasoning

---

### 6. Webhook Node (`Webhook Create Task`)

**BEFORE:**
```json
{
  "path": "prioai/tasks",
  "responseData": "={{ { \"status\": \"accepted\", \"message\": \"Oppgave mottatt\" } }}"
}
```

**AFTER:**
```json
{
  "path": "prioai-tasks",
  "responseData": "={{ { \"status\": \"accepted\", \"message\": \"Oppgave mottatt for AI-behandling\" } }}",
  "webhookId": "prioai-webhook"
}
```

**Why?**
- Changed path separator: slash → hyphen for URL clarity
- Enhanced response message
- Added explicit webhookId for consistency

---

## 📊 API Response Comparison

### Old API Response (v1.0 - Legacy)
```json
{
  "task_title": "Server down",
  "task_description": "Production server not responding",
  "priority_score": 85,
  "estimated_minutes": 120,
  "due_date": "2025-10-06T16:00:00Z",
  "priority_reasoning": "High priority because...",
  "is_task": "yes"
}
```

### New API Response (v2.0 - Current)
```json
{
  "request_id": "task_1696598400_123",
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
  "reasoning": "High priority due to production impact...",
  "ai_confidence": 0.89,
  "suggested_sla_hours": 4.0,
  "user_suggestions": [],
  "escalation_recommended": false,
  "workaround_suggestions": [],
  "next_actions": ["Restart server", "Check logs"],
  "risk_assessment": "High risk of revenue loss",
  "processed_at": "2025-10-06T12:00:01Z"
}
```

**Key Differences:**
1. `is_task` → `urgency_level` (enum: CRITICAL/HIGH/MEDIUM/LOW)
2. Single `priority_score` → Detailed `priority_metrics` object
3. `estimated_minutes` → `effort_complexity_score` (0-10 scale, convert with * 60)
4. `due_date` → `suggested_sla_hours` (relative hours, not absolute timestamp)
5. `priority_reasoning` → `reasoning`
6. Added: `ai_confidence`, `user_suggestions`, `escalation_recommended`, `next_actions`, `risk_assessment`

---

## 🗄️ Database Schema Comparison

### Old Schema (`prioai_task`)
```sql
CREATE TABLE prioai_task (
  id SERIAL PRIMARY KEY,
  title TEXT,
  description TEXT,
  value_score INT,
  risk_score INT,
  role_score INT,
  haste_score INT,
  ai_score INT,
  ai_reason TEXT,
  status VARCHAR(50)
);
```

### New Schema (`tasks`)
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title TEXT,
  description TEXT,
  source VARCHAR(50),
  source_ref TEXT,
  requester VARCHAR(255),
  role_hint VARCHAR(50),
  due_at TIMESTAMP,
  est_minutes INTEGER,
  priority_score FLOAT,
  urgency_level VARCHAR(20),
  reasoning TEXT,
  status VARCHAR(50),
  created_at TIMESTAMP
);
```

**Key Differences:**
1. Simplified scoring: Multiple scores → Single `priority_score`
2. Added `urgency_level` for categorical priority
3. Added `source`, `source_ref`, `requester` for traceability
4. Added `role_hint` for role-based prioritization
5. Added `created_at` timestamp
6. `ai_reason` → `reasoning`

---

## 🔗 URL Changes

| Component | Old | New |
|-----------|-----|-----|
| **n8n** | http://localhost:5678 | http://31.97.38.31:5678 |
| **AI Service (Internal)** | http://ai-prioritization:8000 | http://ai-prioritization:8000 *(no change)* |
| **AI Service (External)** | http://localhost:8000 | http://31.97.38.31:8000 |
| **Frontend** | http://localhost:3000 | http://31.97.38.31:3000 |
| **Webhook** | /webhook/prioai/tasks | /webhook/prioai-tasks |
| **PostgreSQL** | postgres:5432 | postgres:5432 *(no change)* |

---

## ✅ Summary of Benefits

1. **Accurate Data Mapping**: All fields now match the actual API v2.0 response
2. **Better Error Handling**: 30-second timeout prevents hanging requests
3. **Correct Database Schema**: Inserts work without SQL errors
4. **Production URLs**: Frontend links point to VPS IP, not localhost
5. **Enhanced Metadata**: More detailed priority information stored
6. **Cleaner Webhook Path**: Hyphenated path more URL-friendly
7. **Proper Validation**: Checks `urgency_level` which always exists in AI response

---

## 🧪 Testing Validation

Before deploying to production, verify:
- ✅ AI Service returns expected v2.0 format
- ✅ Database INSERT succeeds without errors
- ✅ Webhook responds with 202 status
- ✅ Teams notification shows correct data
- ✅ Planner task creates successfully
- ✅ Frontend links work (when deployed)

**Test command:**
```bash
./infra/deploy/test-deployment.sh
```

---

## 📚 Documentation Updated

All documentation now reflects v2.0 changes:
- ✅ `n8n/WORKFLOW_CONFIGURATION.md` - Complete API examples
- ✅ `n8n/QUICK_REFERENCE.md` - Updated endpoints
- ✅ `n8n/ARCHITECTURE.md` - Updated diagrams
- ✅ `n8n/IMPORT_GUIDE.md` - Matches current workflow

---

**Last Updated**: October 6, 2025  
**Workflow Version**: 2.0  
**AI Service Version**: 2.0.0  
**Deployment**: VPS 31.97.38.31
