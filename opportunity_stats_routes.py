
import os
import hmac

from fastapi import APIRouter, Header, HTTPException
from opportunity_stats import get_daily_opportunity_stats

router = APIRouter(prefix="/api/opportunities")


@router.get("/stats/daily")
def daily_opportunity_stats(
    day: str | None = None,
    x_signals_secret: str | None = Header(default=None)
):
    expected = os.getenv("SIGNALS_READ_SECRET")

    if (
        not expected
        or not x_signals_secret
        or not hmac.compare_digest(
            x_signals_secret, expected
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    try:
        return get_daily_opportunity_stats(day)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date. Use YYYY-MM-DD"
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Statistics unavailable"
        )
