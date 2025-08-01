from openai import OpenAI
import requests
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def obter_dados_mercado(simbolo="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={simbolo}"
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
            "rsi": rsi
        }
    except Exception as e:
        return {"erro": f"Falha ao obter dados: {e}"}

def solicitar_analise_json(simbolo="BTCUSDT"):
    dados = obter_dados_mercado(simbolo)
    if "erro" in dados:
        return {
            "entrada": "-",
            "alvo": "-",
            "stop": "-",
            "confianca": 0,
            "sugestao": dados["erro"]
        }

    prompt = f"""
Você é a IA Clarinha, especialista espiritual em criptoativos. Analise o seguinte contexto de mercado e retorne um sinal de oper
ação em JSON.

DADOS:
- Preço Atual: {dados['preco_atual']}
- Variação 24h: {dados['variacao_24h']}%
- Volume: {dados['volume']}
- RSI: {dados['rsi']}

Responda exclusivamente em JSON estruturado:
{{
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": "...",
  "sugestao": "..."
}}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )
        conteudo = resp.choices[0].message.content.strip()
        return json.loads(conteudo)
    except Exception as e:
        return {
            "entrada": "-",
            "alvo": "-",
            "stop": "-",
            "confianca": 0,
            "sugestao": f"Erro GPT: {e}"
        }
