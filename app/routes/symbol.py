from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol import Symbol

router = APIRouter()

@router.get("/symbols/{job_id}")
async def get_symbols(job_id: str, db: Session = Depends(get_db)):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    return symbols

@router.patch("/symbols/{symbol_id}")
async def update_symbol(symbol_id: int, payload: dict, db: Session = Depends(get_db)):
    symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
    symbol.properties.update(payload)   # merge custom fields
    db.commit()
    return symbol