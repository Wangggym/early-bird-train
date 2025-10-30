# 早起鸟抢票助手 🚄

携程火车票余票监控和AI分析系统，采用企业级架构设计。

## ✨ 特性

- 🎯 **精准监控**：每周一15:30自动抓取15天后的车票
- 🤖 **AI分析**：DeepSeek智能分析余票情况
- 📧 **邮件通知**：精美HTML格式邮件推送
- 🏗️ **企业架构**：面向对象、依赖注入、强类型
- 🐳 **容器部署**：Docker一键部署
- 📊 **全面日志**：结构化日志，便于追踪

## 🏛️ 架构设计

```
分层架构 (Clean Architecture)
├── Domain Layer (领域层)
│   ├── Models (Pydantic强类型模型)
│   ├── Interfaces (抽象接口)
│   └── Exceptions (领域异常)
├── Application Layer (应用层)
│   └── Services (用例服务)
├── Infrastructure Layer (基础设施层)
│   ├── Crawler (携程爬虫)
│   ├── Analyzer (DeepSeek分析)
│   ├── Notifier (邮件通知)
│   └── Scheduler (定时调度)
└── Container (依赖注入容器)
```

### 设计原则

- ✅ **SOLID原则**
- ✅ **依赖倒置**（面向接口编程）
- ✅ **依赖注入**（使用dependency-injector）
- ✅ **强类型**（全面使用Type Hints + Pydantic）
- ✅ **单一职责**（每个类只做一件事）

## 🚀 快速开始

> 📖 详细教程请查看 [QUICKSTART.md](QUICKSTART.md)

### 1. 初始化环境

```bash
make gen
source .venv/bin/activate
```

### 2. 配置环境变量

```bash
cp .env.example .env
vim .env  # 填写 DEEPSEEK_API_KEY, SMTP配置, EMAIL_TO
```

### 3. 运行

```bash
# 开发测试（运行一次）
make dev

# 生产运行（定时调度）
make run

# Docker部署
make docker-build
make docker-up
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `make gen` | 初始化环境 |
| `make fix` | 格式化代码 |
| `make check` | 类型检查 |
| `make dev` | 开发测试 |
| `make help` | 查看所有命令 |

## 🐳 Docker部署

### 构建并运行

```bash
cd docker
docker-compose up -d
```

### 查看日志

```bash
docker-compose logs -f
```

### 停止服务

```bash
docker-compose down
```

## 📁 项目结构

```
early-bird-train/
├── src/
│   ├── domain/              # 领域层
│   │   ├── models.py       # 数据模型（Pydantic）
│   │   ├── interfaces.py   # 抽象接口（ABC）
│   │   └── exceptions.py   # 领域异常
│   ├── application/         # 应用层
│   │   └── ticket_service.py  # 监控服务
│   ├── infrastructure/      # 基础设施层
│   │   ├── crawler.py      # 携程爬虫实现
│   │   ├── analyzer.py     # DeepSeek分析实现
│   │   ├── notifier.py     # 邮件通知实现
│   │   └── scheduler.py    # 定时调度实现
│   ├── config/             # 配置管理
│   │   └── settings.py     # Pydantic Settings
│   └── container.py        # 依赖注入容器
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── logs/                   # 日志目录
├── data/                   # 数据目录
├── main.py                 # 程序入口
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## 🔧 配置说明

### 监控配置

```env
DEPARTURE_STATION=大邑      # 出发站
ARRIVAL_STATION=成都南       # 到达站
TRAIN_NUMBER=C3380          # 车次号
DAYS_AHEAD=15               # 提前天数
```

### 调度配置

```env
SCHEDULE_DAY_OF_WEEK=0      # 0=周一, 6=周日
SCHEDULE_HOUR=15            # 小时（0-23）
SCHEDULE_MINUTE=30          # 分钟（0-59）
```

### DeepSeek配置

```env
DEEPSEEK_API_KEY=sk-xxx     # API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 邮件配置

```env
SMTP_HOST=smtp.gmail.com    # SMTP服务器
SMTP_PORT=587               # SMTP端口
SMTP_USER=your@gmail.com    # 用户名
SMTP_PASSWORD=app_password  # 密码/应用专用密码
EMAIL_FROM=your@gmail.com   # 发件人
EMAIL_TO=["recipient@example.com"]  # 收件人（JSON数组）
```

## 📊 日志

日志文件位于 `logs/` 目录：
- 按天轮转
- 保留30天
- 自动压缩

查看日志：
```bash
tail -f logs/app_$(date +%Y-%m-%d).log
```

## 🧪 测试

```bash
# 运行测试（TODO）
pytest

# 类型检查
mypy src/
```

## 🔮 未来计划

- [ ] FastAPI接口服务
- [ ] 数据持久化（PostgreSQL）
- [ ] 多车次监控
- [ ] Web管理界面
- [ ] browser-use自动购票

## 📝 开发指南

### 添加新的爬虫实现

1. 实现 `ITicketCrawler` 接口
2. 在 `container.py` 中注册
3. 无需修改其他代码

### 添加新的通知方式

1. 实现 `INotifier` 接口
2. 在 `container.py` 中注册
3. 支持多个通知器并行

## 📄 许可证

MIT License

## 🙏 致谢

- [Pydantic](https://pydantic.dev/) - 数据验证
- [dependency-injector](https://python-dependency-injector.ets-labs.org/) - 依赖注入
- [APScheduler](https://apscheduler.readthedocs.io/) - 任务调度
- [DeepSeek](https://www.deepseek.com/) - AI分析
