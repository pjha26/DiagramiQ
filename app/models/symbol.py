from sqlalchemy import Column, String, Integer, JSON, Float
from app.database import Base

class Symbol(Base):
    __tablename__ = "symbols"
    id           = Column(Integer, primary_key=True)
    job_id       = Column(String, index=True)   # ties symbol to an upload
    shape_label  = Column(String)               # Shape-1, Shape-6, etc.
    tag          = Column(String, nullable=True) # XV-200, PV-1000, HEX-500
    symbol_type  = Column(String, nullable=True) # valve, vessel, pump, unknown
    bbox         = Column(JSON)                  # {x, y, w, h} in pixels
    confidence   = Column(Float, nullable=True)  # OCR/detection confidence
    properties   = Column(JSON, default={})      # custom editable fields
    image_crop   = Column(String, nullable=True) # path to cropped image file