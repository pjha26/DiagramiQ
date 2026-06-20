# DiagramIQ - P&ID Symbol Extractor

DiagramIQ is a FastAPI-based backend service designed to automatically extract, detect, and classify engineering symbols from Piping and Instrumentation Diagrams (P&IDs). 

It leverages **OpenCV** for computer vision-based shape detection and **EasyOCR** to read text/tags from diagrams, orchestrating the heavy lifting asynchronously via **Celery** and **Redis**.

## 🏗️ Project Architecture & Workflow

The following diagram illustrates the flow of data from a user's PDF upload to final symbol classification and export.

```mermaid
graph TD
    User([User]) -->|POST /api/upload| API[FastAPI Application]
    API -->|1. Returns job_id| User
    API -->|2. Publishes task| Redis[(Redis Broker)]
    
    Worker[Celery Worker] -.->|3. Consumes task| Redis
    
    subgraph Background Processing Pipeline
        Worker -->|PDF Bytes| PDF[PDF Processor<br/>PyMuPDF]
        PDF -->|Images| OpenCV[Symbol Detector<br/>OpenCV]
        OpenCV -->|Symbol Regions| OCR[OCR Service<br/>EasyOCR]
        OCR -->|Extracted Tags| Classifier[Symbol Classifier]
    end
    
    Classifier -->|4. Saves Symbol Data| DB[(PostgreSQL)]
    
    User -->|"GET /api/symbols/{job_id}"| API
    API -->|Reads Data| DB
    
    User -->|"PATCH /api/symbols/{id}"| API
    API -->|Updates Data| DB
    
    User -->|"GET /api/export/{job_id}"| API
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

### 1. Prerequisites
Ensure you have the following installed:
- Python 3.9+
- PostgreSQL
- Redis Server (running locally on port 6379, or hosted)

### 2. Install Dependencies
Clone the repository and install the required pip packages.

```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create or verify your `.env` file in the root directory. Ensure that special characters in your database password are URL-encoded.

```env
DATABASE_URL="postgresql://postgres:YOUR_ENCODED_PASSWORD@your.database.host:5432/postgres"
REDIS_URL="redis://localhost:6379/0"
```

### 4. Database Migration
The database tables are automatically created on startup via SQLAlchemy's `Base.metadata.create_all(bind=engine)` inside `app/main.py`.

---

## 🏃‍♂️ Running the Application

Because DiagramIQ relies on asynchronous background processing, you must run both the API server and the Celery worker concurrently.

**Terminal 1: Start the FastAPI Server**
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can view the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

**Terminal 2: Start the Celery Worker**
```bash
# On Windows, you may need to add --pool=solo
celery -A app.task.celery worker --loglevel=info
```

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
