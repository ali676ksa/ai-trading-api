
# Fixed 50-stock options scanner watchlist
# No market data or trading orders are generated here.

WATCHLIST = [
    "NVDA",
    "AMD",
    "AVGO",
    "MU",
    "ARM",
    "MRVL",
    "SMCI",
    "INTC",
    "TSM",
    "ASML",
    "LRCX",
    "SNDK",
    "META",
    "AMZN",
    "MSFT",
    "AAPL",
    "GOOGL",
    "NFLX",
    "ORCL",
    "CRM",
    "CRWD",
    "NOW",
    "SHOP",
    "SNOW",
    "TSLA",
    "MSTR",
    "PLTR",
    "COIN",
    "HOOD",
    "APP",
    "RIVN",
    "SOFI",
    "PLUG",
    "CRCL",
    "MARA",
    "RIOT",
    "CVNA",
    "ROKU",
    "DKNG",
    "BA",
    "JPM",
    "BAC",
    "XOM",
    "F",
    "PFE",
    "WMT",
    "NKE",
    "PYPL",
    "ASTS",
    "UBER",
]

TOTAL_STOCKS = 50

assert len(WATCHLIST) == TOTAL_STOCKS
assert len(set(WATCHLIST)) == TOTAL_STOCKS


def get_watchlist():
    return {
        "total": TOTAL_STOCKS,
        "symbols": WATCHLIST.copy(),
        "source": "fixed_watchlist",
        "scanned_count": 0,
        "market_data_verified": False,
        "trading_enabled": False,
    }


def is_approved_symbol(symbol):
    if not isinstance(symbol, str):
        return False

    return symbol.strip().upper() in WATCHLIST
