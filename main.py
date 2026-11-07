from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="AI Trading Command Center API")

@app.get("/")
def home():
    return {"status": "online", "project": "AI Trading Command Center", "mode": "demo"}

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/status")
def api_status():
    return {"connected": False, "provider": "alpaca", "market_data": "not_configured", "trading_enabled": False}
