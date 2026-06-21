from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import base64
from app.task import process_diagram

router = APIRouter()

@router.post("/api/upload")
async def upload_diagram(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted"
            )
        
        pdf_bytes = await file.read()
        
        if len(pdf_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        job_id = str(uuid.uuid4())
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        process_diagram.delay(job_id, pdf_b64)
        
        return {"job_id": job_id, "status": "processing"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )