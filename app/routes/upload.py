
from fastapi import APIRouter, UploadFile, File
import uuid
from app.task import process_diagram

router = APIRouter()

@router.post("/upload")
async def upload_diagram(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    pdf_bytes = await file.read()
    
    # trigger background processing
    process_diagram.delay(job_id, pdf_bytes)
    
    return {"job_id": job_id, "status": "processing"}