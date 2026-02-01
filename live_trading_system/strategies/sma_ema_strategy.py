import pandas as pd
from strategies.base_strategy import BaseStrategy

class SMAEMAStrategy(BaseStrategy):
    def __init__(self, sma_window, ema_window):
        self.sma_window = sma_window
        self.ema_window = ema_window

    def generate_signal(self, candles):
        df = pd.DataFrame(candles)
        df["SMA"] = df["close"].rolling(self.sma_window).mean()
        df["EMA"] = df["close"].ewm(span=self.ema_window).mean()

        if df["EMA"].iloc[-1] > df["SMA"].iloc[-1]:
            return "BUY"
        elif df["EMA"].iloc[-1] < df["SMA"].iloc[-1]:
            return "SELL"
        return None
