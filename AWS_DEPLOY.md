# AWS Deployment Guide

This guide helps you deploy the project to AWS EC2 server.

## 📋 Prerequisites

- ✅ AWS EC2 instance created and running
- ✅ SSH access to server configured
- ✅ Docker and Docker Compose installed on server

## 🚀 Deployment Steps

### 4. Configure Environment Variables

```bash
# Create .env file
cp .env.example .env
vim .env
```

### 5. Test Run

Run a test first to ensure configuration is correct:

```bash
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

**Expected Output**:
```
INFO | Starting Early Bird Train...
INFO | Monitoring: C3380 (大邑 -> 成都南)
INFO | Running ticket monitoring once...
INFO | Configured schedule: Mon at 15:30 (max_retries=5)
INFO | Fetching URL: https://trains.ctrip.com/...
INFO | Successfully fetched 1 train(s)
INFO | Email sent successfully
INFO | Ticket monitoring completed successfully
```

### 6. Start Scheduled Service

After test passes, start scheduled monitoring:

```bash
# Start service (background)
docker-compose -f docker/docker-compose.yml up -d

# Check service status
docker-compose -f docker/docker-compose.yml ps

# View real-time logs
docker-compose -f docker/docker-compose.yml logs -f
```

## 📊 Monitoring and Maintenance

### View Logs

```bash
# View logs in real-time
docker logs -f early-bird-train

# View last 100 lines
docker logs --tail 100 early-bird-train

# View today's logs
docker logs early-bird-train 2>&1 | grep "$(date +%Y-%m-%d)"

# View log files
tail -f logs/app.log
```

### Check Container Status

```bash
# Check container status
docker ps -a | grep early-bird-train

# View resource usage
docker stats early-bird-train

# View container details
docker inspect early-bird-train
```

### Update Deployment

```bash
# 1. Stop containers
docker-compose -f docker/docker-compose.yml down

# 2. Update code (choose one method)
# Method 1: Sync from local
# rsync -avz --exclude '.git' user@local:/path/to/project/* ./

# Method 2: Pull from Git
# git pull origin main

# 3. Rebuild image
docker-compose -f docker/docker-compose.yml build --no-cache

# 4. Start new container
docker-compose -f docker/docker-compose.yml up -d

# 5. Verify
docker logs -f early-bird-train
```

### Backup and Cleanup

```bash
# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Clean old logs (keep last 7 days)
find logs/ -name "*.log" -mtime +7 -delete

# Clean Docker images
docker image prune -a -f

# Check disk usage
df -h
du -sh logs/
```

## 🔧 Troubleshooting

### 1. Container Cannot Start

```bash
# View error logs
docker logs early-bird-train

# Check configuration file
cat .env | grep -v '^#' | grep -v '^$'

# Delete container and recreate
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Network Issues

```bash
# Test network connection
docker exec early-bird-train ping -c 3 trains.ctrip.com
docker exec early-bird-train curl -I https://trains.ctrip.com

# Check DNS
docker exec early-bird-train cat /etc/resolv.conf
```

### 3. Permission Issues

```bash
# Ensure current user is in docker group
sudo usermod -aG docker $USER
# Need to re-login to take effect

# Check log directory permissions
ls -la logs/
chmod 755 logs/
```

### 4. DeepSeek API Error

If you see:
```
WARNING | AI analysis failed, using fallback: Error code: 401
```

**Solution**:
1. Visit https://platform.deepseek.com/
2. Get a new API Key
3. Update `.env` file
4. Restart container:
   ```bash
   docker-compose -f docker/docker-compose.yml restart
   ```

### 5. Email Sending Failed

**Gmail Users**:
1. Enable two-factor authentication
2. Generate "App-specific password": https://myaccount.google.com/apppasswords
3. Use this password to replace `SMTP_PASSWORD` in `.env`

**QQ/163 Mail Users**:
1. Enable SMTP service in email settings
2. Get authorization code
3. Update `.env` configuration

## 🔐 Security Recommendations

### 1. Protect .env File

```bash
# Set only owner can read
chmod 600 .env

# Ensure won't be committed to Git
echo ".env" >> .gitignore
```

### 2. Regular Updates

```bash
# Update system packages
sudo yum update -y

# Update Docker images
docker pull python:3.11-slim
docker-compose -f docker/docker-compose.yml build --no-cache
```

### 3. Setup Firewall

```bash
# AWS Security Group Rules
# - Only allow your IP to access SSH (port 22)
# - Allow outbound HTTPS (443) for API access
# - Allow outbound SMTP (587/465) for sending emails
```

## ⚙️ Advanced Configuration

### Setup Auto-start on Boot

```bash
# Create systemd service
sudo vim /etc/systemd/system/early-bird-train.service
```

Add the following content:

```ini
[Unit]
Description=Early Bird Train Monitoring
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/early-bird-train
ExecStart=/usr/local/bin/docker-compose -f docker/docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker/docker-compose.yml down
User=ec2-user

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable early-bird-train
sudo systemctl start early-bird-train
sudo systemctl status early-bird-train
```

### Setup Log Rotation

```bash
# Create logrotate configuration
sudo vim /etc/logrotate.d/early-bird-train
```

Add the following content:

```
/home/ec2-user/early-bird-train/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 ec2-user ec2-user
}
```

## 📝 Common Commands Quick Reference

```bash
# Start service
docker-compose -f docker/docker-compose.yml up -d

# Stop service
docker-compose -f docker/docker-compose.yml down

# Restart service
docker-compose -f docker/docker-compose.yml restart

# View logs
docker logs -f early-bird-train

# Check status
docker-compose -f docker/docker-compose.yml ps

# Update code and restart
git pull && docker-compose -f docker/docker-compose.yml up -d --build

# Clean everything
docker-compose -f docker/docker-compose.yml down -v
docker system prune -a -f
```

## 🆘 Get Help

If you encounter problems:
1. View logs: `docker logs early-bird-train`
2. Check configuration: `cat .env`
3. Test run: `docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once`
