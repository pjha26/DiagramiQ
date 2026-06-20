
from fastapi import FastAPI
from app.routes import upload, symbols, export
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DiagramIQ")

app.include_router(upload.router, prefix="/api")
app.include_router(symbols.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "DiagramIQ running"}