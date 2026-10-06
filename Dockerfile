# Dockerfile for Multi-Source Web Scraping Pipeline
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and tests
COPY . /app/

# Create output and logs volumes/directories
RUN mkdir -p /app/output /app/logs

# Set default execution command
ENTRYPOINT ["python", "main.py"]
CMD ["--max-pages", "3"]
