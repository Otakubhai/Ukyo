import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def create_pdf(image_paths, pdf_path):
    """Creates a PDF from images without watermark or embedded link."""
    if not image_paths:
        print("No images found to create a PDF.")
        return

    # Set the PDF page size to letter format
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                img.thumbnail((width, height))  # Resize to fit page while maintaining aspect ratio
                img_reader = ImageReader(img)
                c.drawImage(img_reader, 0, 0, width, height)  # Place image on page
                c.showPage()
        except Exception as e:
            print(f"Skipping image {img_path} due to error: {e}")

    c.save()
    print(f"PDF saved at {pdf_path}")
