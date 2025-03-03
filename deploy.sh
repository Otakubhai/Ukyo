#!/bin/bash

# Make sure the script exits on any error
set -e

echo "===== Deploying Telegram Bot ====="

# Rename optimized files to their original names
echo "Preparing files..."
if [ -f "optimized_bot.py" ]; then
    mv optimized_bot.py merged_bot.py
fi

if [ -f "optimized_pdf_generator.py" ]; then
    mv optimized_pdf_generator.py pdf_generator.py
fi

if [ -f "updated_requirements.txt" ]; then
    mv updated_requirements.txt requirements.txt
fi

# Check if .env file exists, if not, create it
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "BOT_TOKEN=" > .env
    echo "TEMP_DIR=/tmp" >> .env
    echo "Please edit .env file and add your bot token."
else
    echo ".env file already exists."
fi

# Make sure the bot token is set
if grep -q "BOT_TOKEN=$" .env; then
    echo "WARNING: Bot token not set in .env file. Please edit the file and add your token."
    exit 1
fi

# Build and run the containers
echo "Building and starting Docker containers..."
docker-compose down
docker-compose build
docker-compose up -d

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo "===== Deployment successful! ====="
    echo "The bot is now running. Check logs with: docker-compose logs -f"
else
    echo "===== Deployment failed! ====="
    echo "Please check the logs for more information."
fi
