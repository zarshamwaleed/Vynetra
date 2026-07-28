FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    graphviz \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base AS development

COPY requirements-dev.txt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN mkdir -p /app/generated /app/assets /app/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
