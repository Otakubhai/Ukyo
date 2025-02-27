import os
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import CallbackContext

# Define directories
DOWNLOAD_DIR = "downloads"
PDF_PATH = os.path.join(DOWNLOAD_DIR, "manga.pdf")

# Watermark text
WATERMARK_TEXT = "🔥 Powered by t.me/Den_of_Sins"

async def create_pdf(update: Update, context: CallbackContext):
    await update.message.reply_text("Creating PDF...")

    # Sort images numerically to maintain correct order
    image_files = sorted(
        [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.endswith((".jpg", ".png"))]
    )

    if not image_files:
        await update.message.reply_text("No images found to create a PDF.")
        return

    try:
        images = []
        for img_path in image_files:
            img = Image.open(img_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            # Load font
            try:
                font = ImageFont.truetype("arial.ttf", 20)  # Adjust size as needed
            except IOError:
                font = ImageFont.load_default()  # Use default font if arial.ttf is missing

            # Get image size
            img_width, img_height = img.size

            # Get text bounding box for accurate placement
            bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Position watermark at bottom-right corner
            x = img_width - text_width - 20
            y = img_height - text_height - 20

            # Add watermark
            draw.text((x, y), WATERMARK_TEXT, fill=(255, 255, 255), font=font)

            images.append(img)

        # Save as PDF
        images[0].save(PDF_PATH, save_all=True, append_images=images[1:])
    except Exception as e:
        await update.message.reply_text(f"Error creating PDF: {str(e)}")
        return

    await update.message.reply_text("Uploading PDF...")
    try:
        await update.message.reply_document(document=open(PDF_PATH, "rb"))
        await update.message.reply_text("PDF uploaded successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error uploading PDF: {str(e)}")
