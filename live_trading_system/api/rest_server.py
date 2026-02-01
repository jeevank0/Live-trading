import asyncio
from fastapi import FastAPI
from stream.binance_stream_client import BinanceStreamClient
import app_state

app = FastAPI()


def _start_stream_task():
    client = BinanceStreamClient(
        sorted(app_state.active_symbols),
        tick_store=app_state.tick_store,
        aggregator=app_state.aggregator,
        on_tick=app_state.engine.on_tick,
        on_candle_close=app_state.engine.on_candle_close,
    )
    app.state.stream_task = asyncio.create_task(client.connect())


@app.on_event("startup")
async def startup_event():
    # run the market stream as a background task
    _start_stream_task()


@app.on_event("shutdown")
async def shutdown_event():
    task = getattr(app.state, "stream_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@app.get("/candles/{symbol}")
def get_candles(symbol: str):
    return app_state.aggregator.get_candles_list(symbol)


@app.get("/tick/{symbol}")
def get_tick(symbol: str):
    return app_state.tick_store.get_tick(symbol)


@app.get("/trades")
def get_trades():
    # Simple in-memory log
    return app_state.trade_log


@app.get("/symbols")
def get_symbols():
    return sorted(app_state.active_symbols)


@app.post("/symbols/add/{symbol}")
async def add_symbol(symbol: str):
    app_state.active_symbols.add(symbol.upper())
    # Restart stream task so Binance URL includes the new symbol
    task = getattr(app.state, "stream_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    _start_stream_task()
    return {"ok": True, "symbols": sorted(app_state.active_symbols)}


@app.post("/symbols/remove/{symbol}")
async def remove_symbol(symbol: str):
    app_state.active_symbols.discard(symbol.upper())
    task = getattr(app.state, "stream_task", None)
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    _start_stream_task()
    return {"ok": True, "symbols": sorted(app_state.active_symbols)}
