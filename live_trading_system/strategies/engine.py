from datetime import datetime, timezone

from strategies.sma_ema_strategy import SMAEMAStrategy
from strategies.variants import StrategyVariant
from utils.logger import get_logger

logger = get_logger("StrategyEngine")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class StrategyEngine:
    """Runs strategy on finalized candles and manages per-variant risk state.

    Intern-style design: keep it simple and explicit.
    - We only trade long/flat (BUY enters, SELL exits).
    - We check SL/TP on every tick using the latest price.
    """

    def __init__(
        self,
        sma_window: int,
        ema_window: int,
        variant_a_sl: float,
        variant_b_sl: float,
        tp_percent: float,
        order_quantities,
        order_manager,
        trade_log,
        aggregator,
    ):
        self.strategy = SMAEMAStrategy(
            sma_window=sma_window, ema_window=ema_window)
        self.variants = {
            "A": StrategyVariant(name="A", sl_percent=variant_a_sl, tp_percent=tp_percent),
            "B": StrategyVariant(name="B", sl_percent=variant_b_sl, tp_percent=tp_percent),
        }
        self.order_quantities = order_quantities
        self.order_manager = order_manager
        self.trade_log = trade_log
        self.aggregator = aggregator

    def _qty_for(self, symbol: str) -> float:
        return float(self.order_quantities.get(symbol, 0.001))

    def _log(self, **data) -> None:
        # Keep the log as plain dicts so it's easy to inspect via REST
        self.trade_log.append(data)

    def on_tick(self, symbol: str, price: float, ts_ms: int) -> None:
        """Called on every tick to enforce SL/TP exits."""
        for variant in self.variants.values():
            if not variant.has_position(symbol):
                continue

            exit_reason = variant.check_exit(
                symbol=symbol, current_price=price)
            if not exit_reason:
                continue

            qty = variant.get_qty(symbol)
            pnl = variant.compute_pnl(symbol=symbol, current_price=price)

            order = self._safe_place_order(
                symbol=symbol, side="SELL", quantity=qty)
            variant.exit_position(symbol)

            self._log(
                timestamp=utc_now_iso(),
                symbol=symbol,
                variant=variant.name,
                event="EXIT",
                side="SELL",
                qty=qty,
                price=price,
                reason=exit_reason,
                pnl=pnl,
                order=order,
            )

    def on_candle_close(self, symbol: str) -> None:
        """Called when a 1-minute candle is finalized for a symbol."""
        candles = self.aggregator.get_finalized_candles(symbol, limit=250)
        if len(candles) < 5:
            return

        signal = self.strategy.generate_signal(candles)
        if signal not in ("BUY", "SELL"):
            return

        # Use last finalized close as the decision price.
        decision_price = float(candles[-1]["close"])

        if signal == "BUY":
            for variant in self.variants.values():
                if variant.has_position(symbol):
                    continue

                qty = self._qty_for(symbol)
                order = self._safe_place_order(
                    symbol=symbol, side="BUY", quantity=qty)
                variant.enter_position(
                    symbol=symbol, entry_price=decision_price, qty=qty)

                self._log(
                    timestamp=utc_now_iso(),
                    symbol=symbol,
                    variant=variant.name,
                    event="ENTRY",
                    side="BUY",
                    qty=qty,
                    price=decision_price,
                    reason="signal",
                    order=order,
                )

        if signal == "SELL":
            for variant in self.variants.values():
                if not variant.has_position(symbol):
                    continue

                qty = variant.get_qty(symbol)
                pnl = variant.compute_pnl(
                    symbol=symbol, current_price=decision_price)
                order = self._safe_place_order(
                    symbol=symbol, side="SELL", quantity=qty)
                variant.exit_position(symbol)

                self._log(
                    timestamp=utc_now_iso(),
                    symbol=symbol,
                    variant=variant.name,
                    event="EXIT",
                    side="SELL",
                    qty=qty,
                    price=decision_price,
                    reason="signal",
                    pnl=pnl,
                    order=order,
                )

    def _safe_place_order(self, symbol: str, side: str, quantity: float):
        """Place a testnet order if credentials exist; otherwise return a skipped record.

        The assignment asks for testnet order punching. This keeps the system running
        even if keys are missing or Binance rejects the request.
        """
        try:
            return self.order_manager.place_order(symbol=symbol, side=side, quantity=quantity)
        except Exception as exc:
            logger.warning(f"Order failed ({symbol} {side}): {exc}")
            return {
                "skipped": True,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "error": str(exc),
            }
