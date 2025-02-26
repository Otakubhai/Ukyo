import os
from PIL import Image
from telegram import Update
from telegram.ext import CallbackContext

# Folder where images are saved
DOWNLOAD_DIR = "downloads"
PDF_PATH = os.path.join(DOWNLOAD_DIR, "manga.pdf")

async def create_pdf(update: Update, context: CallbackContext):
    """Creates a PDF from downloaded images and sends it to the user."""
    await update.message.reply_text("Creating PDF...")

    # Get all images
    image_files = sorted(
        [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.endswith((".jpg", ".png"))]
    )

    if not image_files:
        await update.message.reply_text("No images found to create a PDF.")
        return

    # Convert images to PDF
    try:
        images = [Image.open(img).convert("RGB") for img in image_files]
        images[0].save(PDF_PATH, save_all=True, append_images=images[1:])
    except Exception as e:
        await update.message.reply_text(f"Error creating PDF: {str(e)}")
        return

    await update.message.reply_text("Uploading PDF...")

    # Send PDF to Telegram
    try:
        await update.message.reply_document(document=open(PDF_PATH, "rb"))
        await update.message.reply_text("PDF uploaded successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error uploading PDF: {str(e)}")
