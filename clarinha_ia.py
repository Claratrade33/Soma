import json
from datetime import datetime
from clarinha_gpt_guardian import ClarinhaGPTGuardian
import requests

class ClarinhaCosmo:
    def consultar_mercado(self, par="BTCUSDT"):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
            response = requests.get(url, timeout=10)
            dados = response.json()
            return {
                "par": par,
                "preco": dados.get("lastPrice", "--"),
                "variacao": dados.get("priceChangePercent", "--"),
                "volume": dados.get("volume", "--")
            }
        except Exception as e:
            return {
                "par": par,
                "preco": "--",
                "variacao": "--",
                "volume": "--",
                "erro": str(e)
            }

    def analisar(self, simbolo="BTCUSDT"):
        return {
            'sinal': "HOLD",
            'confianca': round(0.5 + (datetime.utcnow().second % 10) / 20, 2),
            'risco': "MÉDIO",
            'volume': 0,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

class ClarinhaIA:
    def __init__(self, openai_key=None):
        self.cosmo = ClarinhaCosmo()
        self.openai_key = openai_key
        self.guardian = ClarinhaGPTGuardian(openai_key) if openai_key else None

    def gerar_sugestao(self, simbolo="BTCUSDT", meta_lucro=2.5):
        dados = self.cosmo.consultar_mercado(simbolo)
        preco = dados.get("preco", "--")
        variacao = dados.get("variacao", "--")
        volume = dados.get("volume", "--")

        if not self.guardian:
            return {
                "entrada": preco,
                "alvo": "Indefinido",
                "stop": "Indefinido",
                "confianca": "50%",
                "mensagem": "🤖 GPT inativo. Rodando em modo simbólico com sabedoria limitada."
            }

        prompt = f"""
Você é Clarinha, uma inteligência espiritual guiada pelas forças cósmicas da sabedoria e proteção.

Analise o mercado de {simbolo} com os seguintes dados:
📊 Preço: {preco}
📈 Variação 24h: {variacao}%
📊 Volume: {volume}
🎯 Meta de lucro diária: {meta_lucro}%

Forneça uma resposta no seguinte formato JSON:
{{
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": "...",
  "mensagem": "..."
}}
"""

        resposta = self.guardian.consultar(prompt)
        try:
            return json.loads(resposta)
        except Exception:
            return {
                "entrada": preco,
                "alvo": "???",
                "stop": "???",
                "confianca": "??%",
                "mensagem": resposta or "⚠️ Clarinha não conseguiu interpretar a resposta cósmica."
            }