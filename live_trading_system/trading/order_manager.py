from trading.binance_client import client
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
from utils.logger import get_logger

logger = get_logger("OrderManager")


class OrderManager:
    def __init__(self):
        self.trades = []

    def place_order(self, symbol, side, quantity):
        # If keys are missing, we don't crash the system
        # We still return a record so it can be logged as a "skipped" testnet action
        if not BINANCE_API_KEY or not BINANCE_API_SECRET:
            result = {
                "skipped": True,
                "reason": "missing_api_keys",
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity,
            }
            self.trades.append(result)
            logger.warning(
                "Order skipped (missing BINANCE_API_KEY/BINANCE_API_SECRET)")
            return result

        # If the python-binance package isn't installed, skip instead of crashing
        if client is None:
            result = {
                "skipped": True,
                "reason": "python_binance_not_installed",
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity,
            }
            self.trades.append(result)
            logger.warning(
                "Order skipped (python-binance not installed). Install `python-binance` to enable testnet punching."
            )
            return result

        order = client.create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )

        self.trades.append(order)
        logger.info(f"Order placed: {order}")
        return order
