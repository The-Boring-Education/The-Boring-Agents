# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .
COPY src/ ./src/
COPY run.py .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p output temp logs

# Expose the API port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "run.py"]

