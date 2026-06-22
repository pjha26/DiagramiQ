from app.database import SessionLocal
from app.models.symbol import Symbol
from app.models.job import Job
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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def create_job(job_id: str):
    db = SessionLocal()
    try:
        job = Job(job_id=job_id, status="processing")
        db.add(job)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create job {job_id}: {str(e)}")
    finally:
        db.close()

def update_job_status(job_id: str, status: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = status
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update job {job_id} to {status}: {str(e)}")
    finally:
        db.close()
