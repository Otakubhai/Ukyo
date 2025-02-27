import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

DOWNLOAD_DIR = "downloads"
PDF_PATH = os.path.join(DOWNLOAD_DIR, "manga.pdf")

def create_pdf(image_paths, pdf_path):
    """Creates a PDF from images with a watermark and an embedded link."""
    if not image_paths:
        print("No images found to create a PDF.")
        return

    # Define watermark text and link
    watermark_text = "🔥 Powered by t.me/Den_of_Sins"
    link_url = "https://t.me/Den_of_Sins"

    # Load a bold font for better visibility
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Change if needed
    font_size = 24

    # Check if font exists, otherwise use default
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Create the PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    for img_path in image_paths:
        try:
            img = Image.open(img_path).convert("RGB")
            img_width, img_height = img.size

            # Resize image to fit within letter page size while maintaining aspect ratio
            aspect = min(width / img_width, height / img_height)
            new_width = int(img_width * aspect)
            new_height = int(img_height * aspect)

            img = img.resize((new_width, new_height))

            # Add watermark
            draw = ImageDraw.Draw(img)
            text_width, text_height = draw.textbbox((0, 0), watermark_text, font=font)[2:]
            x = new_width - text_width - 20  # Bottom-right corner
            y = new_height - text_height - 20
            draw.text((x, y), watermark_text, font=font, fill="black")

            # Save temp image with watermark
            temp_path = os.path.join(DOWNLOAD_DIR, "temp.jpg")
            img.save(temp_path)

            # Draw image on PDF
            c.drawImage(ImageReader(temp_path), (width - new_width) / 2, (height - new_height) / 2, new_width, new_height)

            # Add clickable link
            c.linkURL(link_url, (x, y, x + text_width, y + text_height), thickness=1)

            c.showPage()
        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")

    c.save()
    print("PDF created successfully!")
