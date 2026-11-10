
from datetime import datetime
from zoneinfo import ZoneInfo


RIYADH = ZoneInfo("Asia/Riyadh")

TOTAL_STOCKS = 50


def get_scanner_coverage():
    """
    Coverage status for the 50-stock scanner.

    A stock is counted as verified only after
    a trusted scanner records a validated scan.
    """

    return {
        "date": datetime.now(RIYADH).date().isoformat(),
        "timezone": "Asia/Riyadh",
        "total_stocks": TOTAL_STOCKS,
        "verified_scanned": 0,
        "remaining": TOTAL_STOCKS,
        "coverage_percent": 0,
        "status": "awaiting_verified_scans",
        "market_data_verified": False,
        "mode": "simulation_only",
        "message": (
            "No verified scans recorded. "
            "Historical simulation results "
            "are not counted as live coverage."
        )
    }
