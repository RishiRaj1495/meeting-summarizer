FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY .env.example .

# Streamlit config — headless, no CORS/XSRF
RUN mkdir -p /root/.streamlit && \
    printf '[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\n' \
    > /root/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# KEY FIX: Use CMD + shell form so $PORT env var is expanded at runtime.
# Render injects $PORT dynamically — ENTRYPOINT with exec form can't expand it.
CMD streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=${PORT:-8501} \
    --server.headless=true
