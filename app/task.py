import os
import base64
import logging
from dotenv import load_dotenv
from celery import Celery
from app.services.pdf_processor import pdf_to_images
from app.services.symbol_detecter import detect_symbol_regions, classify_symbol
from app.services.ocr_services import extract_tag
from app.services.db_services import save_symbol, update_job_status

load_dotenv()
celery = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

logger = logging.getLogger(__name__)

@celery.task
def process_diagram(job_id: str, pdf_b64: str):
    logger.info(f"Processing PDF for job_id: {job_id}")
    try:
        pdf_bytes = base64.b64decode(pdf_b64)
        images = pdf_to_images(pdf_bytes)
        
        for page_img in images:
            regions = detect_symbol_regions(page_img)
            
            if not regions:
                logger.warning(f"No symbols detected on page for job_id: {job_id}")
                continue
            
            for i, region in enumerate(regions):
                try:
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
                except Exception as e:
                    logger.error(f"Failed to process region {i} for job {job_id}: {str(e)}")
                    continue
        
        # Mark job as completed
        update_job_status(job_id, "completed")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        update_job_status(job_id, "failed")