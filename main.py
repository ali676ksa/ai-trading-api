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

# Interactive Brokers connection status
from ibkr_adapter import IBKRAdapter

@app.get("/api/ibkr/status")
def ibkr_status():
    adapter = IBKRAdapter()
    return adapter.status()


# IBKR stock market data
@app.get("/api/ibkr/stock/{symbol}")
def ibkr_stock(symbol: str):
    adapter = IBKRAdapter()
    return adapter.get_stock_price(symbol)


# IBKR options market data
@app.get("/api/ibkr/options/{symbol}")
def ibkr_options(symbol: str):
    adapter = IBKRAdapter()
    return adapter.get_option_chain(symbol)
    
# Market data bridge
from market_data_bridge import router as market_data_router

app.include_router(market_data_router)


# Opportunity filtering engine
from opportunity_routes import router as opportunity_router

app.include_router(opportunity_router)


# Daily opportunity statistics
from opportunity_stats_routes import router as stats_router

app.include_router(stats_router)

