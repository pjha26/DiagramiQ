import fitz
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def pdf_to_images(pdf_bytes: bytes) -> list:
    logger.info("Converting PDF to images")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(2.0, 2.0)   # 2x zoom for better OCR accuracy
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images