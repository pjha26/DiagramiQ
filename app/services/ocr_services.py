import easyocr
import numpy as np
import logging

logger = logging.getLogger(__name__)

reader = easyocr.Reader(['en'], gpu=False)

def extract_tag(pil_crop) -> dict:
    img_array = np.array(pil_crop)
    results = reader.readtext(img_array)
    
    # collect all text found in the crop
    texts = [res[1] for res in results]
    confidences = [res[2] for res in results]
    
    # known P&ID tag patterns
    known_patterns = ["XV", "PV", "HEX", "PIC", "PT", "PE", "P-"]
    
    tag = None
    for text in texts:
        for pattern in known_patterns:
            if pattern in text.upper():
                tag = text.upper()
                break
    
    return {
        "tag": tag,
        "all_text": texts,
        "confidence": round(sum(confidences)/len(confidences), 2) if confidences else 0.0
    }