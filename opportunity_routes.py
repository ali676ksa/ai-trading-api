
import os
import hmac

from fastapi import (
    APIRouter,
    Body,
    Header,
    HTTPException
)

from opportunity_filter import rank_candidates

from opportunity_store import (
    init_opportunity_table,
    save_opportunity_results,
    get_opportunity_history
)


router = APIRouter(prefix="/api/opportunities")


def authorize(secret):
    expected = os.getenv("SIGNALS_READ_SECRET")

    if (
        not expected
        or not secret
        or not hmac.compare_digest(secret, expected)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


@router.post("/evaluate")
def evaluate_opportunities(
    data: dict = Body(...),
    x_signals_secret: str | None = Header(default=None)
):
    authorize(x_signals_secret)

    candidates = data.get("candidates", [])

    if not isinstance(candidates, list):
        raise HTTPException(
            status_code=400,
            detail="Candidates must be a list"
        )

    if len(candidates) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 candidates"
        )

    if not all(
        isinstance(item, dict)
        for item in candidates
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid candidate data"
        )

    safe_candidates = []

    for item in candidates:
        safe_item = dict(item)

        # Manual inputs cannot verify market data.
        safe_item["verified_market_data"] = False
        safe_item["fresh_market_data"] = False

        safe_candidates.append(safe_item)

    result = rank_candidates(safe_candidates)

    try:
        init_opportunity_table()

        saved = save_opportunity_results(
            result["all_results"],
            mode="simulation_only"
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Opportunity storage unavailable"
        )

    return {
        **result,
        "selected": [],
        "selected_count": 0,
        "mode": "simulation_only",
        "market_data_connected": False,
        "orders_enabled": False,
        "storage": "neon_postgresql",
        "saved_count": saved["saved"],
        "note": (
            "Simulation only. "
            "No verified market data or trade signals."
        )
    }


@router.get("/history")
def opportunity_history(
    limit: int = 50,
    x_signals_secret: str | None = Header(default=None)
):
    authorize(x_signals_secret)

    try:
        init_opportunity_table()
        history = get_opportunity_history(limit)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Opportunity history unavailable"
        )

    return {
        "total": len(history),
        "mode": "simulation_only",
        "results": history
    }
