"""Shared in-memory state for the whole system.

This keeps things intern-simple: one place where we create the objects
that multiple servers/modules need.

Important: this is in-memory only (no DB). Restarting the process clears state.
"""

from data.tick_store import TickStore
from data.ohlc_aggregator import OHLCAggregator
from trading.order_manager import OrderManager
from strategies.engine import StrategyEngine
from config import settings


# Mutable set so we can add/remove symbols at runtime
active_symbols = set(settings.SYMBOLS)

# Shared data stores
tick_store = TickStore()
aggregator = OHLCAggregator()

# Trading + logs
order_manager = OrderManager()
trade_log = []  # list[dict]

# Strategy engine (uses the shared aggregator + order manager)
engine = StrategyEngine(
    sma_window=settings.SMA_WINDOW,
    ema_window=settings.EMA_WINDOW,
    variant_a_sl=settings.VARIANT_A_SL,
    variant_b_sl=settings.VARIANT_B_SL,
    tp_percent=settings.TP_PERCENT,
    order_quantities=settings.ORDER_QUANTITIES,
    order_manager=order_manager,
    trade_log=trade_log,
    aggregator=aggregator,
)
