#!/bin/bash

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Starting the bot with auto-restart..."

# Run the bot in a loop to auto-restart if it crashes
while true; do
    python3 Bot.py  # Use 'python3' for compatibility
    echo "Bot crashed! Restarting in 5 seconds..."
    sleep 5
done
