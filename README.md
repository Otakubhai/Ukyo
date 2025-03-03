# Anime & Doujin Telegram Bot

This Telegram bot allows users to:
1. Get anime information with the `/anime <name>` command
2. Download doujins as PDFs with the `/get_doujin <URL>` command

## Features

- Docker support for easy deployment
- Environment variable configuration
- No limits on PDF page count
- Preserves original image quality and aspect ratio
- Optimized for VPS deployment
- Asynchronous operation for better performance
- Detailed logging

## Deployment Instructions

### Prerequisites

- Docker and Docker Compose installed on your VPS
- A valid Telegram Bot Token (obtained from @BotFather)

### Configuration

1. Clone this repository to your VPS:
   ```
   git clone https://your-repository-url.git
   cd your-repository-directory
   ```

2. Rename the files:
   ```
   mv optimized_bot.py merged_bot.py
   mv optimized_pdf_generator.py pdf_generator.py
   mv updated_requirements.txt requirements.txt
   ```

3. Edit the `.env` file and add your Telegram Bot Token:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   TEMP_DIR=/tmp
   ```

### Deployment

1. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

2. Check the logs to ensure everything is running correctly:
   ```
   docker-compose logs -f
   ```

### Updating

To update the bot after making changes:

```
docker-compose down
docker-compose build
docker-compose up -d
```

### Monitoring

View logs:
```
docker-compose logs -f
```

Check container status:
```
docker-compose ps
```

## Performance Optimization

The bot has been optimized for VPS deployment with:

- Asynchronous image downloading with rate limiting to prevent overloading
- Efficient memory management with garbage collection
- Temporary file cleanup after operations
- Error handling and recovery
- Configurable temporary directory

## Usage

After deploying the bot, users can interact with it using:

- `/start` - Get information about the bot
- `/anime <name>` - Search for anime information
- `/get_doujin <URL>` - Download a doujin from Multporn.net as a PDF

## Troubleshooting

If you encounter issues:

1. Check logs with `docker-compose logs`
2. Ensure your bot token is correct
3. Verify that the VPS has enough disk space
4. Check internet connectivity
