.PHONY: install dev lint test migrate worker-payments ui ui-dev build docker-up docker-down docker-infra

install:
	pip install -r requirements.txt

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check . --fix
	mypy api agents workflows --ignore-missing-imports

test:
	pytest tests/ -v --cov=. --cov-report=term-missing

migrate:
	alembic upgrade head

worker-payments:
	python -m workers.payment_worker

ui:
	cd ui && npm ci && npm run build

ui-dev:
	cd ui && npm install && npm run dev

docker-infra:
	docker compose up -d postgres redis temporal temporal-ui

docker-up:
	docker compose up -d

docker-down:
	docker compose down

temporal-ns:
	temporal operator namespace update --update-requirement ADMITTED pay_orchestrator || \
	temporal operator namespace create --retention 7 pay_orchestrator

temporal-ui:
	open http://localhost:8080

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
