from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from app.routes import upload, symbol, export
from app.database import engine, Base
from app.models.job import Job  # ensure Job table is created

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DiagramIQ")

app.include_router(upload.router, prefix="/api")
app.include_router(symbol.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "DiagramIQ running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "DiagramIQ",
        "version": "1.0.0"
    }