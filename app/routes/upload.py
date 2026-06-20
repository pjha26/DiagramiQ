from fastapi import APIRouter, UploadFile, File
import uuid
import base64
from app.task import process_diagram

router = APIRouter()

@router.post("/upload")
async def upload_diagram(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    pdf_bytes = await file.read()
    
    # encode bytes to base64 string for celery JSON serialization
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # trigger background processing
    process_diagram.delay(job_id, pdf_b64)
    
    return {"job_id": job_id, "status": "processing"}