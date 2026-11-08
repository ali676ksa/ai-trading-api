

import unittest

from candle_engine import candle_direction, analyze_candles


def make_candles(start, step, count=60):
    return [
        {"close": start + i * step}
        for i in range(count)
    ]


class TestCandleEngine(unittest.TestCase):

    def test_call(self):
        candles = make_candles(100, 1)
        self.assertEqual(candle_direction(candles), "CALL")

    def test_put(self):
        candles = make_candles(200, -1)
        self.assertEqual(candle_direction(candles), "PUT")

    def test_wait(self):
        candles = make_candles(100, 0)
        self.assertEqual(candle_direction(candles), "WAIT")

    def test_insufficient_candles(self):
        candles = make_candles(100, 1, 20)
        self.assertEqual(candle_direction(candles), "WAIT")

    def test_spx_alignment(self):
        candles = make_candles(100, 1)
        frames = {
            "5": candles,
            "30": candles,
            "60": candles,
        }

        result = analyze_candles(
            "TSLA", frames, candles
        )

        self.assertEqual(result["direction"], "CALL")
        self.assertEqual(
            result["status"], "ALIGNED_UNVERIFIED"
        )
        self.assertFalse(result["recommendation"])


if __name__ == "__main__":
    unittest.main()
