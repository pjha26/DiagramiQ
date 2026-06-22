import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def detect_symbol_regions(pil_image) -> list:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # invert so symbols are white on black
    inverted = cv2.bitwise_not(gray)
    
    # threshold - anything not white becomes white
    _, thresh = cv2.threshold(inverted, 30, 255, cv2.THRESH_BINARY)
    
    # dilate to connect symbol parts
    kernel = np.ones((15, 15), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=3)
    
    contours, _ = cv2.findContours(
        dilated,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    print(f"Total contours found: {len(contours)}")
    
    regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        print(f"Contour: x={x} y={y} w={w} h={h} area={area}")
        
        # image is 2339x3572, symbols are roughly 400-800px each
        # outer border will be ~2339x3572 so filter that out
        if 10000 < area < 2000000:
            regions.append({"x": x, "y": y, "w": w, "h": h})
    
    print(f"Regions after filter: {len(regions)}")
    regions.sort(key=lambda r: (r["y"] // 200, r["x"]))
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