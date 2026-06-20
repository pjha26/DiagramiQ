import cv2
import numpy as np
from PIL import Image

def detect_symbol_regions(pil_image) -> list:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # threshold to isolate dark shapes on white background
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    # find contours of symbol regions
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w *h
        # filter out noise (too small) and full-page contours (too large)
        if 3000 < area < 500000:
            regions.append({"x": x, "y": y, "w": w, "h": h})
    
    return regions