# Quick Start Guide 🚀

## 1️⃣ Initialize Environment

```bash
make gen
```

This will:
- Delete old virtual environment
- Create new Python 3.12 virtual environment
- Install all dependencies

**Then activate environment**:
```bash
source .venv/bin/activate
```

## 2️⃣ Configure Environment Variables

```bash
# Copy configuration template
cp .env.example .env

# Edit configuration
vim .env
```

**Required**:
- `DEEPSEEK_API_KEY`: Get from https://platform.deepseek.com/
- `SMTP_*`: Email SMTP configuration
- `EMAIL_TO`: Recipient email (JSON array format)

**SMTP Configuration Examples**:

### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Need to generate app-specific password in Gmail settings
EMAIL_FROM=your_email@gmail.com
```

### QQ Mail
```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=authorization_code  # Generate authorization code in QQ Mail settings (16 digits, not QQ password)
EMAIL_FROM=your_email@qq.com
```

### 163 Mail
```env
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your_email@163.com
SMTP_PASSWORD=authorization_code
EMAIL_FROM=your_email@163.com
```

## 3️⃣ Development Testing

### Run Test Once
```bash
make dev
```
This will immediately execute one crawl and analysis to verify configuration is correct.

### Code Formatting
```bash
make fix
```

### Type Checking
```bash
make check
```

## 4️⃣ Local Run

```bash
make run
```
This will start the scheduled task scheduler, automatically executing every Monday at 15:30.

**Press Ctrl+C to stop**

## 5️⃣ Docker Deployment (Recommended)

### Build Image
```bash
make docker-build
```

### Start Container
```bash
make docker-up
```

### View Logs
```bash
make docker-logs
```

### Stop Container
```bash
make docker-down
```

## 📝 Common Commands

| Command | Description |
|---------|-------------|
| `make gen` | Initialize virtual environment |
| `make fix` | Format code |
| `make check` | Type checking |
| `make dev` | Development test (run once) |
| `make run` | Production run (scheduled) |
| `make docker-build` | Build Docker image |
| `make docker-up` | Start Docker container |
| `make docker-down` | Stop Docker container |
| `make docker-logs` | View container logs |
| `make clean` | Clean temporary files |
| `make help` | View help |

## 🔍 Verify Deployment

### Check Logs
```bash
# Local run
tail -f logs/app_$(date +%Y-%m-%d).log

# Docker run
make docker-logs
```

### Test Email
After successful run, you should receive an email containing ticket information.

## ⚠️ Common Issues

### 1. DeepSeek API Key Error
Ensure you correctly get the API key from https://platform.deepseek.com/

### 2. Email Sending Failed
- Gmail needs to enable "Less secure app access" or use app-specific password
- QQ/163 Mail needs to use authorization code, not login password

### 3. Train Not Found
- Confirm train number is correct (e.g., C3380)
- Confirm date format is correct (YYYY-MM-DD)
- Check network connection

### 4. Type Check Failed
Install development dependencies:
```bash
source .venv/bin/activate
uv pip install ruff mypy
```

## 📅 Modify Schedule Time

Edit `.env` file:

```env
# Every Monday 15:30
SCHEDULE_DAYS_OF_WEEK=[0]  # 0=Monday, 1=Tuesday, ..., 6=Sunday
SCHEDULE_HOUR=15
SCHEDULE_MINUTE=30
```

## 🎯 Next Steps

- [ ] Monitor logs to ensure normal operation
- [ ] Adjust configuration based on actual situation
- [ ] Add more notification methods (WeChat, Telegram)
- [ ] Deploy to cloud server
