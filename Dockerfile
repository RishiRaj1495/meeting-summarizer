# ─────────────────────────────────────────────────────────────────
# Meeting Summarizer — Dockerfile
# Supports: Whisper (audio), pdfplumber (PDF), python-docx (DOCX),
#           pytesseract (image OCR), Streamlit UI
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY app.py .
COPY .env.example .env.example

# Streamlit configuration
RUN mkdir -p /root/.streamlit
RUN echo '[server]\nheadless = true\nport = 8501\nenableCORS = false\nenableXsrfProtection = false\n' \
    > /root/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
