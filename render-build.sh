#!/bin/bash

# Upgrade pip
pip install --upgrade pip

# Clean pip cache to save space
pip cache purge

# Install dependencies with no-cache option to save space
pip install --no-cache-dir -r requirements.txt

# Clean any temporary files that might exist
if [ -d "/tmp" ]; then
  find /tmp -type f -atime +1 -delete 2>/dev/null || true
fi

echo "Starting the bot with monitoring..."

# Improved restart logic with exponential backoff
WAIT_TIME=5
MAX_WAIT=300 # 5 minutes max wait
CONSECUTIVE_CRASHES=0

while true; do
    echo "Starting bot with $(free -m | grep Mem | awk '{print $4}')MB free memory..."
    
    # Start time
    START_TIME=$(date +%s)
    
    # Run the bot
    python3 Bot.py
    
    # End time
    END_TIME=$(date +%s)
    RUNTIME=$((END_TIME - START_TIME))
    
    # If the bot ran for more than 5 minutes, reset the crash counter
    if [ $RUNTIME -gt 300 ]; then
        CONSECUTIVE_CRASHES=0
        WAIT_TIME=5
        echo "Bot ran successfully for $(($RUNTIME / 60)) minutes."
    else
        # Bot crashed quickly, increment counter
        CONSECUTIVE_CRASHES=$((CONSECUTIVE_CRASHES + 1))
        
        # Exponential backoff
        WAIT_TIME=$((WAIT_TIME * 2))
        
        # Cap at max wait time
        if [ $WAIT_TIME -gt $MAX_WAIT ]; then
            WAIT_TIME=$MAX_WAIT
        fi
        
        echo "Bot crashed after $RUNTIME seconds! Consecutive crashes: $CONSECUTIVE_CRASHES"
        echo "Waiting $WAIT_TIME seconds before restart..."
        
        # Force garbage collection
        echo "Cleaning up memory..."
        sync
        echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    fi
    
    # Wait before restarting
    sleep $WAIT_TIME
done
