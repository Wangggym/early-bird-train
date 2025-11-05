# Environment Variables Update Guide

This document explains how to modify environment variables and apply changes on the server.

---

## 📝 Modifying Environment Variables

### 1. Login to Server

```bash
ssh user@your-server-ip
cd /path/to/early-bird-train
```

### 2. Edit .env File

```bash
# Backup original file (recommended)
cp .env .env.backup

# Edit configuration
vim .env
```

### 3. Common Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCHEDULE_DAYS_OF_WEEK` | Schedule days (0=Mon...6=Sun) | `[0,2,4]` = Mon/Wed/Fri |
| `SCHEDULE_HOUR` | Schedule hour (0-23) | `15` |
| `SCHEDULE_MINUTE` | Schedule minute (0-59) | `30` |
| `DEPARTURE_STATION` | Departure station | `大邑` |
| `ARRIVAL_STATION` | Arrival station | `成都南` |
| `TRAIN_NUMBER` | Train number | `C3380` |
| `DAYS_AHEAD` | Days ahead to query | `15` |
| `MAX_RETRIES` | Retry count | `5` |

---

## 🔄 Apply Configuration Changes

### ✅ Method 1: Recommended (Most Reliable)

```bash
# Stop and restart containers
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

### ✅ Method 2: Quick Update

```bash
# Redeploy (auto-detect configuration changes)
docker-compose -f docker/docker-compose.yml up -d
```

### ❌ Method 3: Not Recommended

```bash
# ⚠️ restart will NOT reload .env file, don't use it!
docker-compose -f docker/docker-compose.yml restart
```

---

## ✅ Verify Configuration

### 1. Check Container Status

```bash
docker-compose -f docker/docker-compose.yml ps
```

### 2. Check Environment Variables

```bash
# Check specific variable
docker exec early-bird-train env | grep SCHEDULE_DAYS_OF_WEEK

# Check all variables
docker exec early-bird-train env
```

### 3. Check Logs

```bash
# View logs in real-time
docker logs -f early-bird-train

# View last 50 lines
docker logs --tail 50 early-bird-train
```

**Expected log output**:
```
INFO | Configured schedule: Mon,Wed,Fri at 15:30 (max_retries=5)
```

### 4. Test Run

```bash
# Run once (without scheduled tasks)
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

---

## 🎯 Common Scenarios

### Scenario 1: Change Schedule Days (Friday Only)

```bash
# 1. Edit .env
vim .env

# Change to:
SCHEDULE_DAYS_OF_WEEK=[4]

# 2. Redeploy
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d

# 3. Verify
docker logs early-bird-train | grep "Configured schedule"
```

### Scenario 2: Change Schedule Time (8:00 AM)

```bash
# 1. Edit .env
vim .env

# Change to:
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0

# 2. Redeploy
docker-compose -f docker/docker-compose.yml up -d

# 3. Verify
docker logs early-bird-train | tail -20
```

### Scenario 3: Change Train Information

```bash
# 1. Edit .env
vim .env

# Change to:
DEPARTURE_STATION=Beijing
ARRIVAL_STATION=Shanghai
TRAIN_NUMBER=G1

# 2. Redeploy
docker-compose -f docker/docker-compose.yml up -d

# 3. Test run
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

---

## ⚠️ Important Notes

### Key Points

1. **JSON Array Format**:
   - ✅ Correct: `SCHEDULE_DAYS_OF_WEEK=[0,2,4]`
   - ❌ Wrong: `SCHEDULE_DAYS_OF_WEEK=0,2,4` (missing brackets)
   - ❌ Wrong: `SCHEDULE_DAYS_OF_WEEK=[0, 2, 4]` (spaces cause parsing errors)

2. **Email List Format**:
   - ✅ Correct: `EMAIL_TO=["user1@example.com","user2@example.com"]`
   - ❌ Wrong: `EMAIL_TO=user1@example.com,user2@example.com`

3. **Always Backup Before Modifying**:
   ```bash
   cp .env .env.backup
   ```

4. **Container Must Be Rebuilt After Env Changes**:
   - `docker-compose up -d` rebuilds containers
   - `docker-compose restart` does **NOT** reload .env

5. **Data Will Not Be Lost**:
   - Log files in `logs/` directory (volume mounted)
   - Rebuilding containers doesn't affect existing logs

---

## 🔧 Troubleshooting

### Issue 1: Configuration Not Applied

```bash
# Check if container was really rebuilt
docker-compose -f docker/docker-compose.yml ps

# View container creation time (should be recent)
docker inspect early-bird-train | grep Created

# Confirm environment variables
docker exec early-bird-train env | grep SCHEDULE
```

### Issue 2: Container Failed to Start

```bash
# View error logs
docker logs early-bird-train

# Check .env file format
cat .env | grep SCHEDULE_DAYS_OF_WEEK

# Restore backup
cp .env.backup .env
docker-compose -f docker/docker-compose.yml up -d
```

### Issue 3: Syntax Error

```bash
# Validate JSON format using Python
python3 -c "import json; print(json.loads('[0,2,4]'))"

# Expected output: [0, 2, 4]
```

---

## 📋 Quick Command Reference

```bash
# Edit configuration
vim .env

# Redeploy (Method 1 - Safest)
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d

# Redeploy (Method 2 - Quick)
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker logs -f early-bird-train

# Test run
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once

# Check environment variables
docker exec early-bird-train env | grep SCHEDULE

# Check container status
docker-compose -f docker/docker-compose.yml ps

# Stop service
docker-compose -f docker/docker-compose.yml down
```

---

## 📚 Related Documentation

- [Deployment Guide](AWS_DEPLOY.md) - Complete deployment workflow
- [Quick Start](QUICKSTART.md) - Local development guide
- [README](README.md) - Project overview and configuration

---

**Last Updated**: 2025-11-05

