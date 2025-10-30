FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY main.py .

# 创建日志和数据目录
RUN mkdir -p /app/logs /app/data

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行应用
CMD ["python", "main.py"]

