#!/bin/bash

# Usage information
usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  logs    - View bot logs"
    echo "  status  - Check bot status"
    echo "  restart - Restart the bot"
    echo "  update  - Rebuild and update the bot"
    echo "  stop    - Stop the bot"
    echo "  start   - Start the bot"
    echo "  cleanup - Remove temporary files"
    exit 1
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    usage
fi

# Function to handle different commands
case "$1" in
    logs)
        echo "Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    status)
        echo "Bot status:"
        docker-compose ps
        echo -e "\nContainer resources:"
        docker stats --no-stream $(docker-compose ps -q)
        echo -e "\nDisk space:"
        df -h /tmp
        ;;
    restart)
        echo "Restarting bot..."
        docker-compose restart
        echo "Bot restarted. Check status with: $0 status"
        ;;
    update)
        echo "Updating bot..."
        docker-compose down
        docker-compose build
        docker-compose up -d
        echo "Bot updated and restarted."
        ;;
    stop)
        echo "Stopping bot..."
        docker-compose down
        echo "Bot stopped."
        ;;
    start)
        echo "Starting bot..."
        docker-compose up -d
        echo "Bot started. Check status with: $0 status"
        ;;
    cleanup)
        echo "Cleaning up temporary files..."
        find /tmp -name "doujin_*" -type d -mtime +1 -exec rm -rf {} \; 2>/dev/null || true
        echo "Temporary files cleaned up."
        ;;
    *)
        echo "Unknown command: $1"
        usage
        ;;
esac
