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
RUN python -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('allenai/specter2'); \
    model.save('/app/models/specter2')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/temp /app/logs

EXPOSE 8001

CMD ["python", "worker.py"]
