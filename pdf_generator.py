import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def create_pdf(image_paths, pdf_path):
    """Creates a PDF from images without watermark or embedded link, maintaining aspect ratio."""
    if not image_paths:
        print("No images found to create a PDF.")
        return

    c = canvas.Canvas(pdf_path, pagesize=letter)
    page_width, page_height = letter

    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                img_width, img_height = img.size

                # Calculate scaling factor to maintain aspect ratio
                scale_factor = min(page_width / img_width, page_height / img_height)
                new_width = img_width * scale_factor
                new_height = img_height * scale_factor

                # Center image on the page
                x_position = (page_width - new_width) / 2
                y_position = (page_height - new_height) / 2

                img_reader = ImageReader(img)
                c.drawImage(img_reader, x_position, y_position, new_width, new_height)
                c.showPage()
        except Exception as e:
            print(f"Skipping image {img_path} due to error: {e}")

    c.save()
    print(f"PDF saved at {pdf_path}")
