
from fastapi import APIRouter, Body, HTTPException

from opportunity_filter import (
    rank_candidates
)

router = APIRouter(
    prefix="/api/opportunities"
)


@router.post("/evaluate")
def evaluate_opportunities(
    data: dict = Body(...)
):
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

    if not all(
        isinstance(item, dict)
        for item in candidates
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid candidate data"
        )

    # Evaluation only, not a trade order
    result = rank_candidates(candidates)

    return {
        **result,
        "mode": "experimental",
        "orders_enabled": False
    }
