from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol import Symbol

router = APIRouter()

@router.get("/export/{job_id}")
def export_symbols(
    job_id: str, 
    min_confidence: float = Query(0.0),
    db: Session = Depends(get_db)
):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    symbols = [s for s in symbols if (s.confidence or 0) >= min_confidence]

    if not symbols:
        raise HTTPException(status_code=404, detail="No symbols found for this job_id")

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
        if s.symbol_type == "unknown" or s.symbol_type is None:
            unknown.append(symbol_data)
        else:
            engineering.append(symbol_data)

    return {
        "job_id": job_id,
        "total_detected": len(symbols),
        "engineering_symbols_count": len(engineering),
        "unclassified_count": len(unknown),
        "summary": {
            "control_valve": len([s for s in engineering if s["symbol_type"] == "control_valve"]),
            "pressure_vessel": len([s for s in engineering if s["symbol_type"] == "pressure_vessel"]),
            "heat_exchanger": len([s for s in engineering if s["symbol_type"] == "heat_exchanger"]),
            "pump": len([s for s in engineering if s["symbol_type"] == "pump"]),
            "instrument": len([s for s in engineering if s["symbol_type"] == "instrument"]),
        },
        "engineering_symbols": engineering,
        "unclassified": unknown
    }