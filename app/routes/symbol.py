from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol import Symbol

router = APIRouter()

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    
    if not symbols:
        return {"job_id": job_id, "status": "processing"}
    
    return {
        "job_id": job_id,
        "status": "completed",
        "total_symbols": len(symbols)
    }

@router.get("/symbols/{job_id}")
async def get_symbols(job_id: str, db: Session = Depends(get_db)):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    return symbols

@router.patch("/symbols/{symbol_id}")
async def update_symbol(symbol_id: int, payload: dict, db: Session = Depends(get_db)):
    symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
    if not symbol:
        raise HTTPException(status_code=404, detail="Symbol not found")
        
    # Reassign dictionary to trigger SQLAlchemy's JSON modification tracking
    props = dict(symbol.properties) if symbol.properties else {}
    props.update(payload)
    symbol.properties = props
    
    db.commit()
    db.refresh(symbol)
    return symbol