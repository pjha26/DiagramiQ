
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol import Symbol

router = APIRouter()

@router.get("/export/{job_id}")
def export_symbols(job_id: str, db: Session = Depends(get_db)):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()

    if not symbols:
        return {"error": "No symbols found for this job_id"}

    engineering = []
    unknown = []

    for s in symbols:
        symbol_data = {
            "id": s.id,
            "shape_label": s.shape_label,
            "tag": s.tag,
            "symbol_type": s.symbol_type,
            "bbox": s.bbox,
            "confidence": s.confidence,
            "properties": s.properties
        }
        if s.symbol_type == "unknown":
            unknown.append(symbol_data)
        else:
            engineering.append(symbol_data)

    return {
        "job_id": job_id,
        "total_detected": len(symbols),
        "engineering_symbols_count": len(engineering),
        "unclassified_count": len(unknown),
        "engineering_symbols": engineering,
        "unclassified": unknown
    }