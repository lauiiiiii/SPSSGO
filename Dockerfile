FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# R 增强分析在容器里必须可用；jsonlite/lavaan 用系统包安装，部署时别再临时拉 CRAN。
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        r-base \
        r-cran-jsonlite \
        r-cran-lavaan && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./spssgo-reqs.txt
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r spssgo-reqs.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 120

COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./
COPY frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS worker-runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends docker.io && \
    rm -rf /var/lib/apt/lists/*
