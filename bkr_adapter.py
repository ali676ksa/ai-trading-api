

from datetime import datetime, timezone

# IBKR adapter - preparation stage
# Read-only. No trading functions.

class IBKRAdapter:
    def __init__(self):
        self.connected = False
        self.read_only = True

    def status(self):
        return {
            "provider": "Interactive Brokers",
            "status": "not_connected",
            "connected": self.connected,
            "read_only": self.read_only,
            "live_prices": False,
            "checked_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def get_stock_price(self, symbol):
        return {
            "symbol": str(symbol).upper(),
            "price": None,
            "status": "not_connected",
            "verified_market_data": False
        }

    def get_option_chain(self, symbol):
        return {
            "symbol": str(symbol).upper(),
            "contracts": [],
            "status": "not_connected",
            "verified_market_data": False
        }
