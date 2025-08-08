from binance.client import Client
from models import Usuario, BinanceKey
from crypto_utils import descriptografar


def get_client(usuario_nome: str) -> Client:
    """Retorna um cliente da Binance para o usuário dado."""
    usuario = Usuario.query.filter_by(usuario=usuario_nome).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")

    cred = BinanceKey.query.filter_by(user_id=usuario.id).first()
    if not cred:
        raise ValueError("Chaves da Binance não configuradas")

    api_key = descriptografar(cred.api_key, usuario.usuario)
    api_secret = descriptografar(cred.api_secret, usuario.usuario)
    client = Client(api_key, api_secret, testnet=cred.testnet)
    if cred.testnet:
        client.API_URL = 'https://testnet.binance.vision/api'
    return client
