# Frontend PostgreSQL Integration - Summary

## ✅ Completed Tasks

### 1. PostgreSQL Operations Module
**File**: `frontend/src/lib/postgres-tasks.ts`

Created comprehensive module with:
- `getTasks(filters)` - Retrieve tasks with filtering by status, source, urgency, priority, search
- `getTask(id)` - Fetch individual task
- `updateTaskStatus(id, status)` - Update task status
- `updateTaskPriority(id, overridePriority, overrideLocked)` - Manual priority overrides
- `deleteTask(id)` - Delete task
- `getTaskStats()` - Dashboard statistics

**Field Mappings**:
- Database `priority_score` (0-10) → UI `aiScore` (0-100)
- Database `urgency_level` → UI `priority` (CRITICAL→urgent, HIGH→high, etc.)
- Database `incoming` → UI `inbox`
- Database `in_progress` → UI `in-progress`

### 2. API Routes Updated
**Files Modified**:
- `frontend/src/app/api/tasks/route.ts`
- `frontend/src/app/api/tasks/[id]/route.ts`

**Changes**:
- Removed Supabase dependencies
- Removed mock data fallback
- Integrated `postgres-tasks.ts` operations
- POST requests forward to n8n webhook for AI processing
- All operations now use direct PostgreSQL

### 3. Environment Configuration
**Files Created/Updated**:
- `frontend/.env.example` - Template with all required variables
- `frontend/.env.production` - Production config (local only, not in git)
- `.gitignore` - Added `.env.production` to prevent secret leaks

**Variables Configured**:
```env
DATABASE_URL=postgresql://prioai_user:password@postgres:5432/prioai_db
N8N_WEBHOOK_URL=http://31.97.38.31:5678/webhook/prioai-tasks
AI_SERVICE_URL=http://ai-prioritization:8000
NEXT_PUBLIC_API_URL=http://31.97.38.31:3000
```

### 4. Docker Integration
**File**: `docker-compose-prod.yml`

Added frontend service with:
- Traefik labels for HTTPS routing (`tasks.${DOMAIN_NAME}`)
- Environment variables from compose file
- Dependencies: postgres, ai-prioritization
- Health check: `curl http://localhost:3000/api/health`
- Auto-restart policy

### 5. Health Check Endpoint
**File**: `frontend/src/app/api/health/route.ts`

Simple endpoint returning:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "prioai-frontend"
}
```

### 6. Documentation
**File**: `frontend/DEPLOYMENT.md`

Comprehensive guide covering:
- Architecture changes
- Field mapping tables
- Environment setup
- Deployment steps
- Troubleshooting
- Security considerations
- Rollback procedures

## 📊 Architecture Overview

```
Frontend (Next.js 15)
    ├── API Routes (/api/tasks)
    │   └── postgres-tasks.ts
    │       └── Direct PostgreSQL Connection
    │           └── VPS Database (tasks table)
    │
    ├── Task Creation Flow
    │   └── POST /api/tasks
    │       └── n8n Webhook (31.97.38.31:5678)
    │           └── AI Prioritization Service
    │               └── PostgreSQL Insert
    │
    └── Docker Container
        ├── Port 3000
        ├── Traefik HTTPS (tasks.domain.com)
        └── Health Check (/api/health)
```

## 🔄 Integration Points

### With n8n Workflow
- **Endpoint**: `http://31.97.38.31:5678/webhook/prioai-tasks`
- **Method**: POST
- **Payload**: Task title, description, requester, est_minutes, due_text, role_hint
- **Response**: Task created with AI priority score

### With PostgreSQL
- **Connection**: Docker internal network (`postgres:5432`)
- **Database**: `prioai_db`
- **Table**: `tasks` (not `prioai_task` anymore)
- **User**: `prioai_user`
- **Pool**: Max 20 connections, 30s idle timeout

### With AI Service
- **Internal**: `http://ai-prioritization:8000`
- **Used by**: n8n workflow (not directly by frontend)
- **Purpose**: AI-powered task prioritization

## 🚀 Deployment Commands

```bash
# On VPS (31.97.38.31)
cd /path/to/TaskPriority
git pull origin main

# Ensure .env.production exists with secrets
cd frontend
nano .env.production  # Add all secrets

# Build and deploy
cd ..
docker compose -f docker-compose-prod.yml build frontend
docker compose -f docker-compose-prod.yml up -d frontend

# Verify
docker compose -f docker-compose-prod.yml logs -f frontend
curl http://localhost:3000/api/health
```

## ✅ Verification Checklist

Before deploying to production:

- [ ] `.env.production` created with all required secrets
- [ ] PostgreSQL accessible from Docker network
- [ ] n8n webhook URL correct and accessible
- [ ] DNS records point to VPS (if using custom domain)
- [ ] Health check endpoint responds
- [ ] Can fetch tasks: `curl http://localhost:3000/api/tasks`
- [ ] Can create task via n8n webhook
- [ ] Traefik routes correctly to frontend
- [ ] SSL certificate provisioned (Let's Encrypt)

## 📝 Git Commits

**Commit 1**: `072b057` - Frontend PostgreSQL integration
- Created postgres-tasks.ts
- Updated API routes
- Added .env.example
- Updated docker-compose-prod.yml
- Added health check endpoint

**Commit 2**: `b90af4e` - Deployment documentation
- Added comprehensive DEPLOYMENT.md guide

## 🔧 Configuration Files

### Modified
- `docker-compose-prod.yml` - Added frontend service
- `frontend/src/app/api/tasks/route.ts` - PostgreSQL integration
- `frontend/src/app/api/tasks/[id]/route.ts` - PostgreSQL integration
- `frontend/src/lib/tasks.ts` - Table name updates
- `.gitignore` - Added .env.production

### Created
- `frontend/src/lib/postgres-tasks.ts` - PostgreSQL operations
- `frontend/src/app/api/health/route.ts` - Health check
- `frontend/.env.example` - Environment template
- `frontend/DEPLOYMENT.md` - Deployment guide

## 🎯 Key Improvements

1. **Direct Database Access**: No more Supabase dependency
2. **Unified Schema**: Matches n8n workflow exactly
3. **Field Mapping**: Transparent conversion between DB and UI
4. **Docker Ready**: Full production deployment configuration
5. **Health Monitoring**: Docker health checks enabled
6. **Security**: Secrets properly excluded from git
7. **Documentation**: Comprehensive deployment guide

## 🔄 Data Flow

### Task Creation
```
User → Frontend UI → POST /api/tasks 
    → n8n Webhook → Microsoft Graph API 
    → AI Prioritization Service → PostgreSQL tasks table 
    → Frontend reads updated task
```

### Task Retrieval
```
User → Frontend UI → GET /api/tasks 
    → postgres-tasks.ts → PostgreSQL 
    → Field mapping (priority_score * 10 = aiScore) 
    → UI displays task
```

### Task Update
```
User → Frontend UI → PATCH /api/tasks/[id] 
    → postgres-tasks.ts → PostgreSQL UPDATE 
    → Fetch updated task → UI reflects changes
```

## 🎉 Status: COMPLETE

All frontend tasks completed and pushed to GitHub. Ready for VPS deployment.

**Next Step**: Deploy to VPS using commands in `frontend/DEPLOYMENT.md`
