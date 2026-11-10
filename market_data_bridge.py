
import os
import hmac
import re

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from pydantic import BaseModel, Field

from market_data_store import (
    init_market_data_table,
    save_market_quote,
    get_latest_market_quote
)


router = APIRouter(prefix="/api/market-data")

MAX_AGE_SECONDS = 60


# Input model
class Quote(BaseModel):
    symbol: str
    bid: float = Field(gt=0, allow_inf_nan=False)
    ask: float = Field(gt=0, allow_inf_nan=False)


# Secret authentication
def authorize(secret):
    expected = os.getenv("MARKET_DATA_BRIDGE_SECRET")

    if (
        not expected
        or not secret
        or not hmac.compare_digest(
            secret,
            expected
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


# Symbol validation
def normalize_symbol(symbol):
    symbol = str(symbol).strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9.\-]{1,15}",
        symbol
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid symbol"
        )

    return symbol


# Initialize storage
def prepare_database():
    try:
        init_market_data_table()

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Market data storage unavailable"
        )


# Save quote to Neon
@router.post("/ingest")
def ingest_quote(
    quote: Quote,
    x_market_data_secret: str | None = Header(
        default=None
    )
):
    authorize(x_market_data_secret)

    symbol = normalize_symbol(quote.symbol)

    if quote.ask < quote.bid:
        raise HTTPException(
            status_code=400,
            detail="Ask below bid"
        )

    prepare_database()

    try:
        quote_id = save_market_quote(
            symbol=symbol,
            bid=quote.bid,
            ask=quote.ask
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Failed to save market quote"
        )

    return {
        "accepted": True,
        "symbol": symbol,
        "quote_id": quote_id,
        "storage": "neon_postgresql",
        "source": "bridge_test",
        "verified_market_data": False,
        "usable_for_signals": False
    }


# Read latest quote from Neon
@router.get("/quote/{symbol}")
def get_quote(
    symbol: str,
    x_market_data_secret: str | None = Header(
        default=None
    )
):
    authorize(x_market_data_secret)

    symbol = normalize_symbol(symbol)

    prepare_database()

    try:
        quote = get_latest_market_quote(
            symbol
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Failed to read market quote"
        )

    if quote.get("status") == "no_data":
        return {
            "symbol": symbol,
            "status": "no_data",
            "storage": "neon_postgresql",
            "verified_market_data": False,
            "usable_for_signals": False
        }

    try:
        received = datetime.fromisoformat(
            quote["received_at"]
        )

        if received.tzinfo is None:
            raise ValueError(
                "Timestamp has no timezone"
            )

        age_seconds = max(
            0,
            (
                datetime.now(timezone.utc)
                - received
            ).total_seconds()
        )

    except (ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=503,
            detail="Invalid stored quote timestamp"
        )

    is_fresh = age_seconds <= MAX_AGE_SECONDS

    return {
        "symbol": symbol,
        "bid": quote["bid"],
        "ask": quote["ask"],
        "source": "bridge_test",
        "received_at": quote["received_at"],
        "age_seconds": round(
            age_seconds,
            1
        ),
        "status": (
            "fresh_test"
            if is_fresh
            else "stale"
        ),
        "storage": "neon_postgresql",
        "verified_market_data": False,
        "usable_for_signals": False
    }
