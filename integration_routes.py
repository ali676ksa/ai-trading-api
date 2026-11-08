
import os
import hmac
from fastapi import APIRouter, HTTPException, Request

from signal_store import (
    save_signal,
    get_signals,
    count_signals
)

router = APIRouter()

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
    try:
        total = count_signals()
        database_connected = True
    except Exception:
        total = 0
        database_connected = False

    return {
        "status": "ready",
        "tradingview": "webhook_ready",
        "ibkr": "not_connected",
        "signals_received": total,
        "live_prices": False,
        "database_connected": database_connected
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

    symbol = str(
        data.get("symbol", "")
    ).upper().strip()

    direction = str(
        data.get("direction", "")
    ).upper().strip()

    timeframe = str(
        data.get("timeframe", "")
    ).strip()

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

    return {
        "accepted": True,
        "signal": signal
    }


@router.get("/api/integration/signals")
def list_saved_signals(request: Request):
    read_secret = os.getenv("SIGNALS_READ_SECRET")

    if not read_secret:
        raise HTTPException(
            status_code=503,
            detail="Signal access not configured"
        )

    supplied_secret = request.headers.get(
        "X-Signals-Secret", ""
    )

    if not hmac.compare_digest(
        supplied_secret, read_secret
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

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
        "note": (
            "Unverified alerts, "
            "not trade recommendations"
        )
    }
