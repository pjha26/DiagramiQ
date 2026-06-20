from app.database import SessionLocal
from app.models.symbol import Symbol

def save_symbol(data: dict):
    db = SessionLocal()
    try:
        symbol = Symbol(**data)
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
        return symbol
    finally:
        db.close()
