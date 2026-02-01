import asyncio
import json
import subprocess
import sys
import time
import urllib.request


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def show_rest():
    print("REST /tick/BTCUSDT ->")
    print(fetch_json("http://127.0.0.1:8000/tick/BTCUSDT"))

    print("\nREST /candles/BTCUSDT ->")
    candles = fetch_json("http://127.0.0.1:8000/candles/BTCUSDT")
    print(f"candles_count={len(candles)}")
    if candles:
        print("last_candle=", candles[-1])


async def show_ws(port: int = 8002):
    import websockets

    url = f"ws://127.0.0.1:{port}/ws/candles/BTCUSDT"
    print(f"\nWS connect -> {url}")

    async with websockets.connect(url, open_timeout=5) as ws:
        print("WS msg 1 ->", await ws.recv())
        msg2 = await ws.recv()
        print("WS msg 2 (truncated) ->",
              msg2[:220] + ("..." if len(msg2) > 220 else ""))


def main():
    show_rest()

    # Start WS server briefly for demo (uses REST as its candle source)
    p = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.websocket_server:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8002",
            "--log-level",
            "warning",
        ]
    )

    try:
        time.sleep(1)
        asyncio.run(show_ws(port=8002))
    finally:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


if __name__ == "__main__":
    main()
