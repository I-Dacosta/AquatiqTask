# 🚀 Adding Frontend to Existing Hostinger VPS

## Problem
GitHub Actions succeeded but frontend container wasn't deployed because `docker-compose-ip.yml` on the VPS didn't include the frontend service.

## Solution

### Option 1: Automatic (Recommended)
Push the updated files and let GitHub Actions handle it:

```bash
# Already done - just push to trigger deployment
git add .
git commit -m "feat: Add frontend to VPS docker-compose"
git push origin main
```

GitHub Actions will:
1. Pull latest code (including `docker-compose-ip.yml` with frontend)
2. Build frontend container
3. Start all services including frontend
4. Run health checks

### Option 2: Manual VPS Update

If you need to deploy immediately without waiting for GitHub Actions:

#### Step 1: SSH to VPS
```bash
ssh root@31.97.38.31
cd /opt/TaskPriority
```

#### Step 2: Pull Latest Code
```bash
git fetch origin
git reset --hard origin/main
```

#### Step 3: Update Environment Variables
Add frontend-related variables to `.env`:

```bash
nano .env
```

Add these lines (if not already present):
```env
# Frontend Auth (Microsoft Entra ID)
AUTH_SECRET=your_auth_secret_here
AUTH_MICROSOFT_ENTRA_CLIENT_ID=your_client_id
AUTH_MICROSOFT_ENTRA_ID_SECRET=your_client_secret
AUTH_MICROSOFT_ENTRA_ID_TENANT_ID=your_tenant_id

# VPS IP (for HTTP-only deployment)
VPS_IP=31.97.38.31
```

#### Step 4: Build and Deploy Frontend
```bash
# Build the frontend
docker compose -f docker-compose-ip.yml build frontend

# Start all services (will start frontend)
docker compose -f docker-compose-ip.yml up -d

# Wait for services to start
sleep 20
```

#### Step 5: Verify Deployment
```bash
# Check all services are running
docker compose -f docker-compose-ip.yml ps

# Check frontend health
curl http://localhost:3000/api/health

# Check frontend logs
docker compose -f docker-compose-ip.yml logs frontend

# Test from external access
curl http://31.97.38.31:3000/api/health
```

Expected health response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "prioai-frontend"
}
```

#### Step 6: Open Firewall Port (if needed)
```bash
# Allow port 3000
ufw allow 3000/tcp
ufw status
```

## Verify Services

### Check Docker Status
```bash
docker compose -f docker-compose-ip.yml ps
```

Should show:
```
NAME                      STATUS         PORTS
prioai-postgres           Up (healthy)   127.0.0.1:5432->5432/tcp
prioai-n8n                Up             0.0.0.0:5678->5678/tcp
prioai-ai-service         Up (healthy)   0.0.0.0:8000->8000/tcp
prioai-frontend           Up (healthy)   0.0.0.0:3000->3000/tcp
```

### Test All Endpoints
```bash
# Frontend
curl http://31.97.38.31:3000/api/health

# n8n
curl -I http://31.97.38.31:5678

# AI Service
curl http://31.97.38.31:8000/health

# PostgreSQL
docker compose -f docker-compose-ip.yml exec postgres pg_isready -U prioai_user
```

## Access Frontend

Open in browser:
```
http://31.97.38.31:3000
```

You should see the PrioritiAI task management interface.

## Troubleshooting

### Frontend Container Not Starting
```bash
# Check logs
docker compose -f docker-compose-ip.yml logs frontend

# Common issues:
# 1. Build failed - check Node.js errors
# 2. Database connection - verify DATABASE_URL in .env
# 3. Port conflict - check if port 3000 is in use
```

### Database Connection Errors
```bash
# Test database connectivity from frontend container
docker compose -f docker-compose-ip.yml exec frontend sh
apk add postgresql-client
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks;"
```

### Port Not Accessible Externally
```bash
# Check firewall
ufw status

# Check if port is listening
netstat -tlnp | grep :3000

# Check Docker port mapping
docker port prioai-frontend
```

### Frontend Shows Errors in Browser
```bash
# Check browser console for JavaScript errors
# Check if API routes work:
curl http://31.97.38.31:3000/api/tasks

# Check environment variables are loaded:
docker compose -f docker-compose-ip.yml exec frontend env | grep DATABASE_URL
```

## Files Updated

| File | Change |
|------|--------|
| `docker-compose-ip.yml` | Added frontend service definition |
| `.github/workflows/hostinger-deploy.yml` | Added frontend build and health check |
| `infra/deploy/vps_setup.sh` | Updated template to include frontend |
| `infra/deploy/deploy-to-vps.sh` | Added frontend to access URLs |

## Next Steps

1. ✅ Frontend now deploys automatically via GitHub Actions
2. ✅ Health checks include frontend
3. ✅ All services integrated (PostgreSQL, n8n, AI, Frontend)

To update in the future, just push to main:
```bash
git push origin main
```

GitHub Actions will handle the rest!

## Architecture

```
Frontend (Port 3000)
    ↓
PostgreSQL (Port 5432) ← n8n (Port 5678)
    ↑                         ↓
    └─────── AI Service (Port 8000)
```

All services communicate via Docker internal network.
External access via IP:PORT (HTTP only, no SSL in IP-based deployment).
