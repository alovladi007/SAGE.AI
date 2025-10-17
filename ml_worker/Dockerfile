# Dockerfile for ML Worker
# ml_worker/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    tesseract-ocr \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-ml.txt .

# Install Python ML dependencies
RUN pip install --no-cache-dir -r requirements-ml.txt

# Download ML models
RUN mkdir -p /app/models && \
    python -c "from transformers import AutoModel, AutoTokenizer; AutoModel.from_pretrained('allenai/specter2_base'); AutoTokenizer.from_pretrained('allenai/specter2_base')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/temp /app/logs

EXPOSE 8001

CMD ["python", "worker.py"]
