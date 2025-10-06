# PrioritiAI n8n Workflow Documentation

Complete documentation suite for the PrioritiAI Unified Workflow v2.0 deployed on Hostinger VPS.

---

## 🚀 Quick Navigation

### New to PrioritiAI?
**Start Here** → [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (5 min read)
- Essential URLs and credentials
- Quick test commands
- Setup checklist

### Ready to Import?
**Step-by-Step** → [IMPORT_GUIDE.md](./IMPORT_GUIDE.md) (10 min read)
- Detailed import instructions
- Credential configuration
- Testing procedures

### Need Complete Understanding?
**Deep Dive** → [WORKFLOW_CONFIGURATION.md](./WORKFLOW_CONFIGURATION.md) (30 min read)
- Complete API documentation
- Database schema details
- Troubleshooting guide

### Want Visual Overview?
**Architecture** → [ARCHITECTURE.md](./ARCHITECTURE.md) (20 min read)
- System architecture diagrams
- Data flow visualizations
- Priority calculation logic

### Upgrading from v1.0?
**What Changed** → [CHANGES.md](./CHANGES.md) (15 min read)
- Before/after comparisons
- Migration guide
- New features overview

---

## 📦 Workflow Files

### **PrioritiAI - Unified Workflow.json**
The main workflow file to import into n8n.

**Version**: 2.0  
**AI Service**: v2.0.0  
**Features**:
- 📧 Outlook Email Trigger
- 📱 Teams Message Trigger
- 🔗 Webhook API Endpoint
- 🤖 AI-Powered Priority Classification
- 💾 PostgreSQL Storage
- 📬 Teams Notifications
- 📋 Microsoft Planner Integration

---

## 🎯 Key Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| **n8n** | http://31.97.38.31:5678 | Workflow dashboard |
| **AI Service** | http://31.97.38.31:8000 | Priority API |
| **API Docs** | http://31.97.38.31:8000/docs | Interactive docs |
| **Webhook** | http://31.97.38.31:5678/webhook/prioai-tasks | Task creation |

---

## 🧪 Quick Test

Run the automated test script:
```bash
./infra/deploy/test-deployment.sh
```

Or test webhook manually:
```bash
curl -X POST http://31.97.38.31:5678/webhook/prioai-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "description": "Server not responding",
    "requester": "test@company.com"
  }'
```

---

## 📚 Documentation Index

| Document | Purpose | Read Time | Best For |
|----------|---------|-----------|----------|
| **QUICK_REFERENCE.md** | Essential info & commands | 5 min | First-time setup |
| **IMPORT_GUIDE.md** | Step-by-step import | 10 min | Importing workflow |
| **WORKFLOW_CONFIGURATION.md** | Complete configuration | 30 min | Deep understanding |
| **ARCHITECTURE.md** | Visual diagrams | 20 min | System design |
| **CHANGES.md** | Version changelog | 15 min | Upgrading |

---

## 🔧 Requirements

- **n8n**: Version 1.0+ (deployed on VPS)
- **PostgreSQL**: 16+ with `prioai_db` database
- **AI Service**: PrioritiAI v2.0.0
- **Microsoft 365**: Azure App Registration with OAuth
- **OpenAI**: API key for GPT-4

---

## ⚡ Quick Setup (3 Steps)

1. **Import Workflow**
   ```
   n8n → Workflows → Import from File → PrioritiAI - Unified Workflow.json
   ```

2. **Configure Credentials**
   - PostgreSQL: `postgres:5432/prioai_db`
   - Microsoft OAuth: See [IMPORT_GUIDE.md](./IMPORT_GUIDE.md)

3. **Activate & Test**
   ```bash
   # Test webhook
   curl -X POST http://31.97.38.31:5678/webhook/prioai-tasks \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","description":"Test task","requester":"test@company.com"}'
   ```

---

## 🆘 Troubleshooting

### Services Not Responding?
```bash
ssh root@31.97.38.31 'docker compose -f /opt/TaskPriority/docker-compose-ip.yml ps'
```

### Check Logs
```bash
# AI Service
ssh root@31.97.38.31 'docker logs prioai-ai-service --tail 50'

# n8n
ssh root@31.97.38.31 'docker logs prioai-n8n --tail 50'
```

### Full Troubleshooting Guide
See [WORKFLOW_CONFIGURATION.md](./WORKFLOW_CONFIGURATION.md#troubleshooting)

---

## 🔄 Data Flow

```
📧 Email/Teams/API → Normalize → Build Payload → 
🤖 AI Classification → 💾 Database → 📬 Notifications
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed diagrams.

---

## 🎉 Ready to Start?

1. Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (5 min)
2. Follow [IMPORT_GUIDE.md](./IMPORT_GUIDE.md) (10 min)
3. Test with `./infra/deploy/test-deployment.sh` (1 min)

**Total setup time**: ~15-20 minutes

---

**Deployment**: Hostinger VPS 31.97.38.31  
**Version**: 2.0  
**Last Updated**: October 6, 2025  
**GitHub**: https://github.com/I-Dacosta/AquatiqTask
