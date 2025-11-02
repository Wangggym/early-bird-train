# 本地 Docker 测试指南

本指南帮助你在本地使用 Docker 测试项目。

## 📋 前置要求

- Docker 已安装
- Docker Compose 已安装

## 🚀 快速开始

### 1. 配置环境变量

复制配置模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件


### 2. 测试运行一次（推荐）

先测试一次，确保配置正确：

```bash
docker-compose -f docker/docker-compose.yml run --rm early-bird-train python main.py --once
```

你会看到类似输出：
```
INFO | Starting 早起鸟抢票助手...
INFO | Monitoring: C3380 (大邑 -> 成都南)
INFO | Running ticket monitoring once...
INFO | Configured schedule: 周一 at 15:30 (max_retries=5)
INFO | Today: 2025-11-02 (Sunday)
INFO | Calculated target (day 15): 2025-11-16 (Sunday)
INFO | Fetching URL: https://trains.ctrip.com/...
INFO | Successfully fetched 1 train(s)
INFO | Email sent successfully
```

### 3. 启动定时任务

确认测试通过后，启动定时监控：

```bash
# 后台运行
docker-compose -f docker/docker-compose.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.yml down
```

## 🔍 查看日志

日志文件保存在 `./logs` 目录：

```bash
# 查看最新日志
tail -f logs/app.log

# 查看今天的日志
grep "$(date +%Y-%m-%d)" logs/app.log
```

## 🐛 故障排查

### 1. DeepSeek API 401 错误

```
WARNING | AI analysis failed, using fallback: Error code: 401
```

**原因**: API Key 无效

**解决**:
- 访问 https://platform.deepseek.com/ 获取新的 API Key
- 更新 `.env` 中的 `DEEPSEEK_API_KEY`
- 重启容器

### 2. 邮件发送失败

**常见原因**:
- SMTP 密码错误（Gmail 需要使用"应用专用密码"）
- SMTP 服务器地址/端口错误
- 防火墙拦截

**解决**:
- 确认 SMTP 配置正确
- Gmail 用户需要启用"两步验证"并生成"应用专用密码"
- 检查防火墙设置

### 3. 查看容器日志

```bash
# 实时查看日志
docker logs -f early-bird-train

# 查看最近100行
docker logs --tail 100 early-bird-train
```


## 📝 常用命令

```bash
# 重新构建镜像
docker-compose -f docker/docker-compose.yml build

# 查看容器状态
docker-compose -f docker/docker-compose.yml ps

# 停止并删除容器
docker-compose -f docker/docker-compose.yml down

# 查看容器资源占用
docker stats early-bird-train
```

