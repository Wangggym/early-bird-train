# 📋 Early Bird Train - TODO List

## ✅ 已完成任务 (2025-10-30)

### 1. 核心功能实现
- [x] **爬虫模块** - 携程火车票数据抓取
  - [x] 解析 Next.js `__NEXT_DATA__` JSON 数据
  - [x] 支持指定车次查询（C3380）
  - [x] 解析座位信息（类型、价格、余票、可订性）
  - [x] 错误处理和日志记录

- [x] **数据分析模块** - AI/规则分析
  - [x] DeepSeek AI 智能分析（可选）
  - [x] 规则判断降级方案（无需 API）
  - [x] 判断是否有坐票（非站票）

- [x] **邮件通知模块** - QQ邮箱 SMTP
  - [x] HTML 格式邮件模板
  - [x] 车次、座位、价格信息展示
  - [x] SSL/STARTTLS 连接支持
  - [x] 处理 QQ 邮箱 quit 时的 SSL 错误

- [x] **定时任务模块** - APScheduler
  - [x] 每周一 15:30 自动运行
  - [x] 提前 15 天查询下周一的票
  - [x] 可配置调度时间

### 2. 架构设计
- [x] **Clean Architecture** 分层设计
  - [x] Domain 层：模型、接口、异常
  - [x] Infrastructure 层：爬虫、AI、邮件、调度
  - [x] Application 层：业务逻辑服务
  - [x] Config 层：配置管理

- [x] **依赖注入** (dependency-injector)
  - [x] 容器配置
  - [x] 服务解耦
  - [x] 易于测试和维护

- [x] **强类型系统**
  - [x] Pydantic 模型验证
  - [x] Type Hints 类型标注
  - [x] mypy 类型检查配置

### 3. 开发工具
- [x] **包管理** - uv
  - [x] 快速依赖安装
  - [x] 虚拟环境管理
  - [x] pyproject.toml 配置

- [x] **代码质量**
  - [x] ruff 格式化和 lint
  - [x] mypy 类型检查
  - [x] 自动化 Makefile

- [x] **文档**
  - [x] README.md - 项目介绍
  - [x] QUICKSTART.md - 快速开始
  - [x] .env.example - 配置模板
  - [x] 代码注释和类型标注

### 4. 部署支持
- [x] **Docker 容器化**
  - [x] Dockerfile
  - [x] docker-compose.yml
  - [x] 环境变量配置

- [x] **配置管理**
  - [x] .env 环境变量
  - [x] Pydantic Settings
  - [x] .gitignore 敏感信息保护

### 5. 测试和调试
- [x] **测试脚本**
  - [x] test_crawler.py - 爬虫测试（无需完整配置）
  - [x] make test-crawler 命令
  
- [x] **日志系统**
  - [x] loguru 日志记录
  - [x] 彩色输出
  - [x] 文件日志（logs/）

### 6. 新功能实现 (2025-11-02)
- [x] **斐波那契退避重试机制**
  - [x] 查询失败自动重试（1s, 1s, 2s, 3s, 5s...）
  - [x] 可配置重试次数（MAX_RETRIES）
  - [x] 智能退避策略避免频繁请求

- [x] **多日期调度支持**
  - [x] 支持多个工作日调度（周一、周三、周五等）
  - [x] JSON数组配置格式（SCHEDULE_DAYS_OF_WEEK）
  - [x] 灵活的时间配置

- [x] **日期计算修复**
  - [x] 修正 DAYS_AHEAD 语义（今天算第1天）
  - [x] 移除自动调整到周一的逻辑
  - [x] 精确查询指定日期的车票

- [x] **调试增强**
  - [x] 打印查询 URL 方便验证
  - [x] 显示今天日期和目标日期
  - [x] 详细的日志输出

### 7. 完整测试套件 (2025-11-02)
- [x] **单元测试**
  - [x] pytest 测试框架
  - [x] 爬虫模块测试（test_crawler.py）
  - [x] 分析器模块测试（test_analyzer.py）
  - [x] 通知模块测试（test_notifier.py）
  - [x] 调度器模块测试（test_scheduler.py）
  - [x] 业务服务测试（test_ticket_service.py）
  - [x] Mock 外部依赖（HTTP、SMTP、OpenAI）

- [x] **测试工具**
  - [x] pytest-cov 代码覆盖率
  - [x] pytest-mock Mock 工具
  - [x] pytest-xdist 并行测试
  - [x] Makefile 测试命令

### 8. 部署文档 (2025-11-02)
- [x] **本地 Docker 测试**
  - [x] LOCAL_DOCKER_TEST.md 详细指南
  - [x] 一键测试命令
  - [x] 故障排查说明

- [x] **AWS 部署**
  - [x] AWS_DEPLOY.md 完整指南
  - [x] 上传代码方案（rsync/scp/Git）
  - [x] Docker 环境配置
  - [x] 开机自启配置
  - [x] 日志轮转配置

- [x] **Bug 修复**
  - [x] 修复 .gitignore 忽略 crawler.py 问题
  - [x] 添加 .dockerignore 确保正确构建
  - [x] 服务器部署问题排查

---

## 🚀 正在进行的任务

### 当前优先级 (P0)

