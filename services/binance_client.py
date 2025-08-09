import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
BINANCE_API_BASE = os.getenv("BINANCE_API_BASE", "").strip()  # opcional

def make_client(api_key: str, api_secret: str) -> Client:
    client = Client(api_key, api_secret, tld='com', testnet=BINANCE_TESTNET)
    # Se quiser forçar base_url (ex.: testnet binance.vision)
    if BINANCE_API_BASE:
        client.API_URL = f"{BINANCE_API_BASE}/api"
        client.WSS_URL = "wss://stream.binance.com:9443/ws"
    return client

def test_account(client: Client) -> dict:
    try:
        info = client.get_account()
        balances = {b['asset']: b['free'] for b in info.get('balances', []) if float(b.get('free', '0')) > 0}
        return {"ok": True, "balances": balances}
    except (BinanceAPIException, BinanceRequestException) as e:
        return {"ok": False, "error": f"{e.status_code if hasattr(e,'status_code') else ''} {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_symbol_price(client: Client, symbol="BTCUSDT") -> float | None:
    try:
        t = client.get_symbol_ticker(symbol=symbol)
        return float(t["price"])
    except Exception:
        return None

def place_market_order(client: Client, symbol="BTCUSDT", side="BUY", qty=0.001) -> dict:
    """
    Em TESTNET funciona normalmente. Em produção: cuidado com saldo e permissões.
    """
    try:
        order = client.create_order(symbol=symbol, side=side, type="MARKET", quantity=qty)
        return {"ok": True, "order": order}
    except (BinanceAPIException, BinanceRequestException) as e:
        return {"ok": False, "error": f"{e.status_code if hasattr(e,'status_code') else ''} {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}