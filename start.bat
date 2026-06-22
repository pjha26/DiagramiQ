@echo off
echo Starting DiagramIQ...
echo.
echo Step 1: Starting Redis...
start "Redis" cmd /k "redis\redis-server.exe"
timeout /t 3

echo Step 2: Starting Celery worker...
start "Celery" cmd /k ".venv\Scripts\celery -A app.task.celery worker --loglevel=info --pool=solo"
timeout /t 3

echo Step 3: Starting FastAPI...
start "FastAPI" cmd /k ".venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo All services started!
echo Open http://127.0.0.1:8000/docs to test the API
pause
