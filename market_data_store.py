

from signal_store import get_connection


# Separate table for market data
def init_market_data_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS market_quotes (
                    id BIGSERIAL PRIMARY KEY,
                    symbol VARCHAR(15) NOT NULL,
                    bid DOUBLE PRECISION NOT NULL,
                    ask DOUBLE PRECISION NOT NULL,
                    source VARCHAR(50) NOT NULL
                        DEFAULT 'bridge_test',
                    verified_market_data BOOLEAN NOT NULL
                        DEFAULT FALSE,
                    received_at TIMESTAMPTZ NOT NULL
                        DEFAULT NOW()
                )
            """)


# Save a quote without marking it verified
def save_market_quote(symbol, bid, ask):
    symbol = str(symbol).strip().upper()
    bid = float(bid)
    ask = float(ask)

    if not symbol or bid <= 0 or ask < bid:
        raise ValueError("Invalid quote")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO market_quotes
                    (symbol, bid, ask,
                     source, verified_market_data)
                VALUES (%s, %s, %s, %s, FALSE)
                RETURNING id
            """, (
                symbol,
                bid,
                ask,
                "bridge_test"
            ))

            quote_id = cur.fetchone()[0]

    return quote_id


# Retrieve the latest saved quote
def get_latest_market_quote(symbol):
    symbol = str(symbol).strip().upper()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    symbol,
                    bid,
                    ask,
                    source,
                    verified_market_data,
                    received_at
                FROM market_quotes
                WHERE symbol = %s
                ORDER BY received_at DESC, id DESC
                LIMIT 1
            """, (symbol,))

            row = cur.fetchone()

    if row is None:
        return {
            "symbol": symbol,
            "status": "no_data",
            "verified_market_data": False,
            "usable_for_signals": False
        }

    return {
        "symbol": row[0],
        "bid": row[1],
        "ask": row[2],
        "source": row[3],
        "verified_market_data": False,
        "received_at": row[5].isoformat(),
        "usable_for_signals": False
    }
