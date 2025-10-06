#!/bin/bash

# Enhanced AI Priority Engine Startup Script v2.0

echo "🚀 Starting Enhanced AI Priority Engine v2.0..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if virtual environment exists (.venv is the new standard)
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   brew services start redis  # macOS with Homebrew"
    echo "   sudo systemctl start redis  # Linux with systemd"
    echo "   docker run -d -p 6379:6379 redis:alpine  # Docker"
    echo "   redis-server  # Manual start"
    exit 1
fi

echo "✅ Redis is running"

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please set your OPENAI_API_KEY in the .env file"
    echo "   Edit .env and replace 'your_openai_api_key_here' with your actual API key"
    exit 1
fi

echo "✅ Environment configured!"
echo ""
echo "🧠 Enhanced AI Features:"
echo "   • Mathematical priority scoring with role weights"
echo "   • Time sensitivity analysis for meetings/deadlines"
echo "   • Automated user suggestions and workarounds"
echo "   • Risk assessment and escalation logic"
echo "   • Category-based urgency multipliers"
echo ""

# Start the FastAPI service
echo "🌟 Starting Enhanced AI Priority Engine service..."
echo "📡 Service available at: http://localhost:8000"
echo "🏥 Health check: http://localhost:8000/api/v1/health"
echo "📖 API docs: http://localhost:8000/docs"
echo "📊 Metrics: http://localhost:8000/api/v1/metrics/categories"
echo "👥 Role weights: http://localhost:8000/api/v1/metrics/roles"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
