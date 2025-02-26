import os
import subprocess

# Ensure dependencies are installed
try:
    import requests
    from bs4 import BeautifulSoup
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
except ImportError:
    subprocess.run(["pip", "install", "--upgrade", "pip"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    # Retry imports after installation
    import requests
    from bs4 import BeautifulSoup
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

from pdf_generator import create_pdf  # Import PDF function

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

bot = Bot(token=TOKEN)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context):
    await update.message.reply_text("Send me a Multporn.net link to download images.")

async def fetch_gallery(update: Update, context):
    url = update.message.text.strip()

    if not url.startswith("https://multporn.net/comics/") and not url.startswith("https://multporn.net/hentai_manga/"):
        await update.message.reply_text("Invalid URL. Please send a valid Multporn.net manga link.")
        return

    await update.message.reply_text(f"Fetching images from: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        images = [
            img.get("src") for img in soup.find_all("img")
            if img.get("src") and "multporn.net" in img.get("src") and img.get("src").endswith((".jpg", ".png"))
        ]

        if not images:
            await update.message.reply_text("No manga images found on this page.")
            return

        await update.message.reply_text(f"Found {len(images)} images. Downloading...")

        image_paths = []
        for index, img_url in enumerate(images):
            filename = os.path.join(DOWNLOAD_DIR, f"image_{index+1}.jpg")
            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as img_file:
                    img_file.write(img_data)
                image_paths.append(filename)
            except requests.exceptions.RequestException:
                continue

        if not image_paths:
            await update.message.reply_text("Failed to download images.")
            return

        await update.message.reply_text("Uploading images to Telegram...")
        for img_path in image_paths:
            await update.message.reply_document(document=open(img_path, "rb"))

        await update.message.reply_text("All images uploaded! Creating a PDF...")
        await create_pdf(update, context)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def cancel(update: Update, context):
    await update.message.reply_text("Process canceled.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_gallery))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
