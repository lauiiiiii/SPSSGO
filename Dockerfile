FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS worker-runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends docker.io && \
    rm -rf /var/lib/apt/lists/*
