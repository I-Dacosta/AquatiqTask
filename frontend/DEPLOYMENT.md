# Frontend Deployment Guide

## Overview
The PrioritiAI frontend is now configured to use direct PostgreSQL connections instead of Supabase. It integrates with n8n workflows and the AI prioritization service running on the VPS.

## Architecture Changes

### Database Integration
- **Removed**: Supabase client library usage
- **Added**: Direct PostgreSQL connection via `pg` library
- **Module**: `src/lib/postgres-tasks.ts` provides all CRUD operations
- **Connection Pool**: Managed in `src/lib/db.ts` using environment variable `DATABASE_URL`

### Field Mappings
The system handles schema differences between the database and UI:

| Database (PostgreSQL) | UI (Frontend) | Conversion |
|-----------------------|---------------|------------|
| `priority_score` (0-10) | `aiScore` (0-100) | Multiply by 10 |
| `urgency_level` (CRITICAL/HIGH/MEDIUM/LOW) | `priority` (urgent/high/medium/low) | Lowercase mapping |
| `incoming` status | `inbox` status | Direct mapping |
| `in_progress` status | `in-progress` status | Hyphen conversion |

### API Routes Updated
1. **GET /api/tasks** - Fetches tasks with filtering support
2. **POST /api/tasks** - Forwards to n8n webhook for AI processing
3. **GET /api/tasks/[id]** - Fetches individual task
4. **PUT/PATCH /api/tasks/[id]** - Updates task status or priority
5. **DELETE /api/tasks/[id]** - Deletes task
6. **GET /api/health** - Health check endpoint for Docker

## Environment Configuration

### Required Environment Variables

Create a `.env.production` file (not committed to git):

```env
# NextAuth Configuration
AUTH_SECRET=your_auth_secret_here
AUTH_URL=https://tasks.yourdomain.com

# Microsoft Entra ID
AUTH_MICROSOFT_ENTRA_CLIENT_ID=your_client_id
AUTH_MICROSOFT_ENTRA_ID_SECRET=your_client_secret
AUTH_MICROSOFT_ENTRA_ID_TENANT_ID=your_tenant_id

# PostgreSQL Database
DATABASE_URL=postgresql://prioai_user:AquatiqSecure2024@postgres:5432/prioai_db

# n8n Webhook
NEXT_PUBLIC_N8N_WEBHOOK_URL=https://n8n.yourdomain.com/webhook/prioai-tasks

# AI Service
NEXT_PUBLIC_AI_SERVICE_URL=http://ai-prioritization:8000

# Frontend URL
NEXT_PUBLIC_FRONTEND_URL=https://tasks.yourdomain.com

# Feature Flags
NEXT_PUBLIC_AUTH_CONFIGURED=true
NEXT_PUBLIC_ENABLE_N8N_INTEGRATION=true
NEXT_PUBLIC_ENABLE_AI_SERVICE=true
```

### Docker Compose Configuration

The frontend is configured in `docker-compose-prod.yml`:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  labels:
    - traefik.enable=true
    - traefik.http.routers.frontend.rule=Host(`tasks.${DOMAIN_NAME}`)
    - traefik.http.routers.frontend.tls=true
  environment:
    - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    - N8N_WEBHOOK_URL=https://${SUBDOMAIN}.${DOMAIN_NAME}/webhook/prioai-tasks
  depends_on:
    - postgres
    - ai-prioritization
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
```

## Deployment Steps

### 1. Prepare VPS Environment

SSH into your VPS:
```bash
ssh root@31.97.38.31
cd /path/to/TaskPriority
```

### 2. Create Production Environment File

Create `.env.production` in the frontend directory with all required secrets:
```bash
cd frontend
nano .env.production
# Paste your production configuration
```

### 3. Pull Latest Code

```bash
git pull origin main
```

### 4. Build and Deploy

```bash
# Build the frontend service
docker compose -f docker-compose-prod.yml build frontend

# Start the frontend (will start dependencies automatically)
docker compose -f docker-compose-prod.yml up -d frontend

# Check logs
docker compose -f docker-compose-prod.yml logs -f frontend
```

### 5. Verify Deployment

Check health endpoint:
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "prioai-frontend"
}
```

