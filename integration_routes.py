
import os
import hmac
from signal_store import save_signal, get_signals
from datetime import datetime, timezone
from collections import deque
from threading import Lock

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

signals = deque(maxlen=100)
signals_lock = Lock()

ALLOWED_SYMBOLS = {
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
}


@router.get("/api/integration/status")
def integration_status():
    return {
        "status": "ready",
        "tradingview": "webhook_ready",
        "ibkr": "not_connected",
        "signals_received": len(signals),
        "live_prices": False
    }


@router.post("/api/tradingview/webhook")
async def tradingview_webhook(request: Request):

    secret = os.getenv("TRADINGVIEW_WEBHOOK_SECRET")

    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Webhook secret not configured"
        )

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON"
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="JSON object required"
        )

    supplied_secret = data.get("secret", "")

    if not isinstance(supplied_secret, str):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    if not hmac.compare_digest(
        supplied_secret, secret
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    symbol = str(data.get("symbol", "")).upper().strip()
    direction = str(
        data.get("direction", "")
    ).upper().strip()

    timeframe = str(data.get("timeframe", "")).strip()

    if symbol not in ALLOWED_SYMBOLS:
        raise HTTPException(
            status_code=400,
            detail="Symbol not allowed"
        )

    if direction not in {"CALL", "PUT", "WAIT"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid direction"
        )

    if timeframe not in {"5", "30", "60"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid timeframe"
        )

    signal = {
        "symbol": symbol,
        "direction": direction,
        "timeframe": timeframe,
        "source": "TradingView",
        "received_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "verified_market_data": False
    }

    
    try:
        signal = save_signal(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            source="TradingView",
            verified_market_data=False
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Signal storage unavailable"
        )


@router.get("/api/integration/signals")
def list_saved_signals():
    try:
        items = get_signals(limit=50)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Signal storage 
@router.get("/api/integration/signals")
def list_saved_signals():
    try:
        items = get_signals(limit=50)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Signal storage unavailable"
        )

    return {
        "total": len(items),
        "signals": items,
        "note": "Unverified alerts, not trade recommendations"
    }

    }


@router.get("/api/integration/signals")
def get_signals():
    with signals_lock:
        items = list(signals)

    return {
        "total": len(items),
        "signals": items,
        "note": "Unverified alerts, not trade recommendations"
    }
