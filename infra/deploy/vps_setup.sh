#!/bin/bash
set -e

echo "🚀 Setting up Hostinger VPS for PrioritiAI (IP-only deployment)..."

VPS_IP="31.97.38.31"

# 1. Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# 2. Install required packages
echo "🔧 Installing Docker and dependencies..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    ufw \
    nano

# 3. Install Docker (if not already installed)
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# 4. Install Docker Compose V2
if ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

# 5. Configure firewall
echo "🔒 Configuring firewall..."
ufw allow 22/tcp     # SSH
ufw allow 5678/tcp   # n8n
ufw allow 8000/tcp   # AI Service
ufw --force enable

# 6. Create deployment directory
echo "📁 Setting up deployment directory..."
mkdir -p /opt/TaskPriority
cd /opt/TaskPriority

# 7. Clone repository
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    git clone https://github.com/I-Dacosta/AquatiqTask.git .
else
    echo "Repository already exists, pulling latest..."
    git pull origin main
fi

# 8. Generate secure password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

# 9. Create .env file for IP-only deployment
cat > .env << EOF
# PrioritiAI Environment Configuration (IP-only deployment)
# Generated: $(date)

# Server Configuration
VPS_IP=$VPS_IP

# Database Configuration
POSTGRES_USER=prioai
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=prioai_db

# n8n Configuration
N8N_HOST=$VPS_IP
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://$VPS_IP:5678/

# AI Service Configuration
OPENAI_API_KEY=sk-your-key-here
AI_SERVICE_URL=http://ai-prioritization:8000

# Microsoft Teams Configuration (optional)
TEAMS_WEBHOOK_URL=
TEAMS_PLAN_ID=
TEAMS_BUCKET_ID=

# Timezone
GENERIC_TIMEZONE=Europe/Oslo
EOF

echo "✅ .env file created with generated database password"

# 10. Create simplified docker-compose for IP-only deployment
cat > docker-compose-ip.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: prioai-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-prioai}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-prioai_db}
    restart: always
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./infra/db/init.sql:/docker-entrypoint-initdb.d/00_init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-prioai}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  n8n:
    image: n8nio/n8n:latest
    container_name: prioai-n8n
    environment:
      - N8N_HOST=${VPS_IP}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://${VPS_IP}:5678/
      - NODE_ENV=production
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE:-Europe/Oslo}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB:-prioai_db}
      - DB_POSTGRESDB_USER=${POSTGRES_USER:-prioai}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
    restart: always
    ports:
      - "5678:5678"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - n8n_data:/home/node/.n8n

  ai-prioritization:
    build:
      context: ./AIPrioritization
      dockerfile: Dockerfile
    container_name: prioai-ai-service
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=info
      - AI_TIMEOUT=300
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: always
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  pg_data:
    driver: local
  n8n_data:
    driver: local
EOFCOMPOSE

echo "✅ docker-compose-ip.yml created"

# 11. Create volumes
echo "📦 Creating Docker volumes..."
docker volume create pg_data 2>/dev/null || true
docker volume create n8n_data 2>/dev/null || true

echo ""
echo "✅ VPS Setup Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   nano /opt/TaskPriority/.env"
echo ""
echo "   Required changes:"
echo "   - OPENAI_API_KEY=sk-..."
echo ""
echo "2. Build and start the services:"
echo "   cd /opt/TaskPriority"
echo "   docker compose -f docker-compose-ip.yml build"
echo "   docker compose -f docker-compose-ip.yml up -d"
echo ""
echo "3. Check service status:"
echo "   docker compose -f docker-compose-ip.yml ps"
echo ""
echo "4. View logs:"
echo "   docker compose -f docker-compose-ip.yml logs -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Access URLs (⚠️ HTTP only - no SSL):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   n8n:        http://$VPS_IP:5678"
echo "   AI Service: http://$VPS_IP:8000"
echo "   Health:     http://$VPS_IP:8000/health"
echo "   API Docs:   http://$VPS_IP:8000/docs"
echo ""
echo "⚠️  WARNING: This setup uses HTTP (no encryption)"
echo "   For production, get a domain and use docker-compose-prod.yml"
echo ""
echo "🔐 Generated database password saved in /opt/TaskPriority/.env"
echo ""
