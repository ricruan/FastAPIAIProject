# 使用官方Python镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# 安装系统依赖（包括 MySQL 开发库和 pkg-config）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        pkg-config \
        libmariadb-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
