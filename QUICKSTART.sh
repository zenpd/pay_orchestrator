#!/bin/bash
# Quick-start script for Payment Orchestrator (Refactored)

set -e

echo "🚀 Payment Orchestrator - Quick Start"
echo "=================================="

PROJECT_ROOT="/Users/sysadm/Documents/agent_foundry/pay_orchestrator"
cd "$PROJECT_ROOT"

# Check if directories exist
if [ ! -d "app_refactored" ]; then
    echo "❌ app_refactored/ directory not found!"
    exit 1
fi

echo ""
echo "📦 Backend Setup"
echo "================"

# Create Python environment (if not exists)
if [ ! -d "app_refactored/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv app_refactored/venv
fi

# Activate environment
source app_refactored/venv/bin/activate

# Install dependencies
if [ -f "requirements_refactored.txt" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements_refactored.txt
else
    echo "⚠️  requirements_refactored.txt not found"
fi

echo ""
echo "📝 Environment Setup"
echo "==================="

# Create .env file if it doesn't exist
if [ ! -f "app_refactored/.env" ]; then
    echo "Creating .env file..."
    cat > app_refactored/.env << 'EOF'
APP_ENV=development
APP_SECRET_KEY=development-secret-key
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/payment_orchestrator
REDIS_URL=redis://localhost:6379/0

AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4-mini

PHOENIX_COLLECTOR_ENDPOINT=
PHOENIX_PROJECT_NAME=payment-orchestration

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

TEMPORAL_ENABLED=false
EOF
    echo "✅ .env created (update with your credentials)"
else
    echo "✅ .env already exists"
fi

echo ""
echo "🎨 Frontend Setup"
echo "================="

cd app_refactored/ui

# Check Node.js
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Please install Node.js 18+"
    echo "   https://nodejs.org/"
    exit 1
fi

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

cd "$PROJECT_ROOT"

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "To start the backend:"
echo "  cd app_refactored"
echo "  source venv/bin/activate"
echo "  PYTHONPATH=. uvicorn api.main:app --port 8005 --reload"
echo ""
echo "To start the frontend (in another terminal):"
echo "  cd app_refactored/ui"
echo "  npm run dev"
echo ""
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8005/docs"
echo ""
echo "📖 Documentation:"
echo "  - REFACTORING_GUIDE.md -- Setup and architecture"
echo "  - REFACTORING_CHECKLIST.md -- What's been completed"
echo "  - REFACTORING_SUMMARY.md -- Comprehensive overview"
