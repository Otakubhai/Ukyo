FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create a volume for temporary storage
VOLUME ["/tmp"]

# Environment variables will be provided via docker-compose or command line
ENV BOT_TOKEN=""
ENV TEMP_DIR="/tmp"

# Run the bot
CMD ["python", "merged_bot.py"]
