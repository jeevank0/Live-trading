import os

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# WebSocket base URL for market data streams
# Testnet (Spot): wss://stream.testnet.binance.vision
# Mainnet (Spot): wss://stream.binance.com:9443
BINANCE_WS_BASE_URL = os.getenv(
    "BINANCE_WS_BASE_URL", "wss://stream.testnet.binance.vision")

SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# Strategy parameters
SMA_WINDOW = 20
EMA_WINDOW = 50

# Stop Loss variants
VARIANT_A_SL = 0.15  # 15%
VARIANT_B_SL = 0.10  # 10%

# Take Profit (same for both variants; variants differ only by SL)
TP_PERCENT = 0.02  # 2%

# Dummy order sizes for testnet. These should be small
ORDER_QUANTITIES = {
    "BTCUSDT": 0.001,
    "ETHUSDT": 0.01,
}
