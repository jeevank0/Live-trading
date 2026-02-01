from utils.logger import get_logger

logger = get_logger("TickStore")


class TickStore:
    def __init__(self):
        self.ticks = {}

    def update_tick(self, symbol, price, ts):
        self.ticks[symbol] = {"price": price, "timestamp": ts}
        logger.info(f"Tick updated: {symbol} {price}")

    def get_tick(self, symbol):
        return self.ticks.get(symbol)
