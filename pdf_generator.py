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
    """Creates a PDF from images with memory optimization."""
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
                # Use context manager to ensure image is closed properly
                with Image.open(img_path) as img:
                    # Resize very large images to reduce memory usage
                    max_dimension = 1200  # Reasonable limit
                    original_width, original_height = img.size
                    
                    # Only resize if image is too large
                    if original_width > max_dimension or original_height > max_dimension:
                        # Calculate new dimensions while preserving aspect ratio
                        if original_width > original_height:
                            new_width = max_dimension
                            new_height = int(original_height * (max_dimension / original_width))
                        else:
                            new_height = max_dimension
                            new_width = int(original_width * (max_dimension / original_height))
                            
                        # Create a smaller version of the image
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        width, height = new_width, new_height
                    else:
                        width, height = original_width, original_height
                    
                    # Create a new page with the same size as the image
                    c.setPageSize((width, height))
                    
                    # Use try-except to handle potential image format issues
                    try:
                        img_reader = ImageReader(img)
                        c.drawImage(img_reader, 0, 0, width=width, height=height)
                        c.showPage()
                    except Exception as e:
                        logger.error(f"Error rendering image {img_path}: {e}")
                        
                        # Try converting to RGB if it's a format issue
                        try:
                            rgb_img = img.convert('RGB')
                            img_reader = ImageReader(rgb_img)
                            c.drawImage(img_reader, 0, 0, width=width, height=height)
                            c.showPage()
                        except Exception as e2:
                            logger.error(f"Second attempt failed for {img_path}: {e2}")
                            # Create an empty page to maintain sequence
                            c.showPage()
            except Exception as e:
                logger.error(f"Error processing image {img_path}: {e}")
                
            # Force garbage collection after each image
            gc.collect()

        c.save()

        if os.path.exists(output_pdf_path):
            return output_pdf_path
        else:
            logger.error(f"PDF file not created at {output_pdf_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating PDF: {e}", exc_info=True)
        return None
