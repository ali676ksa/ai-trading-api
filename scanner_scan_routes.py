
import os
import hmac

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from scanner_scan_store import (
    save_test_scan,
    get_scanner_scan_history,
)

router = APIRouter(
    prefix="/api/scanner",
    tags=["Scanner Scan History"]
)


class TestScanRequest(BaseModel):
    symbol: str


def require_secret(value):
    expected = os.getenv("SIGNALS_READ_SECRET")

    if (
        not expected
        or not value
        or not hmac.compare_digest(value, expected)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


@router.post("/test-scan")
def create_test_scan(
    payload: TestScanRequest,
    x_signals_secret: str | None = Header(default=None),
):
    require_secret(x_signals_secret)

    try:
        return save_test_scan(payload.symbol)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unapproved symbol"
        )


@router.get("/scans")
def list_scans(
    limit: int = 50,
    x_signals_secret: str | None = Header(default=None),
):
    require_secret(x_signals_secret)

    return get_scanner_scan_history(limit)
