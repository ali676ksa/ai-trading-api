from fastapi import HTTPException
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
        ]
    }



from integration_routes import router
app.include_router(router)

# AI Trading Signal Engine
from signal_engine import evaluate_signal
from fastapi import Body

@app.post("/api/analysis/evaluate")
def analyze_signal(data: dict = Body(...)):
    symbol = data.get("symbol", "")
    signals = data.get("signals", {})
    spx_direction = data.get("spx_direction")

    if not isinstance(signals, dict):
        raise HTTPException(
            status_code=400,
            detail="signals must be an object"
        )

    return evaluate_signal(
        symbol=symbol,
        signals=signals,
        spx_direction=spx_direction
    )

# Candle analysis - experimental endpoint
from candle_engine import analyze_candles


@app.post("/api/analysis/candles")
def analyze_candle_request(data: dict = Body(...)):
    symbol = data.get("symbol", "")
    frames = data.get("frames", {})
    spx_candles = data.get("spx_candles", [])

    if not isinstance(frames, dict):
        raise HTTPException(
            status_code=400,
            detail="frames must be an object"
        )

    return analyze_candles(
        symbol=symbol,
        stock_frames=frames,
        spx_candles=spx_candles
    )

