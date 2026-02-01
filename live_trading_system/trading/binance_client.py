"""Binance client wrapper.

We keep this import-safe so the rest of the project can still run
even if `python-binance` is not installed.
"""

from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET

try:
    from binance.client import Client  # type: ignore
except ModuleNotFoundError:
    Client = None


if Client is None:
    client = None
else:
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=True)
