import os, time, requests  # <- adicionamos requests
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

# NOVO: permite preço ao vivo mesmo no paper
PAPER_PRICE_LIVE = os.getenv("PAPER_PRICE_LIVE", "true").lower() == "true"

def make_client(api_key: str, api_secret: str) -> Client | None:
    if PAPER_TRADING:
        return None  # paper: não instanciamos client real para ordens
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
    # NOVO: se estiver em paper, mas quiser preço real, busca na API pública
    if PAPER_TRADING and PAPER_PRICE_LIVE:
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price", params={"symbol": symbol}, timeout=5)
            r.raise_for_status()
            return float(r.json()["price"])
        except Exception:
            return 68000.0  # fallback
    if PAPER_TRADING:
        return 68000.0  # preço simulado (se PAPER_PRICE_LIVE=false)
    try:
        t = client.get_symbol_ticker(symbol=symbol)
       