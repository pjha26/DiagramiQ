from app.database import SessionLocal
from app.models.symbol import Symbol
import logging

logger = logging.getLogger(__name__)

def save_symbol(data: dict):
    logger.info(f"Saving symbol for job_id: {data.get('job_id')}")
    db = SessionLocal()
    try:
        symbol = Symbol(**data)
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
        return symbol
    finally:
        db.close()
