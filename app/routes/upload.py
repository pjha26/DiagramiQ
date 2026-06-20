from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import base64
from app.task import process_diagram

router = APIRouter()

@router.post("/upload")
async def upload_diagram(file: UploadFile = File(...)):
    
    # validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )
    
    # validate file size (limit to 10MB)
    pdf_bytes = await file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be under 10MB"
        )
        
    job_id = str(uuid.uuid4())
    
    # encode bytes to base64 string for celery JSON serialization
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # trigger background processing
    process_diagram.delay(job_id, pdf_b64)
    
    return {"job_id": job_id, "status": "processing"}