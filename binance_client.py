import os
from binance.client import Client

def get_client(username=None, api_key=None, api_secret=None, testnet=None):
    key = api_key or os.getenv("BINANCE_API_KEY")
    secret = api_secret or os.getenv("BINANCE_API_SECRET")
    if testnet is None:
        testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
    if not key or not secret:
        raise RuntimeError("BINANCE_API_KEY/SECRET não configurados no Environment.")
    return Client(key, secret, testnet=testnet)