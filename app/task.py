
from celery import Celery
from app.services.pdf_processor import pdf_to_images
from app.services.symbol_detecter import detect_symbol_regions, classify_symbol
from app.services.ocr_services import extract_tag
from app.services.db_services import save_symbol

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def process_diagram(job_id: str, pdf_bytes: bytes):
    images = pdf_to_images(pdf_bytes)
    
    for page_img in images:
        regions = detect_symbol_regions(page_img)
        
        for i, region in enumerate(regions):
            # crop the symbol region
            crop = page_img.crop((
                region["x"], region["y"],
                region["x"] + region["w"],
                region["y"] + region["h"]
            ))
            
            # run OCR on the crop
            ocr_result = extract_tag(crop)
            
            # classify based on tag
            symbol_type = classify_symbol(ocr_result["tag"], ocr_result["all_text"])
            
            # save to DB
            save_symbol({
                "job_id": job_id,
                "shape_label": f"Shape-{i+1}",
                "tag": ocr_result["tag"],
                "symbol_type": symbol_type,
                "bbox": region,
                "confidence": ocr_result["confidence"],
                "properties": {}
            })