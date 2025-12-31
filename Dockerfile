FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .

# Upgrade pip and install dependencies with retry logic and verbose output
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 --retries 5 -v -r requirements.txt

# Copy application code
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run uvicorn directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
