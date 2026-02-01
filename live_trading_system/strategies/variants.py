class StrategyVariant:
    """Per-variant risk wrapper.

    Intern-level approach:
    - Track positions in memory.
    - Variant A and B differ only by stop loss percent.
    - TP is supported (same TP for both variants).
    """

    def __init__(self, name: str, sl_percent: float, tp_percent: float):
        self.name = name
        self.sl_percent = float(sl_percent)
        self.tp_percent = float(tp_percent)
        self.positions = {}

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def get_qty(self, symbol: str) -> float:
        pos = self.positions.get(symbol) or {}
        return float(pos.get("qty", 0))

    def enter_position(self, symbol: str, entry_price: float, qty: float):
        # long-only positions
        self.positions[symbol] = {
            "entry": float(entry_price), "qty": float(qty)}

    def exit_position(self, symbol: str):
        self.positions.pop(symbol, None)

    def compute_pnl(self, symbol: str, current_price: float) -> float:
        pos = self.positions.get(symbol)
        if not pos:
            return 0.0
        entry = float(pos["entry"])
        qty = float(pos.get("qty", 0))
        return (float(current_price) - entry) * qty

    def check_exit(self, symbol: str, current_price: float):
        """Returns exit reason string if SL/TP is hit, else returns None."""
        pos = self.positions.get(symbol)
        if not pos:
            return None

        entry = float(pos["entry"])
        px = float(current_price)

        if px <= entry * (1 - self.sl_percent):
            return "stop_loss"
        if px >= entry * (1 + self.tp_percent):
            return "take_profit"

        return None
