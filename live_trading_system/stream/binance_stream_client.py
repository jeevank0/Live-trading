import asyncio
import websockets
import json
import ssl
import certifi
from utils.logger import get_logger
from data.tick_store import TickStore
from config.settings import BINANCE_WS_BASE_URL

logger = get_logger("BinanceStreamClient")


class BinanceStreamClient:
    def __init__(self, symbols, tick_store=None, aggregator=None, on_tick=None, on_candle_close=None):
        self.symbols = symbols
        self.tick_store = tick_store or TickStore()
        self.aggregator = aggregator
        self.on_tick = on_tick
        self.on_candle_close = on_candle_close

    async def connect(self):
        """Connect to Binance market streams and keep reconnecting on disconnect.

        This is intentionally simple: if the socket drops, we wait a bit and try again.
        """
        streams = [f"{s.lower()}@trade" for s in self.symbols]
        url = f"{BINANCE_WS_BASE_URL}/stream?streams=" + "/".join(streams)
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        while True:
            try:
                async with websockets.connect(url, ssl=ssl_context) as ws:
                    logger.info("Connected to Binance Testnet WebSocket")

                    async for msg in ws:
                        data = json.loads(msg)
                        if "data" in data:  # trade event
                            symbol = data["data"]["s"]
                            price = float(data["data"]["p"])
                            ts = int(data["data"]["T"])
                            self.tick_store.update_tick(symbol, price, ts)

                            if self.aggregator is not None:
                                finalized = self.aggregator.aggregate(
                                    symbol, {"price": price, "timestamp": ts}
                                )

                                if finalized is not None and self.on_candle_close is not None:
                                    # A candle just closed for this symbol
                                    self.on_candle_close(symbol)

                            if self.on_tick is not None:
                                self.on_tick(symbol, price, ts)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning(f"Stream disconnected, retrying soon: {exc}")
                await asyncio.sleep(2)
