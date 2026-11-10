
from fastapi import APIRouter, Body, HTTPException

from opportunity_filter import rank_candidates

router = APIRouter(prefix="/api/opportunities")


@router.post("/evaluate")
def evaluate_opportunities(data: dict = Body(...)):
    candidates = data.get("candidates", [])

    if not isinstance(candidates, list):
        raise HTTPException(
            status_code=400,
            detail="candidates must be a list"
        )

    if len(candidates) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 candidates"
        )

    if not all(isinstance(item, dict) for item in candidates):
        raise HTTPException(
            status_code=400,
            detail="Invalid candidate data"
        )

    # Public input is never trusted as verified market data.
    safe_candidates = []

    for item in candidates:
        safe_item = dict(item)

        safe_item["verified_market_data"] = False
        safe_item["fresh_market_data"] = False

        safe_candidates.append(safe_item)

    result = rank_candidates(safe_candidates)

    return {
        **result,
        "selected": [],
        "selected_count": 0,
        "mode": "simulation_only",
        "market_data_connected": False,
        "orders_enabled": False,
        "note": (
            "Manual data cannot verify market prices. "
            "No live trade recommendations."
        )
    }
