# 🚀 PrioritiAI Production Deployment Guide

Complete guide to deploy PrioritiAI to production using free/low-cost services.

## 📋 Architecture Overview

**Option A: Free MVP Stack**
- **Frontend**: Vercel (Next.js)
- **Database**: Supabase (PostgreSQL)
- **Workflow Engine**: n8n Cloud
- **AI Service**: Railway (free tier)
- **Cost**: ~$0/month

**Option B: Hostinger VPS Stack (RECOMMENDED)**
- **Frontend**: Vercel (Next.js)
- **Database**: Supabase (PostgreSQL)  
- **Workflow Engine**: n8n Cloud
- **AI Service**: Hostinger VPS
- **Cost**: ~$8/month

**Option C: All-VPS Stack**
- **Everything**: Hostinger VPS (can host all services)
- **Cost**: ~$8/month total

## 🔧 Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/login with GitHub
3. Click "New Project"
4. Choose organization and set:
   - **Name**: `prioritiai-db`
   - **Database Password**: Generate strong password
   - **Region**: Choose closest to your users
5. Wait for project creation (~2 minutes)

### 1.2 Create Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Run this SQL to create the schema:

```sql
-- Create the prioai_task table
CREATE TABLE IF NOT EXISTS prioai_task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    source_ref VARCHAR(255),
    requester VARCHAR(255) NOT NULL,
    role_hint VARCHAR(100),
    due_at TIMESTAMP WITH TIME ZONE,
    est_minutes INTEGER,
    value_score INTEGER NOT NULL DEFAULT 50,
    risk_score INTEGER NOT NULL DEFAULT 50,
    role_score INTEGER NOT NULL DEFAULT 50,
    haste_score INTEGER NOT NULL DEFAULT 50,
    ai_score INTEGER NOT NULL DEFAULT 50,
    ai_reason TEXT,
    override_priority INTEGER,
    override_locked BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'incoming',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_prioai_task_status ON prioai_task(status);
CREATE INDEX IF NOT EXISTS idx_prioai_task_source ON prioai_task(source);
CREATE INDEX IF NOT EXISTS idx_prioai_task_ai_score ON prioai_task(ai_score DESC);
CREATE INDEX IF NOT EXISTS idx_prioai_task_created_at ON prioai_task(created_at DESC);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_prioai_task_updated_at 
    BEFORE UPDATE ON prioai_task 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### 1.3 Configure API Settings
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**
   - **anon/public key**
   - **service_role key** (for server-side operations)

### 1.4 Set Row Level Security (Optional but Recommended)
```sql
-- Enable RLS
ALTER TABLE prioai_task ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (customize later)
CREATE POLICY "Allow all operations" ON prioai_task
    FOR ALL USING (true) WITH CHECK (true);
```

## 🎯 Step 2: Frontend Deployment (Vercel)

### 2.1 Prepare Frontend
1. Ensure your frontend code is in a Git repository
2. Update dependencies:
```bash
cd frontend
npm install @supabase/supabase-js
npm run build  # Test build
```

### 2.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up/login with GitHub
3. Click "New Project"
4. Import your repository
5. Configure:
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: `frontend` (if frontend is in subdirectory)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 2.3 Add Environment Variables
In Vercel dashboard → **Settings** → **Environment Variables**:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
NODE_ENV=production
```

### 2.4 Deploy
1. Click "Deploy"
2. Wait for deployment
3. Test your app at the provided URL

## 🔄 Step 3: n8n Cloud Setup

