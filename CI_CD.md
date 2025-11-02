# CI/CD 配置指南

本文档说明如何配置和使用项目的 CI/CD 流程。

---

## 📋 目录

- [概览](#概览)
- [前置要求](#前置要求)
- [配置步骤](#配置步骤)
- [工作流说明](#工作流说明)
- [常见问题](#常见问题)

---

## 🎯 概览

本项目使用 **GitHub Actions** 实现 CI/CD：

### **CI (持续集成)**
- ✅ 代码格式检查 (ruff format)
- ✅ 代码质量检查 (ruff lint)
- ✅ 类型检查 (mypy)
- ✅ 自动化测试 (pytest)
- ✅ 测试覆盖率报告
- ✅ Docker 构建测试

### **CD (持续部署)**
- 🚀 构建 Docker 镜像
- 🚀 推送到 Docker Hub
- 🚀 自动部署到 AWS EC2
- 🚀 健康检查

---

## 📦 前置要求

### 1. Docker Hub 账号

1. 注册 [Docker Hub](https://hub.docker.com/) 账号
2. 创建访问令牌（Token）：
   - 访问：https://hub.docker.com/settings/security
   - 点击 "New Access Token"
   - 名称：`github-actions`
   - 权限：`Read, Write, Delete`
   - 保存生成的 Token（只显示一次）

### 2. AWS EC2 服务器

确保你的 EC2 服务器已：
- ✅ 安装 Docker 和 Docker Compose
- ✅ 从 GitHub 克隆了项目代码
- ✅ 配置了 `.env` 文件
- ✅ 可以通过 SSH 访问

### 3. SSH 密钥

获取 EC2 的 SSH 私钥：
```bash
# 如果使用 AWS 下载的 .pem 文件
cat ~/.ssh/your-key.pem

# 如果使用自己生成的密钥
cat ~/.ssh/id_rsa
```

---

## 🔧 配置步骤

### Step 1: 配置 GitHub Secrets

在你的 GitHub 仓库中配置以下 Secrets：

**路径**: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名 | `your-username` |
| `DOCKERHUB_TOKEN` | Docker Hub 访问令牌 | `dckr_pat_xxxxx...` |
| `AWS_HOST` | EC2 服务器 IP | `52.123.45.67` |
| `AWS_USER` | EC2 登录用户名 | `ec2-user` |
| `AWS_SSH_KEY` | SSH 私钥（完整内容） | `-----BEGIN RSA...` |
| `AWS_PORT` | SSH 端口（可选，默认22） | `22` |

**配置示例**：

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
...完整的私钥内容...
-----END RSA PRIVATE KEY-----

# AWS_PORT (可选)
22
```

### Step 2: 更新 docker-compose.yml

**方案 A：本地修改并推送（推荐）**

在本地修改 `docker/docker-compose.yml`：

```bash
# 在本地电脑
cd /Users/wangyimin/project/early-bird-train
vim docker/docker-compose.yml
```

将第7行改为你的 Docker Hub 用户名：

```yaml
image: your-dockerhub-username/early-bird-train:latest
```

然后推送到 GitHub：

```bash
git add docker/docker-compose.yml
git commit -m "Update docker-compose with Docker Hub username"
git push origin master
```

在服务器上拉取最新配置：

```bash
# SSH 到服务器
ssh ec2-user@your-server-ip
cd ~/early-bird-train
git pull origin master
```

**方案 B：使用环境变量（最佳实践）**

不修改文件，直接在服务器上设置环境变量：

```bash
# SSH 到服务器
ssh ec2-user@your-server-ip

# 设置环境变量（临时）
export DOCKERHUB_USERNAME=your-dockerhub-username

# 或者写入 ~/.bashrc（永久）
echo 'export DOCKERHUB_USERNAME=your-dockerhub-username' >> ~/.bashrc
source ~/.bashrc

# 验证
echo $DOCKERHUB_USERNAME
```

这样 docker-compose.yml 会自动使用环境变量：
```yaml
image: ${DOCKERHUB_USERNAME:-your-dockerhub-username}/early-bird-train:latest
```

### Step 3: 测试 CI/CD

1. **测试 CI**（代码检查）：
   ```bash
   # 推送到任何分支都会触发 CI
   git add .
   git commit -m "Test CI"
   git push origin master
   ```

2. **测试 CD**（构建和部署）：
   ```bash
   # 推送到 master 分支会触发 CD
   git push origin master
   
   # 或者打标签触发
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **查看执行结果**：
   - 访问：`https://github.com/你的用户名/early-bird-train/actions`
   - 查看工作流执行状态

---

## 🔄 工作流说明

### CI 工作流 (`.github/workflows/ci.yml`)

**触发条件**：
- Push 到任何分支
- Pull Request 到 master

**包含 3 个 Job**：

#### 1. Code Quality Checks
```yaml
代码质量检查：
- ruff format --check  # 格式检查
- ruff check          # 代码质量检查
- mypy               # 类型检查
```

#### 2. Run Tests
```yaml
运行测试：
- pytest tests/ -v                    # 运行所有测试
- --cov=src --cov-report=xml         # 生成覆盖率报告
- Upload to Codecov (可选)           # 上传覆盖率
```

#### 3. Test Docker Build
```yaml
测试 Docker 构建：
- 构建镜像但不推送
- 使用 GitHub Actions 缓存加速
```

---

### CD 工作流 (`.github/workflows/cd.yml`)

**触发条件**：
- Push 到 `master` 分支
- 推送 Git Tag (`v*.*.*`)
- 手动触发 (workflow_dispatch)

**包含 3 个 Job**：

#### 1. Build & Push Docker Image
```yaml
构建并推送镜像：
- 登录 Docker Hub
- 构建镜像
- 自动打标签：
  - master → latest
  - v1.0.0 → 1.0.0, 1.0, 1, latest
  - commit → master-abc1234
- 推送到 Docker Hub
```

#### 2. Deploy to AWS EC2
```yaml
部署到 AWS：
- SSH 连接到 EC2
- 拉取最新镜像
- 重启容器
- 清理旧镜像
```

#### 3. Health Check
```yaml
健康检查：
- 等待服务启动
- 检查容器状态
- 输出最新日志
```

---

## 🏷️ 版本管理（Git Tag）

### 创建和推送标签

```bash
# 1. 创建标签
git tag v1.0.0

# 2. 推送标签
git push origin v1.0.0

# 3. 查看所有标签
git tag -l
```

### 标签命名规范

使用 **语义化版本号** (Semantic Versioning)：

```
v<主版本>.<次版本>.<修订号>

v1.0.0  - 初始版本
v1.1.0  - 新增功能
v1.1.1  - Bug 修复
v2.0.0  - 重大更新（不兼容的变更）
```

### Docker 镜像标签映射

| Git Tag | Docker 镜像标签 |
|---------|---------------|
| `v1.2.3` | `1.2.3`, `1.2`, `1`, `latest` |
| `master` | `latest`, `master-abc1234` |
| `develop` | `develop`, `develop-abc1234` |

---

## 🔍 监控和调试

### 查看工作流状态

1. **GitHub Actions 页面**：
   ```
   https://github.com/你的用户名/early-bird-train/actions
   ```

2. **查看某次执行的详细日志**：
   - 点击工作流运行记录
   - 展开各个 Step 查看日志

### 查看 Docker Hub 镜像

```
https://hub.docker.com/r/你的用户名/early-bird-train/tags
```

### 服务器上查看部署状态

```bash
# SSH 到服务器
ssh ec2-user@your-server-ip

# 查看容器状态
docker ps | grep early-bird-train

# 查看日志
docker logs -f early-bird-train

# 查看最近50行日志
docker logs --tail 50 early-bird-train
```

---

## 🐛 常见问题

### 1. CI 失败：代码格式问题

**错误**：
```
Error: ruff format --check failed
```

**解决**：
```bash
# 本地修复格式
make fix

# 提交修复
git add .
git commit -m "Fix code formatting"
git push
```

### 2. CD 失败：Docker Hub 认证失败

**错误**：
```
Error: unauthorized: incorrect username or password
```

**解决**：
1. 检查 `DOCKERHUB_USERNAME` 是否正确
2. 重新生成 `DOCKERHUB_TOKEN`
3. 确保在 GitHub Secrets 中正确配置

### 3. 部署失败：SSH 连接失败

**错误**：
```
Error: ssh: connect to host xxx.xxx.xxx.xxx port 22: Connection refused
```

**解决**：
1. 检查 `AWS_HOST` IP 地址是否正确
2. 检查 EC2 安全组是否允许 GitHub Actions IP（或全部）访问 22 端口
3. 检查 `AWS_SSH_KEY` 私钥格式是否完整

### 4. 部署失败：容器启动失败

**错误**：
```
Error: Container is not running
```

**解决**：
```bash
# SSH 到服务器检查
ssh ec2-user@your-server-ip

# 查看容器日志
docker logs early-bird-train

# 常见原因：
# - .env 文件缺失或配置错误
# - 端口被占用
# - 依赖服务不可用
```

### 5. 镜像拉取失败

**错误**：
```
Error: manifest for xxx/early-bird-train:latest not found
```

**解决**：
1. 确保 CD 工作流成功执行并推送了镜像
2. 检查 Docker Hub 上是否有该镜像
3. 确认 `docker-compose.yml` 中的镜像名称正确

---

## 🚀 手动触发部署

有时你可能需要手动触发部署（不推送代码）：

### 方法 1：通过 GitHub 界面

1. 访问：`Actions` → `CD - Build & Deploy`
2. 点击 `Run workflow`
3. 选择分支：`master`
4. 选择环境：`production`
5. 点击 `Run workflow`

### 方法 2：通过 GitHub CLI

```bash
# 安装 gh CLI
brew install gh  # macOS
# 或访问 https://cli.github.com/

# 登录
gh auth login

# 触发工作流
gh workflow run cd.yml
```

---

## 📊 添加 Badges 到 README

在 `README.md` 顶部添加状态徽章：

```markdown
# 早起鸟抢票助手

[![CI](https://github.com/你的用户名/early-bird-train/workflows/CI%20-%20Code%20Quality%20%26%20Tests/badge.svg)](https://github.com/你的用户名/early-bird-train/actions)
[![CD](https://github.com/你的用户名/early-bird-train/workflows/CD%20-%20Build%20%26%20Deploy/badge.svg)](https://github.com/你的用户名/early-bird-train/actions)
[![Docker](https://img.shields.io/docker/v/你的用户名/early-bird-train?label=docker)](https://hub.docker.com/r/你的用户名/early-bird-train)
```

---

## 🎓 最佳实践

### 1. 分支策略

```
master (生产环境)
  ↑
develop (开发环境)
  ↑
feature/* (功能分支)
```

### 2. 提交前本地检查

```bash
# 运行所有检查
make check

# 运行测试
make test

# 修复格式问题
make fix
```

### 3. 版本发布流程

```bash
# 1. 确保在 master 分支
git checkout master
git pull

# 2. 创建标签
git tag v1.0.0

# 3. 推送标签（触发 CD）
git push origin v1.0.0

# 4. 在 GitHub 创建 Release（可选）
gh release create v1.0.0 --generate-notes
```

### 4. 回滚部署

如果新版本有问题，快速回滚：

```bash
# 方法1：在服务器上手动回滚
ssh ec2-user@your-server-ip
docker-compose -f docker/docker-compose.yml pull your-username/early-bird-train:v1.0.0
docker-compose -f docker/docker-compose.yml up -d

# 方法2：推送旧版本标签
git tag v1.0.1 v1.0.0^{}  # 基于旧版本创建新标签
git push origin v1.0.1
```

---

## 📞 获取帮助

- **GitHub Actions 文档**: https://docs.github.com/actions
- **Docker Hub 文档**: https://docs.docker.com/docker-hub/
- **问题反馈**: 在 GitHub Issues 中提问

---

最后更新：2025-11-02

