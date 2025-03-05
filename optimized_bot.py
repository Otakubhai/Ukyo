import os
import tempfile
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, filters, CallbackContext
import logging
import gc

# Import PDF generation function
from optimized_pdf_generator import create_pdf

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

# Function to fetch images from a webpage
async def scrape_images(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), "html.parser")
                img_tags = soup.find_all("img")
                return [img["src"] for img in img_tags if "src" in img.attrs]
    return []

# Function to get anime image URL from Anilist
def get_anime_image(anime_id: str):
    return f"https://img.anili.st/media/{anime_id}"

# /get_doujin command to fetch doujin images
async def get_doujin(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Please provide a valid URL.")
        return
    
    url = context.args[0]
    await update.message.reply_text("Scraping image URLs...")
    
    try:
        image_urls = await scrape_images(url)
        if not image_urls:
            await update.message.reply_text("No images found.")
            return
        
        # Download and send the first image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_urls[0]) as response:
                if response.status == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                        temp_file.write(await response.read())
                        temp_path = temp_file.name

                    await update.message.reply_photo(photo=InputFile(temp_path))
                    os.remove(temp_path)
    except Exception as e:
        logging.error(f"Error fetching doujin images: {e}")
        await update.message.reply_text("An error occurred while fetching images.")

# /anime command to fetch anime details and image
async def anime(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /anime <anime_id> <anime_name>")
        return
    
    anime_id = context.args[0]
    anime_name = " ".join(context.args[1:])  # Get full anime name
    image_url = get_anime_image(anime_id)
    
    message_text = f"""💦 {anime_name}
╭──────────────────────
├ 📺 Episode : 01 - 06
├ 💾 Quality : 720p
├ 🎭 Genres: Hanime, Gamers
├ 🔊 Audio track : Sub
├ #Censored
├ #Recommendation +++++
╰──────────────────────"""

    await update.message.reply_photo(photo=image_url, caption=message_text, parse_mode='HTML')

# Initialize bot
app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()
app.add_handler(CommandHandler("get_doujin", get_doujin))
app.add_handler(CommandHandler("anime", anime))

if __name__ == "__main__":
    app.run_polling()
