# PrioritiAI n8n Workflow

Complete unified n8n automation workflow for the PrioritiAI task prioritization system.

## 📋 Unified Workflow

**File:** `PrioritiAI - Unified Workflow.json`

All-in-one intelligent workflow combining AI-powered email classification, manual task creation, and status updates.

**Features:**
- 🤖 AI Agent Email Classification (OpenAI GPT-4o-mini)
- ✍️ Manual Task Creation (Webhook API)
- 🔄 Status Updates (Webhook API)
- 📊 Intelligent Priority Scoring
- 📢 Teams Notifications (Adaptive Cards)

---

## 🚀 Quick Start

1. **Import:** n8n → Settings → Import from File → `PrioritiAI - Unified Workflow.json`
2. **Configure Credentials:** M365 OAuth2, PostgreSQL, OpenAI API
3. **Set Environment Variable:** `TEAMS_WEBHOOK_URL`
4. **Activate Workflow**
5. **Test:** Send email or POST to webhook

**Test Webhook:**
```bash
curl -X POST http://localhost:5678/webhook/prioai/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Testing","requester":"test@example.com"}'
```

---

## 📦 Requirements

- M365 OAuth2 (Outlook)
- PostgreSQL (prioai database)
- OpenAI API (GPT-4o-mini)
- Teams Webhook URL

See [IMPORT_GUIDE.md](./IMPORT_GUIDE.md) for detailed setup.
