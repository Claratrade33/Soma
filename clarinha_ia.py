# clarinha_ia.py

import openai
import requests
import json

class ClarinhaIA:
    def __init__(self, openai_key):
        self.openai_key = openai_key
        openai.api_key = openai_key

    def gerar_sugestao(self):
        try:
            dados = self.obter_dados_mercado()
            prompt = f"""
Você é a IA Clarinha, especialista espiritual em criptoativos. Analise o seguinte contexto de mercado e retorne um sinal de operação.

DADOS:
- Preço Atual: {dados['preco_atual']}
- Variação 24h: {dados['variacao_24h']}%
- Volume: {dados['volume']}
- RSI: {dados['rsi']}

Responda exclusivamente em formato JSON:
{{
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": "...",
  "sugestao": "..."
}}
"""
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=200,
            )
            conteudo = resposta.choices[0].message.content.strip()
            return json.loads(conteudo)
        except Exception as e:
            return {"entrada": "-", "alvo": "-", "stop": "-", "confianca": 0, "sugestao": f"Erro: {str(e)}"}

    def obter_dados_mercado(self):
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
            resposta = requests.get(url)
            resposta.raise_for_status()
            dados = resposta.json()

            preco = float(dados["lastPrice"])
            variacao = float(dados["priceChangePercent"])
            volume = float(dados["volume"])

            rsi = 50 + (variacao * 0.5)
            rsi = min(max(rsi, 0), 100)

            return {
                "preco_atual": preco,
                "variacao_24h": variacao,
                "volume": volume,
                "rsi": rsi,
            }
        except requests.RequestException as e:
            raise Exception(f"Erro ao obter dados da Binance: {str(e)}")
