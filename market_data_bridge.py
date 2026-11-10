 
import os
import hmac
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/market-data")

# Temporary memory only - cleared on server restart
quotes = {}


class Quote(BaseModel):
    symbol: str
    bid: float = Field(gt=0)
    ask: float = Field(gt=0)


def authorize(secret):
    expected = os.getenv("MARKET_DATA_BRIDGE_SECRET")

    if not expected or not secret or not hmac.compare_digest(
        secret, expected
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


@router.post("/ingest")
def ingest_quote(
    quote: Quote,
    x_market_data_secret: str | None = Header(default=None)
):
    authorize(x_market_data_secret)

    symbol = quote.symbol.strip().upper()

    if not re.fullmatch(r"[A-Z0-9.\-]{1,15}", symbol):
        raise HTTPException(400, "Invalid symbol")

    if quote.ask < quote.bid:
        raise HTTPException(400, "Ask below bid")

    received_at = datetime.now(timezone.utc).isoformat()

    quotes[symbol] = {
        "symbol": symbol,
        "bid": quote.bid,
        "ask": quote.ask,
        "received_at": received_at,
        "verified_market_data": False,
        "source": "bridge_test"
    }

    return {
        "accepted": True,
        "symbol": symbol,
        "verified_market_data": False
    }


@router.get("/quote/{symbol}")
def get_quote(
    symbol: str,
    x_market_data_secret: str | None = Header(default=None)
):
    authorize(x_market_data_secret)

    return quotes.get(symbol.upper(), {
        "symbol": symbol.upper(),
        "status": "no_data",
        "verified_market_data": False
    })
