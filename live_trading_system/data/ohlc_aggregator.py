from collections import deque
from datetime import datetime


class OHLCAggregator:
    def __init__(self):
        # Stores finalized candles as a rolling history per symbol
        # Each candle is a dict: {minute, open, high, low, close}
        self.candles = {}

        # Current (still-forming) candle per symbol
        self._current = {}

        # Small in-memory history (finalized candles only)
        self._history_limit = 200

    def aggregate(self, symbol, tick):
        """Update OHLC using a tick.

        Returns the finalized candle dict when a minute closes, else returns None.
        """
        ts = datetime.utcfromtimestamp(tick["timestamp"] / 1000)
        minute = ts.replace(second=0, microsecond=0)
        minute_key = minute.isoformat() + "Z"

        if symbol not in self.candles:
            self.candles[symbol] = deque(maxlen=self._history_limit)

        current = self._current.get(symbol)
        if current is None:
            self._current[symbol] = {
                "minute": minute_key,
                "open": tick["price"],
                "high": tick["price"],
                "low": tick["price"],
                "close": tick["price"],
            }
            return None

        # If we moved into a new minute, finalize the previous candle
        if current["minute"] != minute_key:
            finalized = current
            self.candles[symbol].append(finalized)

            # Start a new candle for the new minute
            self._current[symbol] = {
                "minute": minute_key,
                "open": tick["price"],
                "high": tick["price"],
                "low": tick["price"],
                "close": tick["price"],
            }
            return finalized

        # Same minute: update current candle
        current["high"] = max(current["high"], tick["price"])
        current["low"] = min(current["low"], tick["price"])
        current["close"] = tick["price"]
        return None

    def get_candles_list(self, symbol, limit=200):
        history = list(self.candles.get(symbol, []))

        # Include the current in-progress candle at the end (useful for dashboards)
        current = self._current.get(symbol)
        if current is not None:
            history = history + [current]

        if limit is not None:
            history = history[-limit:]
        return history

    def get_finalized_candles(self, symbol, limit=200):
        """Return only finalized candles (no current in-progress candle)."""
        history = list(self.candles.get(symbol, []))
        if limit is not None:
            history = history[-limit:]
        return history
