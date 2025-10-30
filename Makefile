SHELL := /bin/bash
HIDE ?= @

.PHONY: gen fix check dev test run docker-build docker-up docker-down docker-logs clean

name := "early-bird-train"

# 初始化环境
gen:
	-$(HIDE)rm -rf .venv
	$(HIDE)uv venv .venv --python=3.12.10
	$(HIDE)source .venv/bin/activate && uv pip install -r requirements.txt
	@echo "✅ Environment created. Run 'source .venv/bin/activate' to activate."

# 代码格式化和修复
fix:
	$(HIDE)source .venv/bin/activate && uv run ruff format src/ main.py
	$(HIDE)source .venv/bin/activate && uv run ruff check --fix src/ main.py
	@echo "✅ Code formatted and fixed."

# 类型检查
check:
	$(HIDE)source .venv/bin/activate && MYPY_FORCE_COLOR=1 uv run mypy src/ main.py --color-output | grep --color=always -v "note:"
	@echo "✅ Type check completed."

# 测试爬虫（无需配置）
test-crawler:
	$(HIDE)source .venv/bin/activate && python test_crawler.py

# 开发模式（运行一次测试，需要完整配置）
dev:
	$(HIDE)source .venv/bin/activate && python main.py --once

# 生产运行（定时调度）
run:
	$(HIDE)source .venv/bin/activate && python main.py

# 测试
test:
	$(HIDE)source .venv/bin/activate && uv run pytest
	@echo "✅ Tests passed."

# Docker构建
docker-build:
	$(HIDE)docker build -f docker/Dockerfile -t $(name) .
	@echo "✅ Docker image built: $(name)"

# Docker启动
docker-up: docker-down
	$(HIDE)docker run -d --name $(name) --env-file .env -v $(PWD)/logs:/app/logs -v $(PWD)/data:/app/data $(name)
	@echo "✅ Container started: $(name)"

# Docker停止
docker-down:
	-$(HIDE)docker rm -f $(name) 2>/dev/null || true
	@echo "✅ Container stopped: $(name)"

# Docker日志
docker-logs:
	$(HIDE)docker logs $(name) -f -n 100

# 清理
clean:
	-$(HIDE)rm -rf .venv
	-$(HIDE)rm -rf logs/*.log
	-$(HIDE)rm -rf data/*
	-$(HIDE)find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	-$(HIDE)find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned up."

# 帮助
help:
	@echo "Available commands:"
	@echo "  make gen          - 初始化虚拟环境"
	@echo "  make fix          - 格式化和修复代码"
	@echo "  make check        - 类型检查"
	@echo "  make dev          - 开发模式（运行一次测试）"
	@echo "  make run          - 生产运行（定时调度）"
	@echo "  make test         - 运行测试"
	@echo "  make docker-build - 构建Docker镜像"
	@echo "  make docker-up    - 启动Docker容器"
	@echo "  make docker-down  - 停止Docker容器"
	@echo "  make docker-logs  - 查看Docker日志"
	@echo "  make clean        - 清理临时文件"

