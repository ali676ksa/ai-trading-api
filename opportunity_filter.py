
from datetime import datetime, timezone

REQUIRED_FRAMES = ("5", "30", "60")
DIRECTIONS = ("CALL", "PUT")


def evaluate_candidate(data):
    symbol = str(data.get("symbol", "")).upper().strip()
    frames = data.get("frames", {})
    spx = str(data.get("spx_direction", "")).upper()

    reasons = []
    score = 0

    if not isinstance(frames, dict):
        frames = {}

    directions = [
        str(frames.get(frame, "")).upper()
        for frame in REQUIRED_FRAMES
    ]

    # All timeframes must agree with SPX
    aligned = (
        spx in DIRECTIONS
        and all(d == spx for d in directions)
    )

    if aligned:
        score += 40
    else:
        reasons.append("Timeframes or SPX conflict")

    # Confirmed price action
    if data.get("breakout_confirmed") is True:
        score += 20
    else:
        reasons.append("Breakout not confirmed")

    # Volume confirmation
    if data.get("volume_confirmed") is True:
        score += 15
    else:
        reasons.append("Volume not confirmed")

    # Market catalyst
    if data.get("catalyst_confirmed") is True:
        score += 10
    else:
        reasons.append("Catalyst not confirmed")

    # Options liquidity
    if data.get("options_liquidity_confirmed") is True:
        score += 15
    else:
        reasons.append("Options liquidity not confirmed")

    # Mandatory market-data verification
    verified = data.get("verified_market_data") is True
    fresh = data.get("fresh_market_data") is True

    if not verified:
        reasons.append("Market data not verified")

    if not fresh:
        reasons.append("Market data not fresh")

    ready = (
        aligned
        and score == 100
        and verified
        and fresh
    )

    return {
        "symbol": symbol,
        "direction": spx if aligned else "WAIT",
        "score": score,
        "status": (
            "PASSED_CHECKS"
            if ready
            else "REJECTED"
        ),
        "passes_filter": ready,
        "verified_market_data": verified,
        "reasons": reasons,
        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat()
    }


def rank_candidates(candidates):
    results = [
        evaluate_candidate(item)
        for item in candidates
    ]

    eligible = [
        item for item in results
        if item["passes_filter"]
    ]

    eligible.sort(
        key=lambda item: (-item["score"], item["symbol"])
    )

    return {
        "selected": eligible[:2],
        "all_results": results,
        "selected_count": min(2, len(eligible)),
        "note": (
            "Screening only. No live trading "
            "recommendation or order execution."
        )
    }
