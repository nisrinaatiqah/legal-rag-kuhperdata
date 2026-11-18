FROM python:3.11-slim

WORKDIR /app

# Install dependencies sistem
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install library python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode server dan dataset pendukung
COPY src/ ./src/
COPY data/processed/ ./data/processed/
COPY server.py .

EXPOSE 8080

# Jalankan FastAPI dengan port dinamis untuk Render/Railway/Cloud Run
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
