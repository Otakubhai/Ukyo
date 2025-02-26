import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

# Fetch bot token
TOKEN = os.getenv("BOT_TOKEN")

# Folder to store images
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Define conversation states
WAITING_FOR_NUMBER = 1

# Store user preferences temporarily
user_requests = {}

async def start(update: Update, context):
    """Handles the /start command"""
    await update.message.reply_text("Send me a Multporn.net link to download images.")

async def ask_image_limit(update: Update, context):
    """Asks the user how many images they want to download."""
    url = update.message.text.strip()

    # Allow any Multporn link
    if "multporn.net" not in url:
        await update.message.reply_text("Invalid URL. Please send a valid Multporn.net link.")
        return ConversationHandler.END

    # Store the URL for the user
    user_requests[update.message.chat_id] = {"url": url}

    await update.message.reply_text("How many images do you want to download? (Enter a number)")
    return WAITING_FOR_NUMBER

async def fetch_gallery(update: Update, context):
    """Fetch images from the gallery with a limit set by the user."""
    try:
        num_images = int(update.message.text.strip())
        chat_id = update.message.chat_id

        if chat_id not in user_requests:
            await update.message.reply_text("No URL found. Please send the link again.")
            return ConversationHandler.END

        url = user_requests[chat_id]["url"]
        await update.message.reply_text(f"Fetching up to {num_images} images from: {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all images
        images = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                if img_url.startswith("//"):  # Convert protocol-relative URLs
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):  # Convert relative URLs
                    base_url = "/".join(url.split("/")[:3])
                    img_url = base_url + img_url
                images.append(img_url)

        if not images:
            await update.message.reply_text("No images found on this page.")
            return ConversationHandler.END

        # Apply limit
        images = images[:num_images]

        await update.message.reply_text(f"Downloading {len(images)} images...")

        # Download images
        image_paths = []
        for index, img_url in enumerate(images):
            filename = os.path.join(DOWNLOAD_DIR, f"image_{index+1:03}.jpg")
            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as img_file:
                    img_file.write(img_data)
                image_paths.append(filename)
            except requests.exceptions.RequestException:
                continue

        if not image_paths:
            await update.message.reply_text("Failed to download images.")
            return ConversationHandler.END

        await update.message.reply_text("Uploading images to Telegram...")

        # Send images
        for img_path in sorted(image_paths):  # Ensure correct order
            await update.message.reply_document(document=open(img_path, "rb"))

        # Generate and send PDF
        from pdf_generator import create_pdf
        await create_pdf(update, context)  # Ensure this is awaited if it's an async function

    except ValueError:
        await update.message.reply_text("Invalid number. Please enter a valid number.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context):
    """Handles /cancel command"""
    await update.message.reply_text("Process canceled.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_image_limit)],
        states={WAITING_FOR_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_gallery)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
