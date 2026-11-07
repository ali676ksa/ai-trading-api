
import os
from datetime import datetime, timezone

# AI Trading Command Center
# Persistent Signal Storage - PostgreSQL


def get_connection():
    import psycopg

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    return psycopg.connect(database_url)


def init_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id BIGSERIAL PRIMARY KEY,
                    symbol VARCHAR(15) NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    timeframe VARCHAR(10) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    verified_market_data BOOLEAN
                        NOT NULL DEFAULT FALSE,
                    received_at TIMESTAMPTZ
                        NOT NULL DEFAULT NOW()
                )
            """)


def save_signal(
    symbol,
    direction,
    timeframe,
    source="TradingView",
    verified_market_data=False
):
    symbol = str(symbol).upper().strip()
    direction = str(direction).upper().strip()
    timeframe = str(timeframe).strip()

    if direction not in ("CALL", "PUT", "WAIT"):
        raise ValueError("Invalid direction")

    if timeframe not in ("5", "30", "60"):
        raise ValueError("Invalid timeframe")

    if not symbol or len(symbol) > 15:
        raise ValueError("Invalid symbol")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO trading_signals (
                    symbol,
                    direction,
                    timeframe,
                    source,
                    verified_market_data
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, received_at
            """, (
                symbol,
                direction,
                timeframe,
                source,
                verified_market_data
            ))

            signal_id, received_at = cur.fetchone()

    return {
        "id": signal_id,
        "symbol": symbol,
        "direction": direction,
        "timeframe": timeframe,
        "source": source,
        "verified_market_data": verified_market_data,
        "received_at": received_at.isoformat()
    }


def get_signals(limit=50):
    limit = max(1, min(int(limit), 100))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    symbol,
                    direction,
                    timeframe,
                    source,
                    verified_market_data,
                    received_at
                FROM trading_signals
                ORDER BY received_at DESC, id DESC
                LIMIT %s
            """, (limit,))

            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "symbol": row[1],
            "direction": row[2],
            "timeframe": row[3],
            "source": row[4],
            "verified_market_data": row[5],
            "received_at": row[6].isoformat()
        }
        for row in rows
    ]


def count_signals():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM trading_signals"
            )
            return cur.fetchone()[0]
