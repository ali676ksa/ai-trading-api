

from signal_engine import evaluate_signal

MIN_CANDLES = 60


def ema(values, period):
    """Calculate exponential moving average."""
    if len(values) < period:
        return None

    multiplier = 2 / (period + 1)
    result = sum(values[:period]) / period

    for price in values[period:]:
        result = (price - result) * multiplier + result

    return result


def candle_direction(candles):
    """
    candles: oldest to newest, CLOSED candles only.
    Each candle must contain a numeric 'close'.
    """
    if not isinstance(candles, list):
        return "WAIT"

    if len(candles) < MIN_CANDLES:
        return "WAIT"

    try:
        closes = []
        for candle in candles:
            value = float(candle["close"])
            if not (0 < value < float("inf")):
                return "WAIT"
            closes.append(value)
    except (TypeError, ValueError, KeyError):
        return "WAIT"

    fast = ema(closes, 20)
    slow = ema(closes, 50)
    latest = closes[-1]

    if fast is None or slow is None:
        return "WAIT"

    if latest > fast > slow:
        return "CALL"

    if latest < fast < slow:
        return "PUT"

    return "WAIT"


def analyze_candles(symbol, stock_frames, spx_candles):
    """
    stock_frames:
        {"5": [...], "30": [...], "60": [...]}

    spx_candles:
        closed SPX hourly candles
    """
    frames = {}

    if not isinstance(stock_frames, dict):
        stock_frames = {}

    for timeframe in ("5", "30", "60"):
        frames[timeframe] = candle_direction(
            stock_frames.get(timeframe)
        )

    spx_direction = candle_direction(spx_candles)

    result = evaluate_signal(
        symbol,
        frames,
        spx_direction
    )

    result["analysis_method"] = "EMA20_EMA50"
    result["source"] = "supplied_closed_candles"
    result["verified_market_data"] = False
    result["recommendation"] = False

    return result
