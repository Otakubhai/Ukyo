import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

MAX_IMAGES_PER_PDF = 20  # Split PDFs if more than 20 images

def create_pdf(image_paths, output_pdf):
    """Creates PDFs from images while maintaining aspect ratio and optimizing memory usage."""
    if not image_paths:
        print("No images to create a PDF.")
        return None

    pdf_files = []  # Stores paths of all generated PDFs

    # Split into multiple PDFs if needed
    for i in range(0, len(image_paths), MAX_IMAGES_PER_PDF):
        chunk = image_paths[i:i + MAX_IMAGES_PER_PDF]
        pdf_part_path = f"{output_pdf.rstrip('.pdf')}_{i//MAX_IMAGES_PER_PDF + 1}.pdf"

        c = canvas.Canvas(pdf_part_path, pagesize=letter)
        page_width, page_height = letter

        for img_path in chunk:
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB (fixes issues with transparency in PNGs)
                    img = img.convert("RGB")

                    # Resize if image is too large
                    img.thumbnail((page_width, page_height), Image.LANCZOS)

                    # Center image on page
                    img_width, img_height = img.size
                    x_position = (page_width - img_width) / 2
                    y_position = (page_height - img_height) / 2

                    img_reader = ImageReader(img)
                    c.drawImage(img_reader, x_position, y_position, img_width, img_height)
                    c.showPage()
            except Exception as e:
                print(f"Skipping image {img_path} due to error: {e}")

        c.save()
        pdf_files.append(pdf_part_path)

    return pdf_files  # Returns list of PDFs generated
