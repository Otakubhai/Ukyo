import os
import gc
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pdf(image_paths, output_pdf_path):
    """Creates a PDF from images without altering quality or order."""
    if not image_paths:
        logger.warning("No images to add to PDF.")
        return None

    try:
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        c = canvas.Canvas(output_pdf_path)
        
        for img_path in image_paths:
            try:
                with Image.open(img_path) as img:
                    # Convert image to RGB if necessary
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    width, height = img.size

                    # Add image as a full-page without resizing
                    c.setPageSize((width, height))
                    c.drawImage(ImageReader(img), 0, 0, width, height)
                    c.showPage()
            except Exception as e:
                logger.error(f"Error processing {img_path}: {e}")
        
        c.save()
        logger.info(f"PDF saved at: {output_pdf_path}")

        return output_pdf_path

    except Exception as e:
        logger.error(f"Failed to create PDF: {e}")
        return None

    finally:
        gc.collect()
