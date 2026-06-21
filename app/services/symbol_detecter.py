import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def detect_symbol_regions(pil_image) -> list:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # apply gaussian blur to reduce noise before thresholding
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # use adaptive threshold instead of fixed threshold
    # handles varying lighting and contrast across the page
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )
    
    # dilate to connect nearby symbol components
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    contours, _ = cv2.findContours(
        dilated, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        # relaxed area filter to catch more symbol sizes
        if 1000 < area < 800000:
            regions.append({"x": x, "y": y, "w": w, "h": h})
    
    # sort regions top-left to bottom-right
    regions.sort(key=lambda r: (r["y"] // 100, r["x"]))
    
    return regions

def classify_symbol(tag: str, all_text: list) -> str:
    if not tag:
        return "unknown"
    if "XV" in tag or "PV" in tag:
        return "valve"
    if "HEX" in tag:
        return "vessel"
    if "P-" in tag or "PT" in tag or "PE" in tag:
        return "pump"
    if "PIC" in tag:
        return "instrument"
    return "unknown"