
import json
import unittest
from urllib.request import Request, urlopen

API = (
    "https://ai-trading-demo.onrender.com"
    "/api/analysis/candles"
)


def candles(start, step):
    return [
        {"close": start + i * step}
        for i in range(60)
    ]


def check_signal(stock_step, spx_step):
    frames = {
        "5": candles(200, stock_step),
        "30": candles(200, stock_step),
        "60": candles(200, stock_step),
    }

    payload = {
        "symbol": "TSLA",
        "frames": frames,
        "spx_candles": candles(200, spx_step),
    }

    request = Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise AssertionError(response.status)
        return json.load(response)


class TestLiveCandles(unittest.TestCase):

    def test_call(self):
        result = check_signal(1, 1)
        self.assertEqual(result["direction"], "CALL")
        self.assertEqual(
            result["status"], "ALIGNED_UNVERIFIED"
        )
        self.assertFalse(result["recommendation"])

    def test_put(self):
        result = check_signal(-1, -1)
        self.assertEqual(result["direction"], "PUT")
        self.assertEqual(
            result["status"], "ALIGNED_UNVERIFIED"
        )
        self.assertFalse(result["recommendation"])

    def test_conflict(self):
        result = check_signal(1, -1)
        self.assertEqual(result["direction"], "WAIT")
        self.assertEqual(result["status"], "CONFLICT")


if __name__ == "__main__":
    unittest.main()
