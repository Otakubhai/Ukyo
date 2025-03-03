import os
import gc
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_pdf(image_paths, output_pdf_path):
    """
    Creates a high-quality PDF from images preserving original quality and aspect ratio.
    No limit on the number of pages.
    """
    if not image_paths:
        logger.warning("No images to add to PDF.")
        return None

    start_time = time.time()
    total_images = len(image_paths)
    logger.info(f"Creating PDF with {total_images} images")

    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Create canvas with no initial page size (will be set per image)
        c = canvas.Canvas(output_pdf_path)
        
        for i, img_path in enumerate(image_paths):
            try:
                if i % 10 == 0:
                    logger.info(f"Processing image {i+1}/{total_images}")
                
                with Image.open(img_path) as img:
                    # Convert image mode if necessary
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGB")

                    # Get original dimensions
                    width, height = img.size
                    
                    # Set the page size to match the image dimensions
                    c.setPageSize((width, height))
                    
                    # Draw the image at the correct position and size
                    c.drawImage(
                        ImageReader(img_path),
                        0,  # x position
                        0,  # y position
                        width=width,
                        height=height,
                        mask='auto'  # Handle transparency if present
                    )
                    
                    # Add the page to the PDF
                    c.showPage()
                    
                    # Force garbage collection after each page to manage memory
                    if i % 20 == 0:
                        gc.collect()
                        
            except Exception as e:
                logger.error(f"Error processing image {img_path}: {str(e)}")
                # Continue with the next image instead of failing
        
        # Save the PDF
        c.save()
        
        # Log completion with timing
        elapsed = time.time() - start_time
        logger.info(f"PDF created successfully with {total_images} pages in {elapsed:.2f} seconds")
        
        return output_pdf_path

    except Exception as e:
        logger.error(f"Failed to create PDF: {str(e)}")
        return None

    finally:
        # Clean up memory
        gc.collect()
