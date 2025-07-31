# Use the official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Google Cloud credentials path
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json

# Expose the port the app runs on
EXPOSE 8080

# Start the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 flask_app:app