### 3.1 Create n8n Cloud Account
1. Go to [n8n.cloud](https://n8n.cloud)
2. Sign up (free tier: 5K executions/month)
3. Create new workflow

### 3.2 Import Workflow
1. Copy the content from `n8n/PrioritiAI - Simplified Workflow.json` (recommended)
   - Uses HTTP calls to AIPrioritization service
   - Simpler architecture, easier to debug
   - Better production compatibility
2. Alternative: Use `n8n/PrioritiAI - Unified Workflow.json` (LangChain-based)
3. In n8n Cloud: **New** → **Import from JSON**
4. Paste the workflow JSON

### 3.3 Configure Credentials
1. **PostgreSQL** (for direct DB access if needed):
   - Host: `db.your-project.supabase.co`
   - Database: `postgres`
   - Username: `postgres`
   - Password: Your Supabase database password
   - Port: `5432`
   - SSL: `require`

2. **Microsoft OAuth2** (for Outlook/Teams):
   - Go to [Azure Portal](https://portal.azure.com)
   - Register app with necessary permissions
   - Add credentials to n8n

3. **OpenAI API**:
   - Add your OpenAI API key

### 3.4 Configure Webhooks
1. Activate the workflow
2. Copy webhook URLs from nodes:
   - **Webhook Create Task**: `https://your-n8n.app.n8n.cloud/webhook/prioai/tasks`
3. Update frontend environment variables

### 3.5 Update Environment Variables
Add to n8n Cloud environment:
```bash
TEAMS_WEBHOOK_URL=your_teams_webhook_url
TEAMS_PLAN_ID=your_planner_plan_id
TEAMS_BUCKET_ID=your_planner_bucket_id
```

## 🤖 Step 4: AI Service Deployment

Choose your preferred option:

### Option A: Hostinger VPS (RECOMMENDED - Best Value)
- **Cost**: $3.99-7.99/month
- **Benefits**: Dedicated resources, full control, better performance
- **Service**: AIPrioritization (Advanced AI engine)
- **Setup**: See detailed guide in `HOSTINGER_AI_DEPLOYMENT.md`

### Option B: Railway (Easiest Setup)  
- **Cost**: Free tier available, $5/month for Pro
- **Benefits**: Automatic deployments, simple setup
- **Service**: AIPrioritization (Advanced AI engine)
- **Setup**: Follow instructions below

---

### 4.1 Railway Deployment (AIPrioritization)

#### 4.1.1 Prepare AIPrioritization Service
1. Ensure the `AIPrioritization` directory has a `Dockerfile`
2. Push to Git repository
3. Service provides advanced AI priority scoring with auto-metric calculation

#### 4.1.2 Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository and choose `AIPrioritization` as root directory
5. Railway will auto-detect Dockerfile and deploy

#### 4.1.3 Configure Environment  
Add environment variables in Railway:
```bash
OPENAI_API_KEY=your_openai_key
PORT=8000
```

#### 4.1.4 Get Service URL
1. Copy the provided Railway URL (e.g., `https://your-service.railway.app`)
2. Update n8n workflow to use this URL
3. Update frontend environment with AI service URL

### 4.2 AIPrioritization Service Features

The new AIPrioritization service provides:
- **Advanced Priority Algorithm**: Multi-factor weighted scoring
- **Auto-Metric Calculation**: AI determines business value, risk, effort from content
- **GDPR Compliance**: Local processing for sensitive data
- **Legacy Compatibility**: `/classify` endpoint for existing n8n workflows
- **Modern API**: `/api/v1/prioritization/sync` for new integrations

## 🔗 Step 5: Connect Everything

### 5.1 Update Frontend Environment
In Vercel, add/update:
```bash
NEXT_PUBLIC_N8N_WEBHOOK_URL=https://your-n8n.app.n8n.cloud/webhook/prioai/tasks
AI_SERVICE_URL=https://your-aiprioritization-service.railway.app
```

### 5.2 Update n8n Workflow
1. Update AI service URL in HTTP request node:
   - Change URL to your deployed AIPrioritization service
   - For Railway: `https://your-service.railway.app/classify`
   - For Hostinger: `https://your-domain.com/classify`
2. Update database connection to use Supabase
3. Test all connections

### 5.3 Configure Microsoft Integration
1. Set up Teams webhooks for notifications
2. Configure Planner integration (Plan ID, Bucket ID)
3. Test email and Teams triggers

## 🧪 Step 6: Testing

### 6.1 Test Webhook Integration
```bash
curl -X POST https://your-app.vercel.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing webhook integration",
    "requester": "Test User",
    "priority_score": 75
  }'
```

### 6.2 Test n8n Workflow
1. Send a test email to trigger Outlook integration
2. Post a message in Teams to trigger Teams integration
3. Create a manual task via webhook
4. Verify tasks appear in frontend and Planner

### 6.3 Test Frontend
1. Visit your Vercel URL
2. Check all three tabs work
3. Test task status updates
4. Verify real-time updates

## 📊 Monitoring & Limits

### Free Tier Limits
- **Vercel**: 100GB bandwidth, 100 serverless function invocations
- **Supabase**: 500MB database, 50K API requests, 2GB bandwidth
- **n8n Cloud**: 5K workflow executions
- **Railway**: 500 hours execution time

### Upgrade Path
When you hit limits:
1. **Vercel Pro**: $20/month
2. **Supabase Pro**: $25/month  
3. **n8n Starter**: $20/month
4. **Railway Pro**: $5/month

## 🔒 Security Considerations

### Production Security
1. **Environment Variables**: Never commit secrets
2. **Database**: Enable RLS policies
3. **API Keys**: Rotate regularly
4. **HTTPS**: Ensure all endpoints use HTTPS
5. **CORS**: Configure proper CORS settings

### Supabase Security
```sql
-- Example RLS policy for multi-tenant
CREATE POLICY "Users can only see their tasks" ON prioai_task
    FOR ALL USING (requester = auth.email());
```

## 🎉 Going Live

1. **Custom Domain**: Add to Vercel
2. **SSL Certificate**: Auto-managed by Vercel
3. **Analytics**: Add Vercel Analytics
4. **Monitoring**: Set up error tracking
5. **Backup**: Supabase auto-backups included

## 🆘 Troubleshooting

### Common Issues
1. **CORS Errors**: Check Supabase CORS settings
2. **Webhook Timeouts**: Increase timeout in n8n
3. **Database Connection**: Verify Supabase credentials
4. **Missing Environment Variables**: Check all services have required vars

### Debug Endpoints
- Frontend: `https://your-app.vercel.app/api/stats`
- n8n: Check execution logs in n8n Cloud
- Database: Use Supabase SQL editor

## 📈 Scaling Strategy

### Phase 1 (MVP - Free)
- Current architecture
- Manual monitoring
- Basic features

### Phase 2 (Growth - $70/month)
- Paid tiers
- Custom authentication
- Advanced analytics

### Phase 3 (Scale - $200+/month)
- Dedicated infrastructure
- Custom domains
- Enterprise features

---

**Total Setup Time**: ~2-4 hours
**Monthly Cost**: $0-70 depending on usage
**Scalability**: Easily handles 1000+ tasks and hundreds of users