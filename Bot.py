import os
import tempfile
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import logging
import gc

# Import PDF generation function
from pdf_generator import create_pdf

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch bot token
TOKEN = os.getenv("BOT_TOKEN")

# Use temp directory instead of persistent storage
TEMP_DIR = tempfile.gettempdir()

# Define conversation states
WAITING_FOR_NUMBER = 1

# Store user preferences temporarily (with limited size)
MAX_CONCURRENT_USERS = 50
user_requests = {}

async def start(update: Update, context):
    """Handles the /start command"""
    await update.message.reply_text("Send me a Multporn.net link to download images.")

async def ask_image_limit(update: Update, context):
    """Asks the user how many images they want to download."""
    url = update.message.text.strip()

    if "multporn.net" not in url:
        await update.message.reply_text("Invalid URL. Please send a valid Multporn.net link.")
        return ConversationHandler.END

    # Limit concurrent users
    if len(user_requests) >= MAX_CONCURRENT_USERS:
        oldest_user = list(user_requests.keys())[0]
        user_requests.pop(oldest_user)
        
    user_requests[update.message.chat_id] = {"url": url}
    await update.message.reply_text("How many images do you want to download? (Enter a number, max 10)")
    return WAITING_FOR_NUMBER

async def fetch_gallery(update: Update, context):
    """Fetch and download images with a limit set by the user."""
    try:
        num_images = int(update.message.text.strip())
        chat_id = update.message.chat_id
        
        # Apply reasonable limit
        num_images = min(num_images, 10)

        if chat_id not in user_requests:
            await update.message.reply_text("No URL found. Please send the link again.")
            return ConversationHandler.END

        url = user_requests[chat_id]["url"]
        await update.message.reply_text(f"Fetching up to {num_images} images from: {url}")

        # Clean up user request data after fetching the URL
        del user_requests[chat_id]
        
        # Force garbage collection
        gc.collect()

        response = requests.get(url, timeout=30)  # Increased timeout
        response.raise_for_status()
        
        # Use a more memory-efficient parser
        soup = BeautifulSoup(response.text, "html.parser", parse_only=BeautifulSoup.SoupStrainer("img"))

        # Process images one by one to save memory
        image_urls = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                if img_url.startswith("//"):  # Convert protocol-relative URLs
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    base_url = "/".join(url.split("/")[:3])
                    img_url = base_url + img_url
                image_urls.append(img_url)
                if len(image_urls) >= num_images:
                    break

        if not image_urls:
            await update.message.reply_text("No images found on this page.")
            return ConversationHandler.END

        await update.message.reply_text(f"Found {len(image_urls)} images. Processing...")

        # Create a temporary directory for this user/session
        with tempfile.TemporaryDirectory(dir=TEMP_DIR) as temp_user_dir:
            image_paths = []
            
            # Process images one at a time
            for index, img_url in enumerate(image_urls):
                if index >= num_images:
                    break
                    
                temp_path = os.path.join(temp_user_dir, f"image_{index+1:03}.jpg")
                
                try:
                    # Stream the download to avoid loading entire image into memory
                    with requests.get(img_url, timeout=30, stream=True) as r:
                        r.raise_for_status()
                        with open(temp_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    image_paths.append(temp_path)
                    
                    # Send images individually right after download
                    with open(temp_path, "rb") as img_file:
                        await update.message.reply_document(document=img_file)
                        
                except Exception as e:
                    logger.error(f"Error downloading image {img_url}: {e}")
                    continue
                    
                # Force garbage collection after each image
                gc.collect()

            if not image_paths:
                await update.message.reply_text("Failed to download any images.")
                return ConversationHandler.END

            # Generate PDF and send it
            await update.message.reply_text("Creating PDF...")
            
            pdf_path = os.path.join(temp_user_dir, "output.pdf")
            pdf_path = create_pdf(image_paths, pdf_path)

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    await update.message.reply_document(document=pdf_file, caption="Here is your PDF!")
            else:
                await update.message.reply_text("PDF generation failed. Please try again.")

            # Files are automatically cleaned up when leaving the with block

    except ValueError:
        await update.message.reply_text("Invalid number. Please enter a valid number.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await update.message.reply_text(f"Unexpected error occurred. Please try again later.")

    # Force final garbage collection
    gc.collect()
    return ConversationHandler.END

async def cancel(update: Update, context):
    """Handles /cancel command"""
    chat_id = update.message.chat_id
    if chat_id in user_requests:
        del user_requests[chat_id]
    await update.message.reply_text("Process canceled.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Set memory-friendly options
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_image_limit)],
        states={WAITING_FOR_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_gallery)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
