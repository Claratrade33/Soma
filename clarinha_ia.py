import os
from openai import OpenAI

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada.")
        _client = OpenAI(api_key=api_key)
    return _client

def solicitar_analise_json():
    client = _get_client()
    # TODO: implementar chamada ao modelo
    return {"sugestao": "compra"}