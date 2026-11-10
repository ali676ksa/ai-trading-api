
import json
from datetime import datetime, timezone

from signal_store import get_connection


# Create a separate table for opportunity evaluations
def init_opportunity_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS opportunity_evaluations (
                    id BIGSERIAL PRIMARY KEY,
                    symbol VARCHAR(15) NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    score INTEGER NOT NULL,
                    status VARCHAR(30) NOT NULL,
                    passes_filter BOOLEAN NOT NULL DEFAULT FALSE,
                    verified_market_data BOOLEAN NOT NULL DEFAULT FALSE,
                    mode VARCHAR(30) NOT NULL DEFAULT 'simulation_only',
                    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
                    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)


# Save screening results safely
def save_opportunity_results(results, mode="simulation_only"):
    if not isinstance(results, list):
        raise ValueError("Results must be a list")

    if mode != "simulation_only":
        raise ValueError("Only simulation results are allowed")

    saved_ids = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for result in results:
                if not isinstance(result, dict):
                    raise ValueError("Invalid result")

                symbol = str(
                    result.get("symbol", "")
                ).strip().upper()

                direction = str(
                    result.get("direction", "WAIT")
                ).strip().upper()

                score = result.get("score", 0)

                reasons = result.get("reasons", [])

                if (
                    not symbol
                    or len(symbol) > 15
                    or direction not in ("CALL", "PUT", "WAIT")
                    or type(score) is not int
                    or not 0 <= score <= 100
                    or not isinstance(reasons, list)
                ):
                    raise ValueError("Invalid evaluation data")

                if not all(
                    isinstance(reason, str)
                    for reason in reasons
                ):
                    raise ValueError("Invalid reasons")

                timestamp = result.get("evaluated_at")

                if timestamp:
                    evaluated_at = datetime.fromisoformat(
                        str(timestamp).replace("Z", "+00:00")
                    )
                    if evaluated_at.tzinfo is None:
                        raise ValueError("Timezone required")
                else:
                    evaluated_at = datetime.now(timezone.utc)

                cur.execute("""
                    INSERT INTO opportunity_evaluations (
                        symbol,
                        direction,
                        score,
                        status,
                        passes_filter,
                        verified_market_data,
                        mode,
                        reasons,
                        evaluated_at
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        FALSE, FALSE, %s, %s, %s
                    )
                    RETURNING id
                """, (
                    symbol,
                    direction,
                    score,
                    "REJECTED",
                    mode,
                    json.dumps(reasons, ensure_ascii=False),
                    evaluated_at
                ))

                saved_ids.append(cur.fetchone()[0])

    return {
        "saved": len(saved_ids),
        "ids": saved_ids,
        "mode": mode
    }


# Read saved evaluations
def get_opportunity_history(limit=50):
    limit = max(1, min(int(limit), 100))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    symbol,
                    direction,
                    score,
                    status,
                    passes_filter,
                    verified_market_data,
                    mode,
                    reasons,
                    evaluated_at,
                    saved_at
                FROM opportunity_evaluations
                ORDER BY id DESC
                LIMIT %s
            """, (limit,))

            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "symbol": row[1],
            "direction": row[2],
            "score": row[3],
            "status": row[4],
            "passes_filter": row[5],
            "verified_market_data": row[6],
            "mode": row[7],
            "reasons": row[8],
            "evaluated_at": row[9].isoformat(),
            "saved_at": row[10].isoformat()
        }
        for row in rows
    ]
