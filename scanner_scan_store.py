
from datetime import datetime
from zoneinfo import ZoneInfo

from signal_store import get_connection
from scanner_watchlist import is_approved_symbol


RIYADH = ZoneInfo("Asia/Riyadh")


def init_scanner_scan_table():
    """Create the scanner history table in Neon."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scanner_scan_records (
                    id BIGSERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    scan_time TIMESTAMPTZ NOT NULL
                        DEFAULT NOW(),
                    data_source VARCHAR(100) NOT NULL,
                    scan_status VARCHAR(30) NOT NULL,
                    market_data_verified BOOLEAN NOT NULL
                        DEFAULT FALSE,
                    mode VARCHAR(30) NOT NULL
                        DEFAULT 'simulation_only'
                )
            """)

        conn.commit()


def save_test_scan(symbol):
    """
    Store a simulation record only.
    Never mark test data as verified.
    """

    symbol = symbol.strip().upper()

    if not is_approved_symbol(symbol):
        raise ValueError("Symbol not in approved watchlist")

    init_scanner_scan_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO scanner_scan_records (
                    symbol,
                    data_source,
                    scan_status,
                    market_data_verified,
                    mode
                )
                VALUES (%s, %s, %s, FALSE, %s)
                RETURNING id
            """, (
                symbol,
                "manual_test",
                "TEST_ONLY",
                "simulation_only"
            ))

            scan_id = cur.fetchone()[0]

        conn.commit()

    return {
        "id": scan_id,
        "symbol": symbol,
        "status": "TEST_ONLY",
        "market_data_verified": False,
        "mode": "simulation_only"
    }


def get_scanner_scan_history(limit=50):
    """Read recent scanner records from Neon."""

    init_scanner_scan_table()

    limit = max(1, min(int(limit), 200))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    symbol,
                    scan_time,
                    data_source,
                    scan_status,
                    market_data_verified,
                    mode
                FROM scanner_scan_records
                ORDER BY id DESC
                LIMIT %s
            """, (limit,))

            rows = cur.fetchall()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "symbol": row[1],
            "scan_time": row[2].isoformat(),
            "data_source": row[3],
            "scan_status": row[4],
            "market_data_verified": row[5],
            "mode": row[6]
        })

    return {
        "total": len(results),
        "timezone": "Asia/Riyadh",
        "results": results
    }
