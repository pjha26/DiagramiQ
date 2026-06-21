import fitz
from PIL import Image
import io
import os

def pdf_to_images(pdf_bytes: bytes) -> list:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(3.0, 3.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # save debug image to disk
        debug_path = f"E:\\webd\\DiagramiQ\\debug_page_{i}.png"
        img.save(debug_path)
        
        images.append(img)
    return images