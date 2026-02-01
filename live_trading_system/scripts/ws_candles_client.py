import asyncio
import json
import sys

import websockets


def _usage() -> str:
    return "Usage: python -u scripts/ws_candles_client.py <SYMBOL> [URL]"


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(_usage())

    symbol = sys.argv[1].upper()
    url = sys.argv[2] if len(
        sys.argv) >= 3 else f"ws://127.0.0.1:8001/ws/candles/{symbol}"

    print(f"Connecting to: {url}")
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            try:
                data = json.loads(msg)
                print(json.dumps(data, indent=2))
            except Exception:
                print(msg)


if __name__ == "__main__":
    asyncio.run(main())
