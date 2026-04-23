# Live Trading System (Binance Testnet)

I built this as a simple end-to-end pipeline

What it does:

- Connects to Binance Spot Testnet WebSocket and listens to live trades (ticks)
- Keeps the latest tick in memory
- Builds 1-minute OHLC candles from the ticks
- Exposes data with a REST API (FastAPI)
- Runs a separate WebSocket server that re-broadcasts candles

Nothing is stored in a database. If you stop the app, the data resets

## How to run

### 1) Create venv and install

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r live_trading_system/requirements.txt
```

### 2) Start the REST server (port 8000)

This server also starts the Binance stream + strategy engine in the background

```bash
cd "live_trading_system"
python -u main.py
```

You should see logs like:

- Connected to Binance Testnet WebSocket
- Tick updated: BTCUSDT ...

### 3) Start the custom WebSocket server (port 8001)

Open a second terminal:

```bash
source "../.venv/bin/activate"
cd "live_trading_system"
python -m uvicorn api.websocket_server:app --host 0.0.0.0 --port 8001
```

If you see: “Uvicorn running on http://0.0.0.0:8001” then it’s running

Note: this WebSocket server reads candles by calling the REST server.
So the REST server must be running first.

## What to test

### REST checks

```bash
curl http://127.0.0.1:8000/tick/BTCUSDT
curl http://127.0.0.1:8000/candles/BTCUSDT
curl http://127.0.0.1:8000/trades
```

### WebSocket check (candle rebroadcast)

Start a third terminal:

```bash
source "../.venv/bin/activate"
cd "live_trading_system"
python -u scripts/ws_candles_client.py BTCUSDT
```

You should see JSON messages printing once per second

### Quick demo output (one command)

If you just want to see “it works” output fast:

```bash
source "../.venv/bin/activate"
cd "live_trading_system"
python -u scripts/demo_show_output.py
```

This prints REST output and also starts a temporary WebSocket server on port 8002 just for the demo.

## Config (optional)

- Symbols are in `config/settings.py` (`SYMBOLS` list)
- WebSocket base URL can be overridden with `BINANCE_WS_BASE_URL`
- Custom WS server can read REST from `REST_BASE_URL` (default: `http://127.0.0.1:8000`)
- If you set `BINANCE_API_KEY` and `BINANCE_API_SECRET`, the strategy will try to place testnet orders
  If keys are missing (or python-binance isn’t installed), it will log a skipped order instead of crashing

## Where the main code is

- `stream/binance_stream_client.py` (connects to Binance WS)
- `data/tick_store.py` (latest tick)
- `data/ohlc_aggregator.py` (1-minute candles)
- `strategies/engine.py` (runs SMA/EMA + variant A/B risk)
- `api/rest_server.py` (REST API)
- `api/websocket_server.py` (custom candle WS server)
- `main.py` (starts REST server)
