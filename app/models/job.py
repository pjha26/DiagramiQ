from sqlalchemy import Column, Integer, String
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    status = Column(String, default="processing")
