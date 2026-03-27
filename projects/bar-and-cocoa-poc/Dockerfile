FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Expose port (Railway overrides with $PORT)
EXPOSE 8080

# Start Chainlit
CMD chainlit run app.py --host 0.0.0.0 --port ${PORT:-8080} -h
