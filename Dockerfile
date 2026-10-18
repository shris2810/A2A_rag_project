# Use official slim Python 3.11 runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=10000

# Install system dependencies:
# - build-essential: compiler tools for C extensions
# - curl: used in start.sh health check probe
# - net-tools: provides netstat command used in main.py
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Sanitize Windows CRLF line endings to Linux LF and set execution permissions on start.sh
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose web service port
EXPOSE 10000

# Run startup supervisor
CMD ["./start.sh"]
