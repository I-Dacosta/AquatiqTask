# 🚀 Deploy PrioritiAI (n8n + AIPrioritization + PostgreSQL) to Hostinger VPS

## Why Hostinger VPS?
- **💰 Affordable**: $3.99-7.99/month (cheaper than Railway Pro)
- **🔧 Full Control**: Root access, custom configurations
- **⚡ Performance**: AMD EPYC processors, NVMe SSD for ML workloads
- **🌍 Global**: Data centers worldwide
- **🤖 AI Ready**: Perfect for OpenAI API + Local AI processing
- **🐳 Docker**: Complete containerized stack

## 📋 Prerequisites
- Hostinger VPS account
- TaskPriority code in Git repository
- OpenAI API key
- Domain name configured with DNS pointing to VPS
- Basic understanding of Docker

## 🏗️ Architecture Overview

The production stack includes:
- **Traefik**: Reverse proxy with automatic SSL (Let's Encrypt)
- **n8n**: Workflow automation with PostgreSQL backend
- **AIPrioritization**: FastAPI service for AI task analysis
- **PostgreSQL**: Database for n8n workflow data and task storage

All services run in Docker containers with automatic health checks and restarts.

## 🔧 Step 1: Setup Hostinger VPS

### 1.1 Create VPS
1. Go to [Hostinger VPS](https://www.hostinger.com/vps-hosting)
2. Choose a plan:
   - **VPS 1**: $3.99/month (1 vCPU, 4GB RAM) - Minimal, may struggle with AI
   - **VPS 2**: $7.99/month (2 vCPU, 8GB RAM) - **Recommended** for n8n + AI
   - **VPS 3**: $14.99/month (4 vCPU, 16GB RAM) - High performance
3. Select Ubuntu 22.04 LTS
4. Choose data center closest to your users

### 1.2 Initial Server Setup
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose v2
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Verify installation
docker --version
docker compose version

# Install useful tools
apt install -y git curl nano htop ufw

# Create non-root user (optional but recommended)
adduser prioritiai
usermod -aG docker prioritiai
```

### 1.3 Configure Firewall
```bash
# Setup UFW
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
ufw status
```

### 1.4 Configure DNS
Before proceeding, configure your domain DNS:
```
A Record:    yourdomain.com         → your-vps-ip
A Record:    n8n.yourdomain.com     → your-vps-ip
A Record:    ai.yourdomain.com      → your-vps-ip
```

Wait for DNS propagation (5-30 minutes). Test with:
```bash
ping yourdomain.com
ping n8n.yourdomain.com
ping ai.yourdomain.com
```

## � Step 2: Deploy with Docker Compose

### 2.1 Clone Repository
```bash
# Generate SSH key for GitHub (if needed)
ssh-keygen -t ed25519 -C "prioritiai@hostinger"
cat ~/.ssh/id_ed25519.pub
# Add this key to your GitHub repository Deploy Keys

# Clone repository
cd /opt
git clone git@github.com:yourusername/TaskPriority.git
cd TaskPriority
```

### 2.2 Create Environment File
```bash
# Copy production example
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

**Required variables** (fill these in):
```bash
# CRITICAL: Change these values!
POSTGRES_PASSWORD=YourStrongPasswordHere123!
SSL_EMAIL=your-email@example.com
DOMAIN_NAME=yourdomain.com
OPENAI_API_KEY=sk-proj-your-actual-openai-key

# Database (keep defaults or customize)
POSTGRES_USER=prioai
POSTGRES_DB=prioai_db

# n8n Configuration
SUBDOMAIN=n8n
GENERIC_TIMEZONE=Europe/Oslo

# AI Service
ENVIRONMENT=production
LOG_LEVEL=info
AI_TIMEOUT=300
```

### 2.3 Create Docker Volumes
```bash
# Create external volumes for persistent data
docker volume create traefik_data
docker volume create n8n_data

# Verify volumes
docker volume ls
```

### 2.4 Build and Start Services
```bash
# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Start all services
docker compose -f docker-compose-prod.yml up -d

# Check status
docker compose -f docker-compose-prod.yml ps

# View logs
docker compose -f docker-compose-prod.yml logs -f
```

Expected output:
```
NAME                              STATUS         PORTS
taskpriority-traefik-1           Up             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
taskpriority-postgres-1          Up (healthy)   127.0.0.1:5432->5432/tcp
taskpriority-n8n-1               Up             127.0.0.1:5678->5678/tcp
taskpriority-ai-prioritization-1 Up (healthy)   
```

## ✅ Step 3: Verify Deployment

### 3.1 Check Service Health
```bash
# Check all services are running
docker compose -f docker-compose-prod.yml ps

# Check individual service health
docker compose -f docker-compose-prod.yml exec postgres pg_isready -U prioai
docker compose -f docker-compose-prod.yml exec ai-prioritization curl -f http://localhost:8000/health

# View service logs
docker compose -f docker-compose-prod.yml logs traefik
docker compose -f docker-compose-prod.yml logs postgres
docker compose -f docker-compose-prod.yml logs n8n
docker compose -f docker-compose-prod.yml logs ai-prioritization
```

### 3.2 Test Public Endpoints
```bash
# Test n8n (should redirect to HTTPS and show n8n interface)
curl -I https://n8n.yourdomain.com

# Test AI service health endpoint
curl https://ai.yourdomain.com/health
# Expected: {"status":"healthy","version":"2.0.0"}

# Test AI service docs
curl -I https://ai.yourdomain.com/docs
# Should return 200 OK

# Check SSL certificates
curl -vI https://n8n.yourdomain.com 2>&1 | grep "SSL certificate"
```

### 3.3 Access Services
- **n8n**: https://n8n.yourdomain.com
- **AI Service**: https://ai.yourdomain.com
- **AI API Docs**: https://ai.yourdomain.com/docs

First time accessing n8n, you'll be prompted to create an admin account.

## � Step 4: Configure n8n Workflow

### 4.1 Import Workflow
1. Access n8n at https://n8n.yourdomain.com
2. Create your admin account
3. Go to **Workflows** → **Import from File**
4. Upload: `n8n/PrioritiAI - Simplified Workflow.json`

### 4.2 Update Workflow Configuration
Update these nodes in the imported workflow:

**AI Classification Node (HTTP Request)**:
- URL: `https://ai.yourdomain.com/classify`
- Method: POST
- Authentication: None (internal network)

**Database Insert Node (Postgres)**:
- Host: `postgres`
- Port: `5432`
- Database: `prioai_db`
- User: `prioai`
- Password: (use your POSTGRES_PASSWORD)

### 4.3 Test Workflow
1. Click **Execute Workflow** in n8n
2. Send a test webhook with sample task data
3. Verify AI classification works
4. Check database insert succeeded

## 📊 Step 5: Monitoring & Maintenance

### 5.1 View Logs
```bash
# All services
docker compose -f docker-compose-prod.yml logs -f

# Specific service
docker compose -f docker-compose-prod.yml logs -f n8n
docker compose -f docker-compose-prod.yml logs -f ai-prioritization
docker compose -f docker-compose-prod.yml logs -f postgres
docker compose -f docker-compose-prod.yml logs -f traefik

# Last 100 lines
docker compose -f docker-compose-prod.yml logs --tail=100 ai-prioritization
```

### 5.2 System Monitoring
```bash
# Install monitoring tools
apt install -y htop nethogs iotop

# Monitor resources
htop                    # CPU, RAM, processes
docker stats           # Container resource usage
df -h                  # Disk usage
free -h                # Memory usage

# Check disk space (important for Docker)
docker system df
```

### 5.3 Database Management
```bash
# Access PostgreSQL
docker compose -f docker-compose-prod.yml exec postgres psql -U prioai -d prioai_db

# Common PostgreSQL commands:
\dt                    # List tables
\d+ table_name        # Describe table
SELECT * FROM tasks LIMIT 10;  # Query data

# Backup database
docker compose -f docker-compose-prod.yml exec postgres pg_dump -U prioai prioai_db > backup_$(date +%Y%m%d).sql

# Restore database
docker compose -f docker-compose-prod.yml exec -T postgres psql -U prioai prioai_db < backup_20240115.sql
```

### 5.4 Automated Backups
```bash
# Create backup script
nano /opt/TaskPriority/backup.sh
```

```bash
#!/bin/bash
# Backup script for PrioritiAI
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/TaskPriority"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
docker compose -f $PROJECT_DIR/docker-compose-prod.yml exec -T postgres \
    pg_dump -U prioai prioai_db | gzip > $BACKUP_DIR/database_$DATE.sql.gz

# Backup n8n data volume
docker run --rm -v n8n_data:/data -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/n8n_data_$DATE.tar.gz -C /data .

# Backup environment file (be careful with this!)
cp $PROJECT_DIR/.env.production $BACKUP_DIR/env_$DATE.backup

# Keep only last 14 days of backups
find $BACKUP_DIR -name "database_*.sql.gz" -mtime +14 -delete
find $BACKUP_DIR -name "n8n_data_*.tar.gz" -mtime +14 -delete
find $BACKUP_DIR -name "env_*.backup" -mtime +14 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /opt/TaskPriority/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /opt/TaskPriority/backup.sh >> /var/log/prioritiai-backup.log 2>&1
```

## 🔄 Step 6: Updates & Deployment

### 6.1 Update Services
```bash
cd /opt/TaskPriority

# Pull latest code
git pull origin main

# Rebuild and restart services
docker compose -f docker-compose-prod.yml up -d --build

# Or restart specific service
docker compose -f docker-compose-prod.yml up -d --build ai-prioritization

# Check updated services
docker compose -f docker-compose-prod.yml ps
```

### 6.2 Zero-Downtime Deployment Script
```bash
nano /opt/TaskPriority/deploy.sh
```

```bash
#!/bin/bash
# Zero-downtime deployment script
cd /opt/TaskPriority

echo "🚀 Starting deployment..."

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Build new images
echo "🔨 Building new images..."
docker compose -f docker-compose-prod.yml build

# Deploy with rolling update
echo "🔄 Deploying services..."
docker compose -f docker-compose-prod.yml up -d --no-deps --build ai-prioritization
sleep 10

docker compose -f docker-compose-prod.yml up -d --no-deps --build n8n
sleep 5

# Health checks
echo "🏥 Running health checks..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://ai.yourdomain.com/health)
if [ "$HEALTH" -eq 200 ]; then
    echo "✅ AI service healthy"
else
    echo "❌ AI service health check failed (HTTP $HEALTH)"
    exit 1
fi

N8N_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://n8n.yourdomain.com)
if [ "$N8N_HEALTH" -eq 200 ] || [ "$N8N_HEALTH" -eq 302 ]; then
    echo "✅ n8n service healthy"
else
    echo "❌ n8n health check failed (HTTP $N8N_HEALTH)"
    exit 1
fi

# Cleanup old images
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ Deployment completed successfully!"
```

```bash
chmod +x /opt/TaskPriority/deploy.sh
```

### 6.3 Rollback Procedure
```bash
# If deployment fails, rollback to previous version
cd /opt/TaskPriority

# Revert to previous git commit
git log --oneline -n 5  # Find commit hash
git checkout <previous-commit-hash>

# Rebuild and restart
docker compose -f docker-compose-prod.yml up -d --build

# Or restore from backup
./backup.sh  # This should have restore capability
```

## 🧪 Step 7: Testing

### 7.1 Health Check
```bash
curl http://your-vps-ip/health
curl http://your-vps-ip/docs  # FastAPI docs
```

### 7.2 Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test performance
ab -n 100 -c 10 http://your-vps-ip/health
```

## 📋 Step 8: Update n8n Configuration

In your n8n workflow, update the AI service URL to:
```
http://your-vps-ip:80
# or
https://your-domain.com
```

## 💰 Cost Comparison

### Hostinger VPS vs Alternatives
- **Hostinger VPS 2**: $7.99/month
- **Railway Pro**: $5/month + usage
- **DigitalOcean**: $12/month
- **AWS EC2 t3.small**: ~$15/month

**Winner**: Hostinger VPS for price/performance ratio!

## 🎯 Benefits of Hostinger VPS

1. **Cost Effective**: Cheapest option for dedicated resources
2. **Performance**: AMD EPYC processors, NVMe SSD
3. **Control**: Full root access, custom configurations
4. **Scalability**: Easy to upgrade plans
5. **Support**: 24/7 customer support
6. **Backup**: Free weekly backups included
7. **Global**: Data centers worldwide

## 🆘 Troubleshooting

### Common Issues
```bash
# Service won't start
sudo journalctl -u prioritiai-ai -n 50

# Permission issues
sudo chown -R prioritiai:www-data /home/prioritiai/TaskPriority

# Nginx config test
sudo nginx -t

# Check open ports
sudo netstat -tlnp | grep :8080

# Memory issues
free -h
htop
```

### Performance Optimization
```bash
# Increase worker count for high traffic
# Edit /etc/systemd/system/prioritiai-ai.service
# Change --workers 2 to --workers 4

# Enable Nginx caching for static responses
# Add to nginx config:
location /health {
    proxy_pass http://127.0.0.1:8080/health;
    proxy_cache_valid 200 1m;
}
```

## 🎉 Final Steps

1. ✅ AI service running on Hostinger VPS
2. ✅ Nginx reverse proxy configured
3. ✅ SSL certificate installed (if domain)
4. ✅ Monitoring and backups setup
5. ✅ Update n8n workflow with new URL
6. ✅ Test end-to-end integration

Your AI service is now running on a professional, scalable infrastructure for less than $8/month! 🚀