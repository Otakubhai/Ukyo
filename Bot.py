import os
import subprocess

# Fetch the bot token from environment variables
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

# Automatically install dependencies if missing
try:
    import requests
    from bs4 import BeautifulSoup
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
except ImportError:
    subprocess.run(["pip", "install", "--upgrade", "pip"])
    subprocess.run(["pip", "install", "requests", "beautifulsoup4", "python-telegram-bot"])

    # Retry import after installation
    import requests
    from bs4 import BeautifulSoup
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Initialize bot
bot = Bot(token=TOKEN)

# Folder to store images
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context):
    """Handles the /start command"""
    await update.message.reply_text("Send me a Multporn.net link to download images.")

async def fetch_gallery(update: Update, context):
    """Handles downloading and sending images from a Multporn gallery."""
    url = update.message.text.strip()

    if not url.startswith("https://multporn.net/"):
        await update.message.reply_text("Invalid URL. Please send a valid Multporn.net link.")
        return

    await update.message.reply_text(f"Fetching images from: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all image URLs
        images = [img.get("src") for img in soup.find_all("img") if img.get("src") and "multporn.net" in img.get("src")]

        if not images:
            await update.message.reply_text("No images found on this page.")
            return

        await update.message.reply_text(f"Found {len(images)} images. Downloading...")

        # Download images
        image_paths = []
        for index, img_url in enumerate(images):
            filename = os.path.join(DOWNLOAD_DIR, f"image_{index+1}.jpg")
            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as img_file:
                    img_file.write(img_data)
                image_paths.append(filename)
            except requests.exceptions.RequestException:
                continue  # Skip failed downloads

        if not image_paths:
            await update.message.reply_text("Failed to download images.")
            return

        await update.message.reply_text("Uploading images to Telegram...")

        # Send images as documents to avoid compression
        for img_path in image_paths:
            await update.message.reply_document(document=open(img_path, "rb"))

        await update.message.reply_text("Done! All images sent.")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def cancel(update: Update, context):
    """Handles /cancel command"""
    await update.message.reply_text("Process canceled.")

def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_gallery))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
