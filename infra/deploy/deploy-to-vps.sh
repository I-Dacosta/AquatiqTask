#!/bin/bash
set -e

VPS_HOST="31.97.38.31"
VPS_USER="root"

echo "🚀 Deploying PrioritiAI to Hostinger VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Test SSH connection
echo "🔐 Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'Connection successful'" &> /dev/null; then
    echo "❌ Cannot connect to VPS. Please check:"
    echo "   - VPS is running"
    echo "   - SSH key is added to VPS authorized_keys"
    echo "   - Firewall allows SSH (port 22)"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# 2. Copy setup script to VPS
echo "📤 Uploading setup script to VPS..."
scp infra/deploy/vps_setup.sh $VPS_USER@$VPS_HOST:/tmp/
echo "✅ Setup script uploaded"
echo ""

# 3. Execute setup on VPS
echo "🔧 Running setup script on VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh $VPS_USER@$VPS_HOST 'bash /tmp/vps_setup.sh'
echo ""

# 4. Prompt for OpenAI API key
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 OpenAI API Key Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Do you have an OpenAI API key to configure now? (y/n): " configure_key

if [ "$configure_key" = "y" ] || [ "$configure_key" = "Y" ]; then
    read -sp "Enter your OpenAI API key: " api_key
    echo ""
    
    # Update .env file on VPS
    ssh $VPS_USER@$VPS_HOST "sed -i 's|OPENAI_API_KEY=.*|OPENAI_API_KEY=$api_key|' /opt/TaskPriority/.env"
    echo "✅ API key configured"
else
    echo "⚠️  You'll need to configure the API key manually before starting services"
fi
echo ""

# 5. Ask to start services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 Docker Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Start Docker services now? (y/n): " start_services

if [ "$start_services" = "y" ] || [ "$start_services" = "Y" ]; then
    echo ""
    echo "🔨 Building and starting services..."
    echo "This may take 5-10 minutes on first run..."
    echo ""
    
    ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cd /opt/TaskPriority
echo "Building AI service..."
docker compose -f docker-compose-ip.yml build ai-prioritization

echo ""
echo "Starting all services..."
docker compose -f docker-compose-ip.yml up -d

echo ""
echo "⏳ Waiting 30 seconds for services to initialize..."
sleep 30

echo ""
echo "📊 Service Status:"
docker compose -f docker-compose-ip.yml ps

echo ""
echo "🏥 Health Checks:"
echo "PostgreSQL:"
docker compose -f docker-compose-ip.yml exec -T postgres pg_isready -U prioai || echo "  ⚠️ Not ready yet"

echo "AI Service:"
curl -s http://localhost:8000/health || echo "  ⚠️ Not ready yet"

echo ""
echo "📋 Recent logs:"
docker compose -f docker-compose-ip.yml logs --tail=20
ENDSSH

    echo ""
    echo "✅ Services started!"
else
    echo "⚠️  Services not started. To start manually:"
    echo "   ssh root@$VPS_HOST"
    echo "   cd /opt/TaskPriority"
    echo "   docker compose -f docker-compose-ip.yml up -d"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access your services:"
echo "   n8n:         http://$VPS_HOST:5678"
echo "   AI Service:  http://$VPS_HOST:8000"
echo "   Health:      http://$VPS_HOST:8000/health"
echo "   API Docs:    http://$VPS_HOST:8000/docs"
echo ""
echo "📝 Next steps:"
echo "   1. Open n8n: http://$VPS_HOST:5678"
echo "   2. Create your first admin account"
echo "   3. Import workflow: n8n/PrioritiAI - Unified Workflow.json"
echo "   4. Configure Microsoft 365 & Teams credentials"
echo "   5. Activate the workflow"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:    ssh root@$VPS_HOST 'cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml logs -f'"
echo "   Restart:      ssh root@$VPS_HOST 'cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml restart'"
echo "   Stop:         ssh root@$VPS_HOST 'cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml down'"
echo ""
echo "📚 Documentation:"
echo "   Setup guide:  DEPLOYMENT_IP_ONLY.md"
echo "   n8n guide:    n8n/IMPORT_GUIDE.md"
echo ""
