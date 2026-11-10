
from collections import Counter
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo

from signal_store import get_connection
from opportunity_store import init_opportunity_table

RIYADH = ZoneInfo("Asia/Riyadh")


def get_daily_opportunity_stats(day=None):
    if day is None:
        selected_day = datetime.now(RIYADH).date()
    elif isinstance(day, str):
        selected_day = date.fromisoformat(day)
    elif isinstance(day, date):
        selected_day = day
    else:
        raise ValueError("Invalid date")

    start_local = datetime.combine(
        selected_day, time.min, tzinfo=RIYADH
    )
    end_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    init_opportunity_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT symbol, direction, score,
                       status, mode, reasons
                FROM opportunity_evaluations
                WHERE saved_at >= %s
                  AND saved_at < %s
                  AND mode = %s
                ORDER BY id DESC
                """,
                (start_utc, end_utc, "simulation_only")
            )
            rows = cur.fetchall()

    directions = Counter()
    statuses = Counter()
    rejection_reasons = Counter()
    scores = []
    symbols = set()

    for symbol, direction, score, status, mode, reasons in rows:
        if symbol:
            symbols.add(symbol)
        directions[direction] += 1
        statuses[status] += 1

        if score is not None:
            scores.append(float(score))

        if isinstance(reasons, list):
            for reason in reasons:
                if isinstance(reason, str):
                    rejection_reasons[reason] += 1

    return {
        "date": selected_day.isoformat(),
        "timezone": "Asia/Riyadh",
        "mode": "simulation_only",
        "total_evaluations": len(rows),
        "unique_symbols": len(symbols),
        "call_count": directions["CALL"],
        "put_count": directions["PUT"],
        "wait_count": directions["WAIT"],
        "rejected_count": statuses["REJECTED"],
        "average_score": (
            round(sum(scores) / len(scores), 2)
            if scores else None
        ),
        "top_rejection_reasons": [
            {"reason": reason, "count": count}
            for reason, count in rejection_reasons.most_common(10)
        ],
        "verified_market_data": False,
        "orders_enabled": False,
        "note": "Simulation statistics only. No trades executed."
    }
