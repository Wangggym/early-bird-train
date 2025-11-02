SHELL := /bin/bash
HIDE ?= @

.PHONY: gen fix check dev test run docker-build docker-up docker-down docker-logs clean

name := "early-bird-train"

# Initialize environment
gen:
	-$(HIDE)rm -rf .venv
	$(HIDE)uv venv .venv --python=3.12.10
	$(HIDE)source .venv/bin/activate && uv pip install -r requirements.txt
	@echo "✅ Environment created. Run 'source .venv/bin/activate' to activate."

# Code formatting and fixes
fix:
	$(HIDE)source .venv/bin/activate && uv run ruff format src/ main.py
	$(HIDE)source .venv/bin/activate && uv run ruff check --fix src/ main.py
	@echo "✅ Code formatted and fixed."

# Type checking
check:
	$(HIDE)source .venv/bin/activate && MYPY_FORCE_COLOR=1 uv run mypy src/ main.py --color-output | grep --color=always -v "note:"
	@echo "✅ Type check completed."
	
# Development mode (run once, full configuration required)
dev:
	$(HIDE)source .venv/bin/activate && python main.py --once

# Production run (scheduled)
run:
	$(HIDE)source .venv/bin/activate && python main.py

# Tests
test:
	$(HIDE)source .venv/bin/activate && uv run pytest -v
	@echo "✅ Tests passed."

# Tests with coverage
test-cov:
	$(HIDE)source .venv/bin/activate && uv run pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report generated in htmlcov/"

# Fast tests (parallel)
test-fast:
	$(HIDE)source .venv/bin/activate && uv run pytest -n auto
	@echo "✅ Fast tests completed."

# Test specific files
test-unit:
	$(HIDE)source .venv/bin/activate && uv run pytest tests/unit/ -v
	@echo "✅ Unit tests passed."

# Docker build
docker-build:
	$(HIDE)docker build -f docker/Dockerfile -t $(name) .
	@echo "✅ Docker image built: $(name)"

# Docker start
docker-up: docker-down
	$(HIDE)docker run -d --name $(name) --env-file .env -v $(PWD)/logs:/app/logs -v $(PWD)/data:/app/data $(name)
	@echo "✅ Container started: $(name)"

# Docker stop
docker-down:
	-$(HIDE)docker rm -f $(name) 2>/dev/null || true
	@echo "✅ Container stopped: $(name)"

# Docker logs
docker-logs:
	$(HIDE)docker logs $(name) -f -n 100

# Cleanup
clean:
	-$(HIDE)rm -rf .venv
	-$(HIDE)rm -rf logs/*.log
	-$(HIDE)rm -rf data/*
	-$(HIDE)find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	-$(HIDE)find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned up."

# Help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make gen          - Initialize virtual environment"
	@echo "  make fix          - Format and fix code"
	@echo "  make check        - Type checking"
	@echo "  make dev          - Development mode (run once)"
	@echo "  make run          - Production run (scheduled)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make test-fast    - Fast tests (parallel)"
	@echo "  make test-unit    - Run unit tests only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker container"
	@echo "  make docker-down  - Stop Docker container"
	@echo "  make docker-logs  - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean temporary files"

