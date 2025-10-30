# 快速开始指南 🚀

## 1️⃣ 初始化环境

```bash
make gen
```

这会：
- 删除旧的虚拟环境
- 创建新的Python 3.12虚拟环境
- 安装所有依赖

**然后激活环境**：
```bash
source .venv/bin/activate
```

## 2️⃣ 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env
```

**必填项**：
- `DEEPSEEK_API_KEY`: 在 https://platform.deepseek.com/ 获取
- `SMTP_*`: 邮箱SMTP配置
- `EMAIL_TO`: 收件人邮箱（JSON数组格式）

**SMTP配置示例**：

### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # 需要在Gmail设置中生成应用专用密码
EMAIL_FROM=your_email@gmail.com
```

### QQ邮箱
```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=授权码  # 在QQ邮箱设置中生成授权码（16位，不是QQ密码）
EMAIL_FROM=your_email@qq.com
```

### 163邮箱
```env
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your_email@163.com
SMTP_PASSWORD=授权码
EMAIL_FROM=your_email@163.com
```

## 3️⃣ 开发测试

### 运行一次测试
```bash
make dev
```
这会立即执行一次爬取和分析，验证配置是否正确。

### 代码格式化
```bash
make fix
```

### 类型检查
```bash
make check
```

## 4️⃣ 本地运行

```bash
make run
```
这会启动定时调度器，每周一15:30自动执行。

**按 Ctrl+C 停止**

## 5️⃣ Docker部署（推荐）

### 构建镜像
```bash
make docker-build
```

### 启动容器
```bash
make docker-up
```

### 查看日志
```bash
make docker-logs
```

### 停止容器
```bash
make docker-down
```

## 📝 常用命令

| 命令 | 说明 |
|------|------|
| `make gen` | 初始化虚拟环境 |
| `make fix` | 格式化代码 |
| `make check` | 类型检查 |
| `make dev` | 开发测试（运行一次） |
| `make run` | 生产运行（定时调度） |
| `make docker-build` | 构建Docker镜像 |
| `make docker-up` | 启动Docker容器 |
| `make docker-down` | 停止Docker容器 |
| `make docker-logs` | 查看容器日志 |
| `make clean` | 清理临时文件 |
| `make help` | 查看帮助 |

## 🔍 验证部署

### 检查日志
```bash
# 本地运行
tail -f logs/app_$(date +%Y-%m-%d).log

# Docker运行
make docker-logs
```

### 测试邮件
成功运行后，你应该会收到一封包含车票信息的邮件。

## ⚠️ 常见问题

### 1. DeepSeek API密钥错误
确保在 https://platform.deepseek.com/ 正确获取API密钥

### 2. 邮件发送失败
- Gmail需要开启"不够安全的应用访问"或使用应用专用密码
- QQ/163邮箱需要使用授权码，不是登录密码

### 3. 找不到车次
- 确认车次号正确（如 C3380）
- 确认日期格式正确（YYYY-MM-DD）
- 检查网络连接

### 4. 类型检查失败
安装开发依赖：
```bash
source .venv/bin/activate
uv pip install ruff mypy
```

## 📅 修改调度时间

编辑 `.env` 文件：

```env
# 每周一 15:30
SCHEDULE_DAY_OF_WEEK=0  # 0=周一, 1=周二, ..., 6=周日
SCHEDULE_HOUR=15
SCHEDULE_MINUTE=30
```

## 🎯 下一步

- [ ] 监控日志确保正常运行
- [ ] 根据实际情况调整配置
- [ ] 添加更多通知方式（微信、Telegram）
- [ ] 部署到云服务器

