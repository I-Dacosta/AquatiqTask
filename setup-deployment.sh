#!/bin/bash

# PrioritiAI Quick Deployment Setup Script
# Run this script to set up your deployment environment

echo "🚀 PrioritiAI Deployment Setup"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the root TaskPriority directory"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🔧 Creating local environment file..."
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo "✅ Created .env.local - please update with your actual values"
else
    echo "ℹ️  .env.local already exists"
fi

echo "🏗️  Testing build..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed - please check for errors"
    exit 1
fi

cd ..

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Update frontend/.env.local with your Supabase credentials"
echo "2. Follow DEPLOYMENT_GUIDE.md for full deployment"
echo "3. Import n8n/PrioritiAI - Unified Workflow.json to n8n Cloud"
echo ""
echo "📋 Quick deployment checklist:"
echo "□ Create Supabase project and database"
echo "□ Deploy frontend to Vercel"
echo "□ Set up n8n Cloud workflow"
echo "□ Deploy AI service to Railway"
echo "□ Configure all environment variables"
echo "□ Test end-to-end integration"
echo ""
echo "💡 For detailed instructions, see DEPLOYMENT_GUIDE.md"