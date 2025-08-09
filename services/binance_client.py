import os, time
from typing import Dict
from binance.client import Client
from binance.enums import (
    SIDE_BUY, SIDE_SELL,
    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, ORDER_TYPE_STOP_LOSS_LIMIT, ORDER_TYPE_TAKE_PROFIT_LIMIT
)
from binance.enums import TIME_IN_FORCE_GTC
from binance.exceptions import BinanceAPIException, BinanceRequestException

BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
BINANCE_API_BASE = os.getenv("BINANCE_API_BASE", "").strip()
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

def make_client(api_key: str, api_secret: str) -> Client | None:
    if PAPER_TRADING:
        return None  # paper: não instanciamos client real
    client = Client(api_key, api_secret, tld='com', testnet=BINANCE_TESTNET)
    if BINANCE_API_BASE:
        client.API_URL = f"{BINANCE_API_BASE}/api"
    return client

def _ok(order: Dict): return {"ok": True, "order": order}
def _err(e: Exception):
    code = getattr(e, "status_code", "")
    return {"ok": False, "error": f"{code} {str(e)}"}

def _paper_order(symbol, side, tipo, qty, price=0.0, extra=None):
    now = int(time.time()*1000)
    return _ok({
        "paper": True, "symbol": symbol, "side": side, "type": tipo,
        "origQty": qty, "price": price, "extra": extra or {}, "transactTime": now, "orderId": now
    })

def test_account(client: Client | None) -> dict:
    if PAPER_TRADING:
        return {"ok": True, "balances": {"USDT": 10000.0}}
    try:
        info = client.get_account()
        balances = {b['asset']: float(b['free']) for b in info.get('balances', []) if float(b.get('free', '0')) > 0}
        return {"ok": True, "balances": balances}
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)

def get_symbol_price(client: Client | None, symbol="BTCUSDT") -> float | None:
    if PAPER_TRADING:
        return 68000.0  # preço simulado
    try:
        t = client.get_symbol_ticker(symbol=symbol)
        return float(t["price"])
    except Exception:
        return None

def get_free_usdt(client: Client | None) -> float:
    if PAPER_TRADING:
        return 10000.0
    try:
        info = client.get_asset_balance(asset="USDT")
        return float(info["free"])
    except Exception:
        return 0.0

def place_market_order(client: Client | None, symbol="BTCUSDT", side="BUY", qty=0.001) -> dict:
    if PAPER_TRADING:
        return _paper_order(symbol, side, "MARKET", qty)
    try:
        order = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=qty)
        return _ok(order)
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)

def place_limit_order(client: Client | None, symbol="BTCUSDT", side="BUY", qty=0.001, price: float = 0.0) -> dict:
    if PAPER_TRADING:
        return _paper_order(symbol, side, "LIMIT", qty, price)
    try:
        order = client.create_order(
            symbol=symbol, side=side, type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC, quantity=qty, price=f"{price:.8f}"
        )
        return _ok(order)
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)

def place_stop_loss_limit(client: Client | None, symbol="BTCUSDT", side="SELL", qty=0.001, stop_price: float=0.0, limit_price: float=0.0) -> dict:
    if PAPER_TRADING:
        return _paper_order(symbol, side, "STOP_LOSS_LIMIT", qty, limit_price, {"stopPrice": stop_price})
    try:
        order = client.create_order(
            symbol=symbol, side=side, type=ORDER_TYPE_STOP_LOSS_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC, quantity=qty, price=f"{limit_price:.8f}", stopPrice=f"{stop_price:.8f}"
        )
        return _ok(order)
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)

def place_take_profit_limit(client: Client | None, symbol="BTCUSDT", side="SELL", qty=0.001, stop_price: float=0.0, limit_price: float=0.0) -> dict:
    if PAPER_TRADING:
        return _paper_order(symbol, side, "TAKE_PROFIT_LIMIT", qty, limit_price, {"stopPrice": stop_price})
    try:
        order = client.create_order(
            symbol=symbol, side=side, type=ORDER_TYPE_TAKE_PROFIT_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC, quantity=qty, price=f"{limit_price:.8f}", stopPrice=f"{stop_price:.8f}"
        )
        return _ok(order)
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)

def place_oco_order(client: Client | None, symbol="BTCUSDT", side="SELL", qty=0.001, price: float=0.0, stop_price: float=0.0, stop_limit_price: float=0.0) -> dict:
    if PAPER_TRADING:
        ext = {"price": price, "stopPrice": stop_price, "stopLimitPrice": stop_limit_price}
        return _paper_order(symbol, side, "OCO", qty, price, ext)
    try:
        order = client.create_oco_order(
            symbol=symbol, side=side, quantity=qty,
            price=f"{price:.8f}", stopPrice=f"{stop_price:.8f}", stopLimitPrice=f"{stop_limit_price:.8f}",
            stopLimitTimeInForce=TIME_IN_FORCE_GTC
        )
        return _ok(order)
    except (BinanceAPIException, BinanceRequestException) as e:
        return _err(e)
    except Exception as e:
        return _err(e)