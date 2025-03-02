import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def create_pdf(image_paths, output_pdf_path):
    """Creates a PDF from images, keeping their original aspect ratio without distortion."""
    if not image_paths:
        print("No images to add to PDF.")
        return None  # Return None if no images are available

    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)  # Ensure directory exists

    c = canvas.Canvas(output_pdf_path)

    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                img_width, img_height = img.size  # Get original size
                
                # Create a new page with the same size as the image
                c.setPageSize((img_width, img_height))
                img_reader = ImageReader(img)
                
                # Draw the image on the page without resizing
                c.drawImage(img_reader, 0, 0, width=img_width, height=img_height)
                c.showPage()
        except Exception as e:
            print(f"Error adding image {img_path}: {e}")

    c.save()

    if os.path.exists(output_pdf_path):
        return output_pdf_path  # Return the correct file path
    else:
        return None  # If the file is missing, return None
