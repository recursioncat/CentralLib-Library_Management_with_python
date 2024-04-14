import os, shutil
import PyPDF2 
from pdf2image import convert_from_path

def pdf_to_image(pdf_path, page_number, dpi):
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)

            if page_number < 0 or page_number > len(pdf_reader.pages):
                raise ValueError("Invalid page number")
            
            images = convert_from_path(pdf_path, dpi=dpi, first_page=page_number, last_page=page_number)

            # Check if images were generated
            if not images:
                raise ValueError("No images generated")

            # Get the path to the static/Images directory
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'Images')
            os.makedirs(static_dir, exist_ok=True)
            # Save the image in the static/Images directory
            image_path = os.path.join(static_dir, f"{page_number}.png")
            images[0].save(image_path, 'PNG')

            # Return the relative path from the static directory
            return os.path.relpath(image_path, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'))      
    except Exception as e:
        # Log the error
        print(f"Error converting PDF to image: {e}")
        return None  # Return None to indicate failure
    