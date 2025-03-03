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
from pdf_generator import create_pdf

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

# Fetch bot token from environment variables
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Use environment variable for temp directory or default to system temp
TEMP_DIR = os.getenv("TEMP_DIR", tempfile.gettempdir())
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)

# Define conversation states
QUALITY_SELECTION, SYNOPSIS = range(2)

async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command"""
    await update.message.reply_text(
        "Hey there! Use this bot to:\n"
        "- Get anime posts: `/anime <name>`\n"
        "- Download doujins: `/get_doujin <URL>`"
    )

# ANIME POST HANDLER
async def anime(update: Update, context: CallbackContext) -> None:
    """Handles the /anime command."""
    if not context.args:
        await update.message.reply_text("Please provide an anime name.")
        return

    status_message = await update.message.reply_text("Searching for anime... Please wait.")
    
    anime_name = " ".join(context.args)
    anime_data = await get_anime_info(anime_name)

    await status_message.delete()
    
    if anime_data:
        await update.message.reply_photo(
            photo=anime_data["image_url"], 
            caption=anime_data["caption"], 
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Anime not found or an error occurred.")

async def get_anime_info(anime_name: str) -> dict | None:
    """Fetch anime details from AniList API."""
    url = "https://graphql.anilist.co/"
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
            title { romaji english }
            episodes genres coverImage { extraLarge }
        }
    }
    '''
    variables = {"search": anime_name}

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json={"query": query, "variables": variables}) as response:
                if response.status == 200:
                    data = await response.json()
                    anime_data = data.get("data", {}).get("Media")

                    if anime_data:
                        title = anime_data["title"]["english"] or anime_data["title"]["romaji"]
                        genres = ", ".join(["Hanime"] + anime_data["genres"])
                        image_url = anime_data["coverImage"]["extraLarge"]

                        caption = (
                            f"💦 {title}\\n"
                            "╭──────────────────────\\n"
                            f"├ 📺 Episode : {anime_data['episodes']}\\n"
                            "├ 💾 Quality : 720p\\n"
                            f"├ 🎭 Genres: {genres}\\n"
                            "├ 🔊 Audio track : Sub\\n"
                            "├ #Censored\\n"
                            "├ #Recommendation +++++++\\n"
                            "╰──────────────────────"
                        )

                        return {"image_url": image_url, "caption": caption}
    except Exception as e:
        logger.error(f"Error fetching anime info: {e}")
    
    return None

# DOUJIN DOWNLOAD HANDLER
async def get_doujin(update: Update, context: CallbackContext) -> None:
    """Handles the /get_doujin command."""
    if not context.args:
        await update.message.reply_text("Please provide a valid Multporn.net URL.")
        return
    
    url = context.args[0].strip()
    if "multporn.net" not in url:
        await update.message.reply_text("Invalid URL. Please send a valid Multporn.net link.")
        return

    status_message = await update.message.reply_text("Fetching images... This may take a while depending on the size.")
    
    try:
        # Create a unique folder for this request
        request_id = f"doujin_{hash(url) % 10000}"
        request_dir = os.path.join(TEMP_DIR, request_id)
        os.makedirs(request_dir, exist_ok=True)
        
        await status_message.edit_text("Scraping image URLs...")
        image_urls = await scrape_images(url)
        
        if not image_urls:
            await status_message.edit_text("No images found or invalid URL.")
            return

        total_images = len(image_urls)
        await status_message.edit_text(f"Found {total_images} images. Downloading...")
        
        # Download images
        image_paths = await download_images(image_urls, request_dir, status_message)

        if not image_paths:
            await status_message.edit_text("Failed to download images.")
            return

        await status_message.edit_text("Generating PDF... This may take a moment.")
        
        # Generate PDF
        pdf_path = os.path.join(request_dir, f"{request_id}.pdf")
        create_pdf(image_paths, pdf_path)

        # Send PDF to user
        await status_message.edit_text("PDF created! Sending to you now...")
        
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=InputFile(pdf_file, filename=f"{request_id}.pdf"), 
                caption=f"Here is your doujin PDF with {len(image_paths)} pages."
            )
        
        await status_message.delete()

    except Exception as e:
        logger.error(f"Error processing doujin: {e}")
        await update.message.reply_text(f"An error occurred while processing the request: {str(e)}")
    finally:
        # Clean up
        try:
            import shutil
            if os.path.exists(request_dir):
                shutil.rmtree(request_dir)
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")
        
        gc.collect()

async def scrape_images(url: str):
    """Scrapes all image URLs from the given Multporn.net page asynchronously."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch page: HTTP {response.status}")
                    return None
                
                html_content = await response.text()
        
        soup = BeautifulSoup(html_content, "html.parser")
        image_tags = soup.find_all("img")
        
        image_urls = []
        for img in image_tags:
            src = img.get("src")
            if src and "uploads" in src:
                if not src.startswith("http"):
                    src = "https://multporn.net" + src
                image_urls.append(src)
                
        logger.info(f"Found {len(image_urls)} images")
        return image_urls
    
    except Exception as e:
        logger.error(f"Error scraping images: {e}")
        return None

async def download_images(image_urls, output_dir, status_message=None):
    """Downloads images asynchronously and returns a list of local file paths."""
    image_paths = []
    total = len(image_urls)
    completed = 0
    
    sem = asyncio.Semaphore(10)  # Limit concurrent downloads
    
    async def download_image(url, index):
        nonlocal completed
        
        async with sem:
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            img_path = os.path.join(output_dir, f"image_{index:03d}.jpg")
                            with open(img_path, "wb") as f:
                                f.write(await response.read())
                            
                            # Validate the image
                            try:
                                with Image.open(img_path) as img:
                                    img.verify()
                                image_paths.append(img_path)
                            except Exception as img_error:
                                logger.error(f"Invalid image file: {img_error}")
                                if os.path.exists(img_path):
                                    os.remove(img_path)
                        else:
                            logger.error(f"Failed to download image {index}: HTTP {response.status}")
            except Exception as e:
                logger.error(f"Error downloading image {index}: {e}")
            
            completed += 1
            if status_message and completed % 5 == 0:
                try:
                    await status_message.edit_text(f"Downloading images: {completed}/{total}")
                except Exception:
                    pass  # Ignore message editing errors
    
    # Create download tasks
    tasks = [download_image(url, i) for i, url in enumerate(image_urls)]
    await asyncio.gather(*tasks)
    
    # Sort by filename so images appear in the correct order
    return sorted(image_paths)

def main() -> None:
    """Main function to run the bot."""
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Register command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("anime", anime))
        app.add_handler(CommandHandler("get_doujin", get_doujin))
        
        # Set up graceful shutdown
        import signal
        def shutdown_handler(signum, frame):
            logger.info("Received shutdown signal, exiting...")
            asyncio.get_event_loop().stop()
        
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
        
        logger.info("Bot is running...")
        app.run_polling()
    
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    main()
