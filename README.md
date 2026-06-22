# DiagramIQ - P&ID Symbol Extractor

DiagramIQ is a FastAPI-based backend service designed to automatically extract, detect, and classify engineering symbols from Piping and Instrumentation Diagrams (P&IDs). 

It leverages **OpenCV** for computer vision-based shape detection and **EasyOCR** to read text/tags from diagrams, orchestrating the heavy lifting asynchronously via **Celery** and **Redis**.

## 🏗️ Project Architecture & Workflow

The following diagram illustrates the flow of data from a user's PDF upload to final symbol classification and export.

```mermaid
graph TD
    Client(["User / client"])
    
    subgraph API ["FastAPI — API layer"]
        Upload["POST /upload<br>accepts PDF, returns job_id"]
        Status["GET /status/{job_id}<br>processing or completed"]
        Export["GET /export/{job_id}<br>structured JSON output"]
        Patch["PATCH /symbols/{symbol_id} — assign custom properties"]
    end
    
    Client -- "HTTP request" --> API
    
    Redis["Redis broker<br>job queue (base64 payload)"]
    API -- "publishes job" --> Redis
    
    subgraph Pipeline ["Celery — background pipeline"]
        direction TB
        PDF["pdf_processor.py — PyMuPDF<br>PDF → high-res image (2x zoom)"]
        CV["symbol_detector.py — OpenCV<br>contour detection → bounding boxes"]
        OCR["ocr_service.py — EasyOCR<br>crops → tag extraction (XV, PV, HEX...)"]
        Classify["classify_symbol() — rule-based<br>valve / vessel / pump / unknown"]
        PDF --> CV --> OCR --> Classify
    end
    
    Redis -- "consumes task" --> Pipeline
    
    DB[("PostgreSQL<br>symbols table<br>job_id, tag, type<br>bbox, confidence<br>properties (JSON)")]
    
    Classify -- "saves symbol data" --> DB
    API -- "reads / updates" --> DB
```

### Workflow Steps:
1. **Upload:** A user uploads a P&ID PDF document.
2. **Task Delegation:** FastAPI immediately returns a `job_id` and sends the document (base64 encoded) to a Redis message broker.
3. **Processing:** 
   - A Celery background worker picks up the job.
   - **PyMuPDF** converts the PDF into high-resolution images.
   - **OpenCV** identifies geometric contours and bounds shapes to find symbol regions.
   - **EasyOCR** reads any textual tags inside those bounding boxes.
   - The **Classifier** categorizes the shape based on its tag (e.g., `XV` -> Valve, `P-` -> Pump).
4. **Storage:** The classified symbol data and bounding box coordinates are saved to a PostgreSQL database.
5. **Retrieval & Export:** The user can poll the API to get the processed symbols, update custom properties, or export the finalized data.

---

## 🚀 Tech Stack
- **Web Framework:** FastAPI
- **Database:** PostgreSQL (via SQLAlchemy)
- **Task Queue:** Celery + Redis
- **Computer Vision:** OpenCV (`opencv-python`)
- **OCR:** EasyOCR
- **PDF Processing:** PyMuPDF (`fitz`)

---

## 🛠️ Setup & Installation

### Quick Start
1. Clone the repo
2. Copy .env.example to .env and fill in your values
3. pip install -r requirements.txt
4. Create PostgreSQL database named diagramiq
5. Double-click start.bat to launch all services
6. Open http://127.0.0.1:8000/docs

## Running with Docker (Recommended)
1. Install Docker Desktop
2. Clone the repo
3. Run: docker-compose up --build
4. Open http://localhost:8000/docs
5. Open http://localhost:8000 for the UI

That is all you need. Docker handles PostgreSQL, Redis, FastAPI and Celery automatically.

---

## 📡 API Endpoints

### `POST /api/upload`
Upload a PDF diagram.
- **Payload:** `multipart/form-data` (PDF file, max 10MB)
- **Response:** Returns a `job_id` and marks status as `processing`.

### `GET /api/status/{job_id}`
Check the current processing status of a Celery background job.
- **Response:** Returns `{"status": "processing"}` or `{"status": "completed", "total_symbols": X}`.

### `GET /api/symbols/{job_id}`
Retrieve all extracted symbols associated with a specific job upload.
- **Response:** List of symbol JSON objects including bounding boxes, confidence scores, and identified types.

### `PATCH /api/symbols/{symbol_id}`
Update custom properties or correct the classification of a specific symbol.
- **Payload:** JSON dictionary of properties to merge.
- **Response:** The updated symbol record.

### `GET /api/export/{job_id}`
Export a summarized report of the P&ID processing.
- **Response:** Groups symbols into `engineering_symbols` and `unclassified`, providing counts and formatted data for downstream applications.
