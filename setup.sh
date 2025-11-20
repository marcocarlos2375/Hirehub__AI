#!/bin/bash

# HireHubAI Setup Script
# This script helps you set up the project quickly

echo "🚀 HireHubAI Setup Script"
echo "========================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY!"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask if user wants to start backend
read -p "🐳 Start backend services (Docker)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Building and starting backend + Qdrant..."
    docker-compose up -d --build
    echo ""
    echo "✅ Backend running at http://localhost:8000"
    echo "✅ Qdrant running at http://localhost:6333"
    echo ""
fi

# Ask if user wants to install frontend dependencies
read -p "📦 Install frontend dependencies? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
    echo ""
    echo "✅ Frontend dependencies installed"
    echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env and add your GEMINI_API_KEY"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Open http://localhost:3000"
echo ""
echo "📚 Read README.md for full documentation"
