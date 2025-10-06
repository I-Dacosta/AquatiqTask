# PrioritiAI Workflow - Quick Reference Card

## 🚀 Essential URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **n8n Dashboard** | http://31.97.38.31:5678 | Workflow management |
| **AI Service Docs** | http://31.97.38.31:8000/docs | API documentation |
| **AI Health Check** | http://31.97.38.31:8000/health | Service status |
| **Production Webhook** | http://31.97.38.31:5678/webhook/prioai-tasks | Task creation API |
| **Test Webhook** | http://31.97.38.31:5678/webhook-test/prioai-tasks | Testing endpoint |
| **Frontend** | http://31.97.38.31:3000 | Dashboard (when deployed) |

## 🔐 Required Credentials in n8n

### 1. PostgreSQL (`PG PrioAI`)
```
Host: postgres
Port: 5432
Database: prioai_db
User: prioai_user
Password: [Get from VPS .env]
SSL: disable
```

**Get password**: 
```bash
ssh root@31.97.38.31 "grep DB_PASSWORD /opt/TaskPriority/.env"
```

### 2. Microsoft Outlook OAuth2 (`M365 OAuth2`)
- **Redirect URI**: `http://31.97.38.31:5678/rest/oauth2-credential/callback`
- **Permissions**: Mail.Read, Mail.ReadWrite, offline_access
- **Azure Portal**: https://portal.azure.com → App registrations

### 3. Microsoft Teams OAuth2 (`Teams OAuth2`)
- **Redirect URI**: `http://31.97.38.31:5678/rest/oauth2-credential/callback`
- **Permissions**: ChannelMessage.Read.All, Group.Read.All, Tasks.ReadWrite, offline_access

## 📊 API Response Format (v2.0)

### AI Service Response
```json
{
  "request_id": "task_1696598400_123",
  "urgency_level": "HIGH",          // CRITICAL | HIGH | MEDIUM | LOW
  "priority_metrics": {
    "final_priority_score": 7.8,    // 0-10 scale
    "urgency_score": 8.5,
    "business_impact_score": 7.2,
    "risk_score": 6.8,
    "role_weight": 3.0,
    "time_sensitivity_score": 8.0,
    "effort_complexity_score": 4.5
  },
  "reasoning": "High priority due to...",
  "suggested_sla_hours": 4.0,
  "ai_confidence": 0.89
}
```

## 🧪 Quick Tests

### Test AI Service
```bash
curl http://31.97.38.31:8000/health
# Expected: {"status":"healthy", "service":"PrioritiAI Engine", "version":"2.0.0"}
```

### Test Webhook (with workflow active)
```bash
curl -X POST http://31.97.38.31:5678/webhook/prioai-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "description": "Server not responding",
    "requester": "test@company.com"
  }'
# Expected: {"status":"accepted","message":"Oppgave mottatt for AI-behandling"}
```

### Test Database Connection
```bash
ssh root@31.97.38.31
docker exec -it prioai-postgres psql -U prioai_user -d prioai_db -c "SELECT COUNT(*) FROM tasks;"
```

## 🔄 Workflow Pipeline

```
📧 Outlook Email ──┐
                   ├──→ Normalize ──→ Build Payload ──→ Call AI ──→ IF Is Task? ──→ Insert DB ──→ Notify
📱 Teams Message ──┤                                                      ↓
                   │                                                   (Teams notification)
🔗 Webhook API ────┘                                                      ↓
                                                                      (Planner task)
```

## 📝 Database Field Mapping

| Database Column | Source | Example |
|----------------|--------|---------|
| `title` | AI response: `request_id` | "task_1696598400_123" |
| `description` | Original content | "Server is down..." |
| `priority_score` | AI: `final_priority_score` | 7.8 |
| `urgency_level` | AI: `urgency_level` | "HIGH" |
| `reasoning` | AI: `reasoning` | "High priority because..." |
| `due_at` | NOW() + `suggested_sla_hours` | NOW() + 4 hours |
| `est_minutes` | `effort_complexity_score * 60` | 270 minutes |

## ⚙️ Optional Environment Variables

Add in n8n → Settings → Environments:

```env
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
TEAMS_PLAN_ID=your-microsoft-planner-plan-id
TEAMS_BUCKET_ID=your-planner-bucket-id
```

## 🐛 Troubleshooting Commands

### Check Service Health
```bash
ssh root@31.97.38.31 'docker compose -f /opt/TaskPriority/docker-compose-ip.yml ps'
```

### View AI Service Logs
```bash
ssh root@31.97.38.31 'docker logs prioai-ai-service --tail 50 -f'
```

### View n8n Logs
```bash
ssh root@31.97.38.31 'docker logs prioai-n8n --tail 50 -f'
```

### View PostgreSQL Logs
```bash
ssh root@31.97.38.31 'docker logs prioai-postgres --tail 50 -f'
```

### Restart Services
```bash
ssh root@31.97.38.31 'cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml restart'
```

## 📋 Setup Checklist

- [ ] Import workflow JSON to n8n
- [ ] Add PostgreSQL credential (`PG PrioAI`)
- [ ] Create Azure App Registration
- [ ] Add Outlook OAuth2 credential (`M365 OAuth2`)
- [ ] Add Teams OAuth2 credential (`Teams OAuth2`)
- [ ] Test webhook endpoint
- [ ] Activate workflow
- [ ] Send test email to trigger
- [ ] Verify task inserted in database
- [ ] (Optional) Configure Teams webhook
- [ ] (Optional) Set up Planner integration

## 🔗 Documentation Links

- **Full Configuration Guide**: `n8n/WORKFLOW_CONFIGURATION.md`
- **Import Guide**: `n8n/IMPORT_GUIDE.md`
- **Deployment Docs**: `docs/DEPLOYMENT_IP_ONLY.md`
- **GitHub Actions**: `.github/SETUP_SECRETS.md`

---

**Need Help?** Check `WORKFLOW_CONFIGURATION.md` for detailed troubleshooting and configuration steps.
