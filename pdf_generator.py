import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

def create_pdf(image_paths, output_pdf_path):
    """Generates a PDF from a list of images."""
    if not image_paths:
        print("No images to add to PDF.")
        return None  # Return None if no images are available

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    pdf = canvas.Canvas(output_pdf_path, pagesize=letter)

    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            width, height = img.size  # Maintain original aspect ratio

            # Scale image to fit within the page size
            max_width = 500
            max_height = 700
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            pdf.drawInlineImage(img_path, 50, 750 - new_height, width=new_width, height=new_height)
            pdf.showPage()
        except Exception as e:
            print(f"Error adding image {img_path}: {e}")

    pdf.save()

    if os.path.exists(output_pdf_path):
        return output_pdf_path  # Return the correct file path
    else:
        return None  # If the file is missing, return None
