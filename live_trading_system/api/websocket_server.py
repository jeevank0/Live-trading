import asyncio
import json
import os
import urllib.request
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect

app = FastAPI()


REST_BASE_URL = os.getenv("REST_BASE_URL", "http://127.0.0.1:8000")


def _fetch_candles(symbol: str, limit: int = 50):
    # Fetch candles from the REST server so the WS server can be run
    # as a separate process and still stream the correct live candles
    url = f"{REST_BASE_URL}/candles/{symbol}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        candles = json.loads(resp.read().decode("utf-8"))
    return candles[-limit:]


@app.websocket("/ws/candles/{symbol}")
async def websocket_candles(websocket: WebSocket, symbol: str):
    """Re-broadcast candle updates.

    This is the "custom WebSocket server" asked in the assignment.
    It pushes candle snapshots once per second.
    """
    symbol = symbol.upper()
    await websocket.accept()
    await websocket.send_json({"type": "subscribed", "symbol": symbol})

    try:
        while True:
            try:
                candles = _fetch_candles(symbol, limit=50)
                payload = {"type": "candles",
                           "symbol": symbol, "candles": candles}
            except Exception as exc:
                payload = {
                    "type": "error",
                    "symbol": symbol,
                    "message": f"Failed to fetch candles from REST ({REST_BASE_URL}): {exc}",
                }

            await websocket.send_json(
                payload
            )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
