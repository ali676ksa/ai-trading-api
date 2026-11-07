
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="AI Trading Command Center")

@app.get("/")
def home():
    return {
        "status": "online",
        "project": "AI Trading Command Center"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/status")
def api_status():
    return {
        "connected": False,
        "provider": "none",
        "mode": "demo"
    }

from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/dashboard", include_in_schema=False)
def dashboard():
    path = Path(__file__).resolve().parent / "dashboard.html"
    return FileResponse(path, media_type="text/html")


from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/dashboard")
def dashboard():
    return FileResponse(
        Path(__file__).resolve().parent / "dashboard.html"
    )