- [ ] **持续集成和部署 (CI/CD)**
  - [ ] GitHub Actions 工作流配置
  - [ ] 自动化测试运行
  - [ ] Docker 镜像自动构建
  - [ ] 自动部署到 AWS
  - [ ] 代码质量检查（ruff, mypy）

- [ ] **DeepSeek API 配置**
  - [ ] 获取 DeepSeek API Key
  - [ ] 测试 AI 分析功能
  - [ ] 优化 prompt 提升准确度
  - [ ] 监控 API 调用情况

---

## 🚀 未来改进计划

### 短期优化 (P1)

- [x] ~~**增强爬虫稳定性**~~
  - [x] ~~添加重试机制（网络失败时）~~ ✅ 已完成（斐波那契退避）
  - [ ] 请求频率限制（避免被封）
  - [ ] User-Agent 轮换
  - [ ] Cookie 管理

- [ ] **邮件模板优化**
  - [ ] 添加票价趋势图
  - [ ] 支持多车次对比
  - [ ] 紧急票提醒高亮

### 中期功能 (P2)

- [ ] **数据持久化**
  - [ ] SQLite 存储历史查询
  - [ ] 票价变化趋势分析
  - [ ] 余票变化监控

- [ ] **多通知渠道**
  - [ ] 微信通知（企业微信 Webhook）
  - [ ] Telegram Bot
  - [ ] Slack 集成
  - [ ] 短信通知（阿里云/腾讯云）

- [ ] **Web 界面** (FastAPI)
  - [ ] 查询历史记录
  - [ ] 实时余票查看
  - [ ] 配置管理界面
  - [ ] 监控多个车次

- [x] ~~**单元测试**~~ ✅ 已完成
  - [x] pytest 测试框架
  - [x] 爬虫模块测试
  - [x] 服务层测试
  - [x] Mock 外部依赖

### 长期规划 (P3)

- [ ] **自动抢票功能**
  - [ ] browser-use AI 自动化
  - [ ] 模拟登录携程
  - [ ] 自动下单流程
  - [ ] 支付提醒

- [ ] **多用户支持**
  - [ ] 用户认证系统
  - [ ] 个性化监控设置
  - [ ] 独立通知配置

- [ ] **智能推荐**
  - [ ] 基于历史数据的票价预测
  - [ ] 最佳购票时机推荐
  - [ ] 备选方案推荐（中转）

- [ ] **性能优化**
  - [ ] 异步并发爬取
  - [ ] 缓存机制
  - [ ] 分布式部署

---

## 🐛 已知问题

### 已解决
- [x] ~~QQ 邮箱 SSL quit 错误~~ → 使用 try-except 忽略
- [x] ~~Gmail SMTP 连接超时~~ → 改用 QQ 邮箱
- [x] ~~爬虫解析失败~~ → 修正 JSON 字段名 (trainInfoList)
- [x] ~~.gitignore 误删 crawler.py~~ → 改为 /crawler.py 只忽略根目录
- [x] ~~Docker 构建缺少文件~~ → 添加 .dockerignore
- [x] ~~日期计算不准确~~ → 修正为 today + (days_ahead - 1)
- [x] ~~自动调整到周一~~ → 移除该逻辑

### 待观察
- [ ] 大邑站 15:30 准时开售的稳定性
- [ ] 爬虫在高并发时的表现
- [ ] 邮件发送的成功率
- [ ] AWS 服务器定时任务稳定性

---

## 📊 项目进展总结

### 完成情况（截至 2025-11-02）
- **开发周期**: 4天（10-30 至 11-02）
- **代码行数**: ~3000+行（含测试）
- **Python 文件**: 25+个
- **测试覆盖率**: 核心模块全覆盖

### 技术栈
- **语言**: Python 3.11/3.12
- **框架**: APScheduler, Pydantic
- **爬虫**: Requests, BeautifulSoup4, lxml
- **AI**: OpenAI SDK (DeepSeek)
- **邮件**: SMTP (支持 Gmail/QQ/163/阿里云)
- **容器**: Docker, Docker Compose
- **测试**: pytest, pytest-cov, pytest-mock, pytest-xdist
- **工具**: uv, ruff, mypy, loguru

### 核心亮点
1. ✨ **架构清晰** - Clean Architecture + DI
2. ✨ **类型安全** - 全面类型标注
3. ✨ **易于维护** - 代码质量高
4. ✨ **开箱即用** - Makefile + Docker
5. ✨ **文档完善** - README + 部署指南
6. ✨ **测试完善** - 单元测试全覆盖
7. ✨ **智能重试** - 斐波那契退避策略
8. ✨ **灵活调度** - 多日期支持

### 最近更新（2025-11-02）
- ✅ 添加完整测试套件
- ✅ 实现斐波那契退避重试
- ✅ 支持多日期调度
- ✅ 修复日期计算逻辑
- ✅ 完善部署文档
- ✅ 修复 .gitignore 和 Docker 构建问题

### 下一步行动
1. 🔄 配置 CI/CD 自动化部署
2. 🤖 配置 DeepSeek AI 分析
3. 📊 收集运行数据，优化策略
4. 🚀 监控生产环境运行状态

---

## 📞 支持信息

- **项目仓库**: (待填写)
- **问题反馈**: (待填写)
- **更新日志**: 见 Git commit history

最后更新：2025-11-02

