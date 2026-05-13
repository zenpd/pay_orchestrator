.PHONY: help setup clean run-local run-docker stop install-deps test lint format

help:
	@echo "Payment Orchestrator - Development Commands"
	@echo "============================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup              - Complete setup (venv, deps, db)"
	@echo "  make install-deps       - Install Python dependencies"
	@echo "  make install-frontend   - Install frontend dependencies"
	@echo ""
	@echo "Local Development:"
	@echo "  make run-local          - Run backend + frontend locally"
	@echo "  make run-backend        - Run backend only"
	@echo "  make run-frontend       - Run frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make run-docker         - Run with Docker Compose"
	@echo "  make stop               - Stop Docker containers"
	@echo ""
	@echo "Quality:"
	@echo "  make lint               - Run linters"
	@echo "  make format             - Format code"
	@echo "  make test               - Run tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              - Clean build artifacts"
	@echo ""

setup: install-deps install-frontend
	@echo "✅ Setup complete! Run 'make run-local' to start development."

install-deps:
	@echo "📦 Installing Python dependencies..."
	@test -d venv || python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip setuptools wheel
	@. venv/bin/activate && pip install -r requirements_refactored.txt
	@echo "✅ Python dependencies installed"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd app_refactored/ui && npm install
	@echo "✅ Frontend dependencies installed"

run-backend:
	@echo "🚀 Starting backend server on port 8005..."
	@. venv/bin/activate && cd app_refactored && PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload

run-frontend:
	@echo "🚀 Starting frontend on port 5173..."
	@cd app_refactored/ui && npm run dev

run-local:
	@echo "🚀 Starting Payment Orchestrator (local development)"
	@echo "  Backend:  http://localhost:8005/docs"
	@echo "  Frontend: http://localhost:5173"
	@echo ""
	@echo "Running both servers (use separate terminals):"
	@echo "  Terminal 1: make run-backend"
	@echo "  Terminal 2: make run-frontend"
	@echo ""

run-docker:
	@echo "🐳 Starting with Docker Compose..."
	@cd app_refactored && docker-compose up --build
	@echo ""
	@echo "  Backend:  http://localhost:8005/docs"
	@echo "  Frontend: http://localhost:5173"

stop:
	@echo "⛔ Stopping Docker containers..."
	@cd app_refactored && docker-compose down
	@echo "✅ Stopped"

lint:
	@echo "🔍 Running linters..."
	@. venv/bin/activate && cd app_refactored && ruff check .
	@echo "✅ Lint passed"

format:
	@echo "🎨 Formatting code..."
	@. venv/bin/activate && cd app_refactored && black .
	@echo "✅ Formatted"

test:
	@echo "🧪 Running tests..."
	@. venv/bin/activate && cd app_refactored && pytest
	@echo "✅ Tests passed"

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@rm -rf ./venv
	@cd app_refactored/ui && rm -rf node_modules dist build
	@echo "✅ Cleaned"
