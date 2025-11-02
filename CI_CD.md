# CI/CD Configuration Guide

This document explains how to configure and use the project's CI/CD pipeline.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration Steps](#configuration-steps)
- [Workflow Details](#workflow-details)
- [FAQ](#faq)

---

## 🎯 Overview

This project uses **GitHub Actions** for CI/CD:

### **CI (Continuous Integration)**
- ✅ Code format checking (ruff format)
- ✅ Code quality checking (ruff lint)
- ✅ Type checking (mypy)
- ✅ Automated testing (pytest)
- ✅ Test coverage reports
- ✅ Docker build testing

### **CD (Continuous Deployment)**
- 🚀 Build Docker images
- 🚀 Push to Docker Hub
- 🚀 Auto-deploy to AWS EC2
- 🚀 Health checks

---

## 📦 Prerequisites

### 1. Docker Hub Account

1. Register a [Docker Hub](https://hub.docker.com/) account
2. Create an access token:
   - Visit: https://hub.docker.com/settings/security
   - Click "New Access Token"
   - Name: `github-actions`
   - Permissions: `Read, Write, Delete`
   - Save the generated token (displayed only once)

### 2. AWS EC2 Server

Ensure your EC2 server has:
- ✅ Docker and Docker Compose installed
- ✅ Project code cloned from GitHub
- ✅ `.env` file configured
- ✅ SSH access available

### 3. SSH Keys

Get EC2's SSH private key:
```bash
# If using AWS downloaded .pem file
cat ~/.ssh/your-key.pem

# If using self-generated key
cat ~/.ssh/id_rsa
```

---

## 🔧 Configuration Steps

### Step 1: Configure GitHub Secrets

Configure the following secrets in your GitHub repository:

**Path**: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret Name | Description | Example |
|------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Docker Hub username | `your-username` |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_xxxxx...` |
| `AWS_HOST` | EC2 server IP | `52.123.45.67` |
| `AWS_USER` | EC2 login username | `ec2-user` |
| `AWS_SSH_KEY` | SSH private key (full content) | `-----BEGIN RSA...` |
| `AWS_PORT` | SSH port (optional, default 22) | `22` |

**Configuration Example**:

```bash
# DOCKERHUB_USERNAME
your-dockerhub-username

# DOCKERHUB_TOKEN
dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# AWS_HOST
52.123.45.67

# AWS_USER
ec2-user

# AWS_SSH_KEY
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...complete private key content...
-----END RSA PRIVATE KEY-----

# AWS_PORT (optional)
22
```

### Step 2: Update docker-compose.yml

**Option A: Modify Locally and Push (Recommended)**

Modify `docker/docker-compose.yml` locally:

```bash
# On local machine
cd /Users/wangyimin/project/early-bird-train
vim docker/docker-compose.yml
```

Change line 7 to your Docker Hub username:

```yaml
image: your-dockerhub-username/early-bird-train:latest
```

Then push to GitHub:

```bash
git add docker/docker-compose.yml
git commit -m "Update docker-compose with Docker Hub username"
git push origin master
```

Pull latest config on server:

```bash
# SSH to server
ssh ec2-user@your-server-ip
cd ~/early-bird-train
git pull origin master
```

**Option B: Use Environment Variables (Best Practice)**

Without modifying files, set environment variables directly on server:

```bash
# SSH to server
ssh ec2-user@your-server-ip

# Set environment variable (temporary)
export DOCKERHUB_USERNAME=your-dockerhub-username

# Or write to ~/.bashrc (permanent)
echo 'export DOCKERHUB_USERNAME=your-dockerhub-username' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $DOCKERHUB_USERNAME
```

The docker-compose.yml will automatically use the environment variable:
```yaml
image: ${DOCKERHUB_USERNAME:-your-dockerhub-username}/early-bird-train:latest
```

### Step 3: Test CI/CD

1. **Test CI** (code checks):
   ```bash
   # Push to any branch triggers CI
   git add .
   git commit -m "Test CI"
   git push origin master
   ```

2. **Test CD** (build and deploy):
   ```bash
   # Push to master branch triggers CD
   git push origin master
   
   # Or push tag to trigger
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **View Execution Results**:
   - Visit: `https://github.com/your-username/early-bird-train/actions`
   - Check workflow execution status

---

## 🔄 Workflow Details

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers**:
- Push to any branch
- Pull Request to master

**Contains 3 Jobs**:

#### 1. Code Quality Checks
```yaml
Code quality checks:
- ruff format --check  # Format check
- ruff check          # Code quality check
- mypy               # Type check
```

#### 2. Run Tests
```yaml
Run tests:
- pytest tests/ -v                    # Run all tests
- --cov=src --cov-report=xml         # Generate coverage report
- Upload to Codecov (optional)           # Upload coverage
```

#### 3. Test Docker Build
```yaml
Test Docker build:
- Build image but don't push
- Use GitHub Actions cache for speed
```

---

### CD Workflow (`.github/workflows/cd.yml`)

**Triggers**:
- Push to `master` branch
- Push Git Tag (`v*.*.*`)
- Manual trigger (workflow_dispatch)

**Contains 3 Jobs**:

#### 1. Build & Push Docker Image
```yaml
Build and push image:
- Login to Docker Hub
- Build image
- Auto tag:
  - master → latest
  - v1.0.0 → 1.0.0, 1.0, 1, latest
  - commit → master-abc1234
- Push to Docker Hub
```

#### 2. Deploy to AWS EC2
```yaml
Deploy to AWS:
- SSH connect to EC2
- Pull latest image
- Restart containers
- Clean old images
```

#### 3. Health Check
```yaml
Health check:
- Wait for service to start
- Check container status
- Output latest logs
```

---

## 🏷️ Version Management (Git Tag)

### Create and Push Tags

```bash
# 1. Create tag
git tag v1.0.0

# 2. Push tag
git push origin v1.0.0

# 3. View all tags
git tag -l
```

### Tag Naming Convention

Use **Semantic Versioning**:

```
v<major>.<minor>.<patch>

v1.0.0  - Initial version
v1.1.0  - New features
v1.1.1  - Bug fixes
v2.0.0  - Major update (breaking changes)
```

### Docker Image Tag Mapping

| Git Tag | Docker Image Tags |
|---------|------------------|
| `v1.2.3` | `1.2.3`, `1.2`, `1`, `latest` |
| `master` | `latest`, `master-abc1234` |
| `develop` | `develop`, `develop-abc1234` |

---

## 🔍 Monitoring and Debugging

### View Workflow Status

1. **GitHub Actions Page**:
   ```
   https://github.com/your-username/early-bird-train/actions
   ```

2. **View Detailed Logs for a Run**:
   - Click on workflow run record
   - Expand each Step to view logs

### View Docker Hub Images

```
https://hub.docker.com/r/your-username/early-bird-train/tags
```

### Check Deployment Status on Server

```bash
# SSH to server
ssh ec2-user@your-server-ip

# Check container status
docker ps | grep early-bird-train

# View logs
docker logs -f early-bird-train

# View last 50 lines of logs
docker logs --tail 50 early-bird-train
```

---

## 🐛 FAQ

### 1. CI Failure: Code Format Issues

**Error**:
```
Error: ruff format --check failed
```

**Solution**:
```bash
# Fix format locally
make fix

# Commit fix
git add .
git commit -m "Fix code formatting"
git push
```

### 2. CD Failure: Docker Hub Authentication Failed

**Error**:
```
Error: unauthorized: incorrect username or password
```

**Solution**:
1. Check if `DOCKERHUB_USERNAME` is correct
2. Regenerate `DOCKERHUB_TOKEN`
3. Ensure correct configuration in GitHub Secrets

### 3. Deployment Failure: SSH Connection Failed

**Error**:
```
Error: ssh: connect to host xxx.xxx.xxx.xxx port 22: Connection refused
```

**Solution**:
1. Check if `AWS_HOST` IP address is correct
2. Check if EC2 security group allows GitHub Actions IP (or all) to access port 22
3. Check if `AWS_SSH_KEY` private key format is complete

### 4. Deployment Failure: Container Startup Failed

**Error**:
```
Error: Container is not running
```

**Solution**:
```bash
# SSH to server and check
ssh ec2-user@your-server-ip

# View container logs
docker logs early-bird-train

# Common causes:
# - .env file missing or misconfigured
# - Port already in use
# - Dependency services unavailable
```

### 5. Image Pull Failed

**Error**:
```
Error: manifest for xxx/early-bird-train:latest not found
```

**Solution**:
1. Ensure CD workflow executed successfully and pushed the image
2. Check if the image exists on Docker Hub
3. Confirm image name in `docker-compose.yml` is correct

---

## 🚀 Manual Deployment Trigger

Sometimes you may need to trigger deployment manually (without pushing code):

### Method 1: Via GitHub UI

1. Visit: `Actions` → `CD - Build & Deploy`
2. Click `Run workflow`
3. Select branch: `master`
4. Select environment: `production`
5. Click `Run workflow`

### Method 2: Via GitHub CLI

```bash
# Install gh CLI
brew install gh  # macOS
# Or visit https://cli.github.com/

# Login
gh auth login

# Trigger workflow
gh workflow run cd.yml
```

---

## 📊 Add Badges to README

Add status badges at the top of `README.md`:

```markdown
# Early Bird Train

[![CI](https://github.com/your-username/early-bird-train/workflows/CI%20-%20Code%20Quality%20%26%20Tests/badge.svg)](https://github.com/your-username/early-bird-train/actions)
[![CD](https://github.com/your-username/early-bird-train/workflows/CD%20-%20Build%20%26%20Deploy/badge.svg)](https://github.com/your-username/early-bird-train/actions)
[![Docker](https://img.shields.io/docker/v/your-username/early-bird-train?label=docker)](https://hub.docker.com/r/your-username/early-bird-train)
```

---

## 🎓 Best Practices

### 1. Branch Strategy

```
master (production)
  ↑
develop (development)
  ↑
feature/* (feature branches)
```

### 2. Pre-commit Local Checks

```bash
# Run all checks
make check

# Run tests
make test

# Fix format issues
make fix
```

### 3. Version Release Process

```bash
# 1. Ensure on master branch
git checkout master
git pull

# 2. Create tag
git tag v1.0.0

# 3. Push tag (triggers CD)
git push origin v1.0.0

# 4. Create Release on GitHub (optional)
gh release create v1.0.0 --generate-notes
```

### 4. Rollback Deployment

If the new version has issues, quickly rollback:

```bash
# Method 1: Manual rollback on server
ssh ec2-user@your-server-ip
docker-compose -f docker/docker-compose.yml pull your-username/early-bird-train:v1.0.0
docker-compose -f docker/docker-compose.yml up -d

# Method 2: Push old version tag
git tag v1.0.1 v1.0.0^{}  # Create new tag based on old version
git push origin v1.0.1
```

---

## 📞 Get Help

- **GitHub Actions Documentation**: https://docs.github.com/actions
- **Docker Hub Documentation**: https://docs.docker.com/docker-hub/
- **Issue Feedback**: Ask questions in GitHub Issues

---

Last updated: 2025-11-02
