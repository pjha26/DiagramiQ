import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def detect_symbol_regions(pil_image) -> list:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    total_area = gray.shape[0] * gray.shape[1]
    
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    regions = []
    seen = set()
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        
        # skip anything covering more than 5% of total image
        # this eliminates the page border contours
        if area > total_area * 0.05:
            continue
        
        # skip tiny noise
        if area < 8000:
            continue
        
        # skip duplicate/overlapping regions
        key = (x // 20, y // 20)
        if key in seen:
            continue
        seen.add(key)
        
        regions.append({"x": x, "y": y, "w": w, "h": h})
    
    # sort top-left to bottom-right
    regions.sort(key=lambda r: (r["y"] // 300, r["x"]))
    
    print(f"Final regions detected: {len(regions)}")
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