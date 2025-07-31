FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies in stages
RUN pip install --upgrade pip

# Install core dependencies first
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    gunicorn==21.2.0 \
    python-telegram-bot==20.3 \
    firebase-admin==6.2.0 \
    requests==2.31.0

# Install large packages separately with retries
RUN pip install --no-cache-dir --retries 5 \
    google-api-python-client==2.177.0

# Install remaining dependencies
RUN pip install --no-cache-dir \
    google-cloud-secret-manager==2.16.1 \
    pycryptodome==3.19.0 \
    python-dotenv==1.0.0

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x startup.sh

# Expose the port the app runs on
EXPOSE 8080

# Start the application
CMD ["./startup.sh"]