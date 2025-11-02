# Local Docker Testing Guide

This guide helps you test the project locally using Docker.

## 📋 Prerequisites

- Docker installed
- Docker Compose installed

## 🚀 Quick Start

### 1. Configure Environment Variables

Copy configuration template:
```bash
cp .env.example .env
```

Edit `.env` file

### 2. Test Run Once (Recommended)

Test once to ensure configuration is correct:

```bash
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

You will see output similar to:
```
INFO | Starting Early Bird Train...
INFO | Monitoring: C3380 (大邑 -> 成都南)
INFO | Running ticket monitoring once...
INFO | Configured schedule: Mon at 15:30 (max_retries=5)
INFO | Today: 2025-11-02 (Sunday)
INFO | Calculated target (day 15): 2025-11-16 (Sunday)
INFO | Fetching URL: https://trains.ctrip.com/...
INFO | Successfully fetched 1 train(s)
INFO | Email sent successfully
```

### 3. Start Scheduled Tasks

After test passes, start scheduled monitoring:

```bash
# Run in background
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop service
docker-compose -f docker/docker-compose.yml down
```

## 🔍 View Logs

Log files are saved in `./logs` directory:

```bash
# View latest logs
tail -f logs/app.log

# View today's logs
grep "$(date +%Y-%m-%d)" logs/app.log
```

## 🐛 Troubleshooting

### 1. DeepSeek API 401 Error

```
WARNING | AI analysis failed, using fallback: Error code: 401
```

**Cause**: Invalid API Key

**Solution**:
- Visit https://platform.deepseek.com/ to get a new API Key
- Update `DEEPSEEK_API_KEY` in `.env`
- Restart container

### 2. Email Sending Failed

**Common Causes**:
- SMTP password incorrect (Gmail requires "App-specific password")
- SMTP server address/port incorrect
- Firewall blocking

**Solution**:
- Confirm SMTP configuration is correct
- Gmail users need to enable "Two-factor authentication" and generate "App-specific password"
- Check firewall settings

### 3. View Container Logs

```bash
# View logs in real-time
docker logs -f early-bird-train

# View last 100 lines
docker logs --tail 100 early-bird-train
```

## 📝 Common Commands

```bash
# Rebuild image
docker-compose -f docker/docker-compose.yml build

# Check container status
docker-compose -f docker/docker-compose.yml ps

# Stop and remove containers
docker-compose -f docker/docker-compose.yml down

# View container resource usage
docker stats early-bird-train
```
