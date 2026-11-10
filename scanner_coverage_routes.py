
import os
import hmac

from fastapi import APIRouter, Header, HTTPException
from scanner_coverage import get_scanner_coverage


router = APIRouter(
    prefix="/api/scanner",
    tags=["Scanner Coverage"]
)


@router.get("/coverage")
def scanner_coverage(
    x_signals_secret: str | None = Header(default=None)
):
    expected = os.getenv("SIGNALS_READ_SECRET")

    if (
        not expected
        or not x_signals_secret
        or not hmac.compare_digest(
            x_signals_secret,
            expected
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return get_scanner_coverage()
