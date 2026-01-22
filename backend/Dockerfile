FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && (apt-get install -y --no-install-recommends linux-perf || apt-get install -y --no-install-recommends linux-tools-common) \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including dev dependencies for testing)
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application
COPY . .

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
