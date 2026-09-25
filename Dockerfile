FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (libgomp needed by duckdb, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Pre-install DuckDB httpfs extension at build time so runtime is offline-safe
RUN python -c "import duckdb; c = duckdb.connect(); c.execute('INSTALL httpfs'); c.execute('LOAD httpfs'); print('httpfs pre-installed')"

# Copy app code
COPY . .

# Render injects $PORT; default to 10000 for local docker runs
ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --timeout-keep-alive 30"]
