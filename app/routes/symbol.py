
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

# app/routes/export.py
@router.get("/export/{job_id}")
async def export_symbols(job_id: str, db: Session = Depends(get_db)):
    symbols = db.query(Symbol).filter(Symbol.job_id == job_id).all()
    return {
        "job_id": job_id,
        "total": len(symbols),
        "engineering_symbols": [s for s in symbols if s.symbol_type != "unknown"],
        "unclassified": [s for s in symbols if s.symbol_type == "unknown"]
    }