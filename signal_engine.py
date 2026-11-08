
from datetime import datetime, timezone

VALID_DIRECTIONS = {"CALL", "PUT"}


def evaluate_signal(symbol, signals, spx_direction=None):
    """
    signals مثال:
    {"60": "CALL", "30": "CALL", "5": "CALL"}

    تقييم توافق الإشارات فقط.
    لا يستخدم أسعارًا مباشرة ولا يتنبأ بالعوائد.
    """

    symbol = str(symbol).strip().upper()

    if not symbol:
        raise ValueError("Symbol is required")

    frames = {}

    for timeframe in ("60", "30", "5"):
        value = signals.get(timeframe)
        frames[timeframe] = (
            str(value).strip().upper()
            if value is not None else None
        )

    spx = (
        str(spx_direction).strip().upper()
        if spx_direction is not None else None
    )

    missing = [
        frame for frame, direction in frames.items()
        if direction not in VALID_DIRECTIONS
    ]

    result = {
        "symbol": symbol,
        "direction": "WAIT",
        "status": "INSUFFICIENT_DATA",
        "score": None,
        "frames": frames,
        "spx_direction": spx,
        "verified_market_data": False,
        "recommendation": False,
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    if missing or spx not in VALID_DIRECTIONS:
        result["reason"] = (
            "Missing or invalid timeframe/SPX signals"
        )
        return result

    hourly = frames["60"]

    if (
        frames["30"] != hourly
        or frames["5"] != hourly
        or spx != hourly
    ):
        result["status"] = "CONFLICT"
        result["reason"] = (
            "Timeframes or SPX direction do not agree"
        )
        return result

    result["direction"] = hourly
    result["status"] = "ALIGNED_UNVERIFIED"
    result["reason"] = (
        "Directional agreement only; "
        "market data and option pricing not verified"
    )

    return result
