class BaseStrategy:
    def generate_signal(self, candles):
        raise NotImplementedError

    def apply_stop_loss(self, position, current_price):
        raise NotImplementedError
