from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol import Symbol
from app.models.job import Job

router = APIRouter()

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    
    return {
        "job_id": job_id,
        "status": job.status,
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