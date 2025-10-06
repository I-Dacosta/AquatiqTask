# PrioritiAI - n8n Workflow Import Guide

## 📋 Available Workflows

### 1. **PrioritiAI - Outlook til Oppgave.json** (Traditional)
Classic workflow with manual AI service integration
- **Nodes:** 6
- **Features:** Email trigger → IF filter → Code preprocessing → HTTP AI classify → Postgres insert → Teams notification
- **Use case:** Legacy approach with FastAPI AI service at `http://ai:8080/classify`

### 2. **PrioritiAI - AI Agent Email Classifier.json** (AI-Powered) ⭐ **RECOMMENDED**
Modern AI Agent workflow with LangChain integration
- **Nodes:** 7
- **Features:** Email trigger → AI Agent (GPT-4o-mini) → Structured parser → IF filter → Postgres insert → Teams notification
- **Use case:** Intelligent email classification with natural language reasoning
- **Benefits:** 
  - More accurate priority scoring
  - Natural language explanations
  - Adaptive learning from context
  - No external AI service needed

### 3. **PrioritiAI - Manuell oppgave (Webhook).json**
POST webhook for manual task creation
- **Endpoint:** `http://localhost:5678/webhook/prioai/tasks`
- **Method:** POST
- **Body:** `{ title, description, requester, role_hint, due_text, est_minutes }`

### 4. **PrioritiAI - Oppdater status (Webhook).json**
PATCH webhook for task status updates
- **Endpoint:** `http://localhost:5678/webhook/prioai/tasks/:id`
- **Method:** PATCH
- **Body:** `{ status, override_priority, override_locked }`

---

## 🚀 Quick Start

### Prerequisites
- ✅ Docker containers running: `docker compose up -d`
- ✅ PostgreSQL database initialized (prioai_task table)
- ✅ AI service running on `http://ai:8080` (for traditional workflow)
- ✅ n8n accessible at `http://localhost:5678`

### Step 1: Import Workflows

1. Open n8n: **http://localhost:5678**
2. Navigate to **Workflows** (left sidebar)
3. Click **Add workflow** → **Import from File**
4. Select workflow JSON files from `n8n/` directory
5. Repeat for each workflow

**Import order (recommended):**
1. AI Agent Email Classifier (main)
2. Manuell oppgave (Webhook)
3. Oppdater status (Webhook)
4. Outlook til Oppgave (optional/backup)

---

## 🔐 Credentials Configuration

### Required Credentials

#### 1. **Microsoft 365 OAuth2** (for Outlook trigger)
- **Name:** `M365 OAuth2`
- **Type:** Microsoft Outlook OAuth2 API
- **Setup:**
  1. Go to **Azure Portal** → **App registrations**
  2. Create new app or use existing
  3. Add **Redirect URI:** `http://localhost:5678/rest/oauth2-credential/callback`
  4. **API permissions:** 
     - `Mail.Read` (Delegated)
     - `User.Read` (Delegated)
     - `offline_access` (Delegated)
  5. Create **Client Secret**
  6. Copy **Application (client) ID** and **Client secret** to n8n
  7. Click **Connect my account** and authorize

#### 2. **PostgreSQL** (for database operations)
- **Name:** `PG PrioAI`
- **Type:** Postgres
- **Configuration:**
  ```
  Host: postgres (or localhost if running n8n outside Docker)
  Database: prioai
  User: prioai
  Password: prioai123
  Port: 5432
  SSL: Disabled
  ```

#### 3. **OpenAI API** (for AI Agent workflow only)
- **Name:** `OpenAI API`
- **Type:** OpenAI
- **Configuration:**
  ```
  API Key: sk-... (your OpenAI API key)
  ```
- **Get API Key:** https://platform.openai.com/api-keys
- **Model used:** `gpt-4o-mini` (cost-effective, fast)

---

## ⚙️ Environment Variables

Add to your `.env` file or n8n environment:

```bash
# Teams Webhook (optional - for notifications)
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# OpenAI API (required for AI Agent workflow)
OPENAI_API_KEY=sk-...

# n8n Configuration
N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
GENERIC_TIMEZONE=Europe/Oslo
```

To add environment variables in n8n:
1. Settings → Environment Variables
2. Add each variable manually, or
3. Restart n8n with updated `.env`

---

## 🧪 Testing Workflows

### Test AI Agent Workflow

1. **Activate workflow:**
   - Open "PrioritiAI - AI Agent Email Classifier"
   - Toggle **Active** (top right)

2. **Send test email to your configured Outlook:**
   ```
   Subject: #oppgave Webshop feil må fixes før møte i dag kl 14:00
   Body: CFO har rapportert at checkout-siden crasher. Dette må prioriteres høyt.
   ```