Test task retrieval:
```bash
curl http://localhost:3000/api/tasks
```

### 6. DNS Configuration

If using Traefik with custom domain:
1. Point `tasks.yourdomain.com` to your VPS IP (31.97.38.31)
2. Traefik will automatically provision SSL certificate via Let's Encrypt
3. Access frontend at `https://tasks.yourdomain.com`

## Database Connection

The frontend connects to PostgreSQL using the internal Docker network:
- **Host**: `postgres` (Docker service name)
- **Port**: `5432`
- **Database**: `prioai_db`
- **User**: `prioai_user`
- **Password**: Set in `.env.production`

### Connection Pool Configuration

In `src/lib/postgres-tasks.ts`:
```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,                  // Maximum connections
  idleTimeoutMillis: 30000, // 30 seconds
  connectionTimeoutMillis: 2000
})
```

## Task Creation Flow

When a user creates a task through the frontend:

1. **POST /api/tasks** receives task data
2. Request is forwarded to n8n webhook: `https://n8n.yourdomain.com/webhook/prioai-tasks`
3. n8n workflow:
   - Fetches Microsoft Outlook/Graph data
   - Calls AI prioritization service
   - Inserts prioritized task into PostgreSQL `tasks` table
4. Frontend polls or refreshes to see new task

## Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is accessible
docker compose -f docker-compose-prod.yml exec frontend sh
apk add postgresql-client
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks;"
```

### View Logs

```bash
# Frontend logs
docker compose -f docker-compose-prod.yml logs -f frontend

# All services
docker compose -f docker-compose-prod.yml logs -f
```

### Database Connection Errors

If seeing "connection refused" errors:
1. Verify `DATABASE_URL` uses `postgres` as hostname (not `localhost`)
2. Check PostgreSQL is running: `docker compose ps postgres`
3. Verify database exists: `docker compose exec postgres psql -U prioai_user -d prioai_db -c "\dt"`

### n8n Webhook Errors

If task creation fails:
1. Check n8n is running: `curl http://31.97.38.31:5678/healthz`
2. Verify webhook URL in `.env.production`
3. Check n8n workflow is active
4. View n8n logs: `docker compose logs -f n8n`

## Performance Considerations

### Connection Pooling
- Default max 20 connections
- Adjust in `postgres-tasks.ts` if needed
- Monitor with: `SELECT count(*) FROM pg_stat_activity;`

### Caching
- Consider adding Redis for session/task caching
- Use Next.js ISR (Incremental Static Regeneration) for static pages

### Scaling
- Frontend is stateless and can scale horizontally
- Add multiple replicas in docker-compose:
  ```yaml
  frontend:
    deploy:
      replicas: 3
  ```
- Traefik will load balance automatically

## Security Notes

1. **Secrets Management**: Never commit `.env.production` to git
2. **Database Access**: Frontend uses restricted user `prioai_user`
3. **HTTPS**: Traefik handles SSL/TLS termination
4. **CORS**: Configure in Next.js config if needed
5. **Rate Limiting**: Consider adding for public endpoints

## Rollback Procedure

If deployment fails:

```bash
# View previous images
docker images priotask-frontend

# Stop current version
docker compose -f docker-compose-prod.yml stop frontend

# Revert code
git log  # Find last working commit
git checkout <commit-hash>

# Rebuild and restart
docker compose -f docker-compose-prod.yml build frontend
docker compose -f docker-compose-prod.yml up -d frontend
```

## Monitoring

### Health Checks
- Docker health check runs every 30s
- Endpoint: `http://localhost:3000/api/health`
- Unhealthy after 3 consecutive failures

### Logs
- Docker logs: `docker compose logs -f frontend`
- Application logs visible in Next.js console
- Consider adding structured logging (e.g., Winston, Pino)

### Metrics
- Consider adding Prometheus metrics
- Monitor database connection pool usage
- Track API response times

## Next Steps

1. Set up monitoring (Prometheus + Grafana)
2. Configure backup strategy for PostgreSQL
3. Implement rate limiting for public endpoints
4. Add comprehensive error tracking (e.g., Sentry)
5. Set up CI/CD pipeline for automated deployments
