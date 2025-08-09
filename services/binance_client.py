import os
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
from binance.exceptions import BinanceAPIException, BinanceRequestException

BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
BINANCE_API_BASE = os.getenv("BINANCE_API_BASE", "").strip()

def make_client(api_key: str, api_secret: str) -> Client:
    client = Client(api_key, api_secret, tld='com', testnet=BINANCE_TESTNET)
    if BINANCE_API_BASE:
        client.API_URL = f"{BINANCE_API_BASE}/api"
        client.WSS_URL = "wss://stream.binance.com:9443/ws"
    return client

def test_account(client: Client) -> dict:
    try:
        info = client.get_account()
        balances = {b['asset']: float(b['free']) for b in info.get('balances', []) if float(b.get('free', '0')) > 0}
        return {"ok": True, "balances": balances}
    except (BinanceAPIException, BinanceRequestException) as e:
        return {"ok": False, "error": f"{getattr(e,'status_code', '')} {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_symbol_price(client: Client, symbol="BTCUSDT") -> float | None:
    try:
        t = client.get_symbol_ticker(symbol=symbol)
        return float(t["price"])
    except Exception:
        return None

def get_free_usdt(client: Client) -> float:
    try:
        info = client.get_asset_balance(asset="USDT")
        return float(info["free"])
    except Exception:
        return 0.0

def place_market_order(client: Client, symbol="BTCUSDT", side="BUY", qty=0.001) -> dict:
    try:
        order = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=qty)
        return {"ok": True, "order": order}
    except (BinanceAPIException, BinanceRequestException) as e:
        return {"ok": False, "error": f"{getattr(e,'status_code','')} {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def place_limit_order(client: Client, symbol="BTCUSDT", side="BUY", qty=0.001, price: float = 0.0) -> dict:
    try:
        order = client.create_order(
            symbol=symbol, side=side, type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC, quantity=qty, price=f"{price:.8f}"
        )
        return {"ok": True, "order": order}
    except (BinanceAPIException, BinanceRequestException) as e:
        return {"ok": False, "error": f"{getattr(e,'status_code','')} {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}