3. **Check execution:**
   - n8n: Executions tab
   - Database: `SELECT * FROM prioai_task ORDER BY created_at DESC LIMIT 1;`
   - Frontend: http://localhost:3000

### Test Manual Webhook

```bash
curl -X POST http://localhost:5678/webhook/prioai/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test oppgave fra webhook",
    "description": "Dette er en test",
    "requester": "test@example.com",
    "role_hint": "Developer",
    "est_minutes": 30
  }'
```

### Test Status Update Webhook

```bash
# Get task ID from database first
TASK_ID="..." # UUID from prioai_task table

curl -X PATCH http://localhost:5678/webhook/prioai/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "override_priority": 95
  }'
```

---

## 🎯 AI Agent vs Traditional Workflow

| Feature | AI Agent | Traditional |
|---------|----------|-------------|
| **Intelligence** | GPT-4o-mini LLM | Heuristics + regex |
| **Priority Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Natural Language** | ✅ Full understanding | ❌ Keyword matching |
| **Reasoning** | ✅ Explains decisions | ⚠️ Basic scoring |
| **Adaptability** | ✅ Learns from context | ❌ Fixed rules |
| **Cost** | ~$0.0001/email | Free (self-hosted) |
| **Latency** | 2-5 seconds | <1 second |
| **Dependencies** | OpenAI API key | FastAPI service |

**Recommendation:** Start with **AI Agent** for best results. Fall back to **Traditional** if API costs are a concern or you need sub-second response times.

---

## 🔧 Troubleshooting

### Workflow doesn't trigger from Outlook
- ✅ Check credentials are authorized
- ✅ Verify workflow is **Active**
- ✅ Check Outlook account has Mail.Read permission
- ✅ Test with n8n's "Test Workflow" button

### AI Agent returns errors
- ✅ Verify OpenAI API key is valid
- ✅ Check OpenAI account has credits
- ✅ Ensure `gpt-4o-mini` model is available
- ✅ Review execution log for specific error message

### Database connection fails
- ✅ Verify PostgreSQL is running: `docker compose ps postgres`
- ✅ Check database exists: `docker compose exec postgres psql -U prioai -d prioai -c "\dt"`
- ✅ Test connection from n8n: Use "Test" button in credentials
- ✅ Verify network: If n8n is outside Docker, use `localhost:5432` instead of `postgres:5432`

### Webhook returns 404
- ✅ Activate workflow first (webhooks need active workflows)
- ✅ Check URL matches workflow webhook path
- ✅ Verify HTTP method (POST vs PATCH)
- ✅ Look for webhook URL in workflow execution settings

---

## 📊 Monitoring

### n8n Dashboard
- **Executions:** View all workflow runs
- **Errors:** Filter by failed executions
- **Performance:** Check execution duration

### Database Queries

```sql
-- Recent tasks
SELECT id, title, ai_score, status, created_at 
FROM prioai_task 
ORDER BY created_at DESC LIMIT 10;

-- High priority tasks
SELECT id, title, ai_score, due_at 
FROM prioai_task 
WHERE status = 'incoming' AND ai_score > 80 
ORDER BY ai_score DESC;

-- Tasks by source
SELECT source, COUNT(*) as count, AVG(ai_score) as avg_score
FROM prioai_task
GROUP BY source;
```

### Frontend Dashboard
- **Innkommende:** http://localhost:3000
- **Godkjente:** Status tab
- **Pågående:** Status tab

---

## 🚀 Next Steps

1. **Customize AI Agent prompts** to match your organization's priorities
2. **Add more tools** to AI Agent (Slack, Google Calendar, etc.)
3. **Create dashboards** in n8n for monitoring
4. **Set up error workflows** for handling failures
5. **Configure backup workflows** with fallback models

---

## 📚 Resources

- **n8n Documentation:** https://docs.n8n.io/
- **AI Agent Tutorial:** https://docs.n8n.io/advanced-ai/intro-tutorial/
- **LangChain Nodes:** https://docs.n8n.io/integrations/langchain/
- **OpenAI API:** https://platform.openai.com/docs/

---

## ✅ Success Checklist

- [ ] All 4 workflows imported
- [ ] M365 OAuth2 credentials configured and authorized
- [ ] PostgreSQL credentials tested
- [ ] OpenAI API key added (for AI Agent)
- [ ] TEAMS_WEBHOOK_URL environment variable set (optional)
- [ ] AI Agent workflow activated
- [ ] Test email sent and processed successfully
- [ ] Task appears in database and frontend
- [ ] Teams notification received (if configured)

**Your PrioritiAI n8n setup is complete! 🎉**
