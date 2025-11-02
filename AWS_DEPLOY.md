# AWS 部署指南

本指南帮助你将项目部署到 AWS EC2 服务器。

## 📋 前置条件

- ✅ AWS EC2 实例已创建并运行
- ✅ 已通过 SSH 连接到服务器
- ✅ 服务器已安装 Docker 和 Docker Compose

## 🚀 部署步骤

### 4. 配置环境变量

```bash
# 创建 .env 文件
cp .env.example .env
vim .env
```

### 5. 测试运行

先运行一次测试，确保配置正确：

```bash
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

**预期输出**：
```
INFO | Starting 早起鸟抢票助手...
INFO | Monitoring: C3380 (大邑 -> 成都南)
INFO | Running ticket monitoring once...
INFO | Configured schedule: 周一 at 15:30 (max_retries=5)
INFO | Fetching URL: https://trains.ctrip.com/...
INFO | Successfully fetched 1 train(s)
INFO | Email sent successfully
INFO | Ticket monitoring completed successfully
```

### 6. 启动定时服务

测试通过后，启动定时监控：

```bash
# 启动服务（后台运行）
docker-compose -f docker/docker-compose.yml up -d

# 查看服务状态
docker-compose -f docker/docker-compose.yml ps

# 查看实时日志
docker-compose -f docker/docker-compose.yml logs -f
```

## 📊 监控和维护

### 查看日志

```bash
# 实时查看日志
docker logs -f early-bird-train

# 查看最近 100 行
docker logs --tail 100 early-bird-train

# 查看今天的日志
docker logs early-bird-train 2>&1 | grep "$(date +%Y-%m-%d)"

# 查看日志文件
tail -f logs/app.log
```

### 检查容器状态

```bash
# 查看容器状态
docker ps -a | grep early-bird-train

# 查看资源占用
docker stats early-bird-train

# 查看容器详情
docker inspect early-bird-train
```

### 更新部署

```bash
# 1. 停止容器
docker-compose -f docker/docker-compose.yml down

# 2. 更新代码（选择一种方式）
# 方式1：从本地同步
# rsync -avz --exclude '.git' user@local:/path/to/project/* ./

# 方式2：从 Git 拉取
# git pull origin main

# 3. 重新构建镜像
docker-compose -f docker/docker-compose.yml build --no-cache

# 4. 启动新容器
docker-compose -f docker/docker-compose.yml up -d

# 5. 验证
docker logs -f early-bird-train
```

### 备份和清理

```bash
# 备份日志
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# 清理旧日志（保留最近7天）
find logs/ -name "*.log" -mtime +7 -delete

# 清理 Docker 镜像
docker image prune -a -f

# 查看磁盘占用
df -h
du -sh logs/
```

## 🔧 故障排查

### 1. 容器无法启动

```bash
# 查看错误日志
docker logs early-bird-train

# 检查配置文件
cat .env | grep -v '^#' | grep -v '^$'

# 删除容器重新创建
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d
```

### 2. 网络问题

```bash
# 测试网络连接
docker exec early-bird-train ping -c 3 trains.ctrip.com
docker exec early-bird-train curl -I https://trains.ctrip.com

# 检查 DNS
docker exec early-bird-train cat /etc/resolv.conf
```

### 3. 权限问题

```bash
# 确保当前用户在 docker 组
sudo usermod -aG docker $USER
# 需要重新登录才能生效

# 检查日志目录权限
ls -la logs/
chmod 755 logs/
```

### 4. DeepSeek API 错误

如果看到：
```
WARNING | AI analysis failed, using fallback: Error code: 401
```

**解决方法**：
1. 访问 https://platform.deepseek.com/
2. 获取新的 API Key
3. 更新 `.env` 文件
4. 重启容器：
   ```bash
   docker-compose -f docker/docker-compose.yml restart
   ```

### 5. 邮件发送失败

**Gmail 用户**：
1. 启用两步验证
2. 生成"应用专用密码"：https://myaccount.google.com/apppasswords
3. 使用该密码替换 `.env` 中的 `SMTP_PASSWORD`

**QQ/163 邮箱**：
1. 在邮箱设置中开启 SMTP 服务
2. 获取授权码
3. 更新 `.env` 配置

## 🔐 安全建议

### 1. 保护 .env 文件

```bash
# 设置只有所有者可读
chmod 600 .env

# 确保不会被提交到 Git
echo ".env" >> .gitignore
```

### 2. 定期更新

```bash
# 更新系统包
sudo yum update -y

# 更新 Docker 镜像
docker pull python:3.11-slim
docker-compose -f docker/docker-compose.yml build --no-cache
```

### 3. 设置防火墙

```bash
# AWS 安全组规则
# - 仅允许你的 IP 访问 SSH (22端口)
# - 允许出站 HTTPS (443) 用于访问 API
# - 允许出站 SMTP (587/465) 用于发送邮件
```

## ⚙️ 高级配置

### 设置开机自启

```bash
# 创建 systemd 服务
sudo vim /etc/systemd/system/early-bird-train.service
```

添加以下内容：

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

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable early-bird-train
sudo systemctl start early-bird-train
sudo systemctl status early-bird-train
```

### 设置日志轮转

```bash
# 创建 logrotate 配置
sudo vim /etc/logrotate.d/early-bird-train
```

添加以下内容：

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

## 📝 常用命令速查

```bash
# 启动服务
docker-compose -f docker/docker-compose.yml up -d

# 停止服务
docker-compose -f docker/docker-compose.yml down

# 重启服务
docker-compose -f docker/docker-compose.yml restart

# 查看日志
docker logs -f early-bird-train

# 查看状态
docker-compose -f docker/docker-compose.yml ps

# 更新代码并重启
git pull && docker-compose -f docker/docker-compose.yml up -d --build

# 清理所有
docker-compose -f docker/docker-compose.yml down -v
docker system prune -a -f
```

## 🆘 获取帮助

如遇到问题，请：
1. 查看日志：`docker logs early-bird-train`
2. 检查配置：`cat .env`
3. 测试运行：`docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once`

