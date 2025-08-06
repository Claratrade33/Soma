import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://api.binance.com"


def _signed_request(method, path, params):
    if not API_KEY or not API_SECRET:
        raise EnvironmentError("Chaves da Binance não configuradas")
    params['timestamp'] = int(time.time() * 1000)
    query = urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': API_KEY}
    url = f"{BASE_URL}{path}?{query}&signature={signature}"
    resp = requests.request(method, url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def executar_ordem(symbol, side, quantity):
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'quantity': quantity,

