
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

WATCHLIST = [
    "NVDA", "TSLA", "MU", "AVGO", "AMD",
    "MSFT", "AAPL", "AMZN", "META", "GOOGL",
    "GOOG", "NFLX", "PLTR", "APP", "MSTR",
    "COIN", "HOOD", "CRWD", "PANW", "SNOW",
    "CRM", "ORCL", "ADBE", "INTC", "SNDK",
    "QCOM", "AMAT", "LRCX", "KLAC", "ARM",
    "SMCI", "DELL", "UBER", "SHOP", "ANET",
    "NOW", "TSM", "ASML", "JPM", "BAC",
    "GS", "V", "MA", "LLY", "UNH",
    "CAT", "XOM", "CVX", "COST", "WMT"
]

@app.get("/api/scanner")
def scanner():
    return {
        "mode": "watchlist_only",
        "data_connected": False,
        "total": len(WATCHLIST),
        "stocks": [
            {
                "symbol": symbol,
                "direction": "WAIT",
                "score": None,
                "entry": None,
                "target": None
            }
            for symbol in WATCHLIST
            
@app.get("/api/scanner")
def scanner():
    return {
        "status": "ready",
        "mode": "demo",
        "total_stocks": 50,
        "confirmed_opportunities": 0,
        "broker_connected": False,
        "message": "Scanner endpoint is working. Live market data is not connected yet."
    }

        ]
    }

