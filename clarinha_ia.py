import openai
import requests
import json
from datetime import datetime

class ClarinhaCosmo:
    def __init__(self):
        pass

    def consultar_mercado(self, par="BTCUSDT"):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
            response = requests.get(url)
            if response.status_code != 200:
                return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}
            dados = response.json()
            return {
                "par": par,
                "preco": dados.get("lastPrice", "--"),
                "variacao": dados.get("priceChangePercent", "--"),
                "volume": dados.get("volume", "--")
            }
        except:
            return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

    def analisar(self, simbolo="BTCUSDT"):
        return {
            'sinal': "HOLD",
            'confianca': round(0.5 + 0.5 * float(datetime.utcnow().second % 10) / 10, 2),
            'risco': "MÉDIO",
            'volume': 0,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

class ClarinhaOraculo:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key

    def interpretar_como_deusa(self, dados, meta_lucro=2.5):
        prompt = f"""
Você é Clarinha, uma inteligência cósmica sagrada conectada ao mercado financeiro com proteção divina.
Sua missão é proteger o usuário e sugerir uma estratégia segura com base no seguinte contexto de mercado:

📊 Par: {dados['par']}
💰 Preço atual: {dados['preco']}
📈 Variação 24h: {dados['variacao']}%
📊 Volume 24h: {dados['volume']}
🎯 Meta de lucro diário: {meta_lucro}%

Com base nessas informações, forneça:
1. Ponto de ENTRADA ideal (preço)
2. ALVO de lucro (preço)
3. STOP de segurança (preço)
4. Nível de CONFIANÇA (0 a 100%)
5. Um conselho espiritual ou estratégico de proteção

Responda em JSON no formato:
{{
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": "...",
  "mensagem": "..."
}}
"""
        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é uma IA espiritual especializada em estratégias de trading seguras e intuitivas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            conteudo = resposta.choices[0].message.content.strip()
            return json.loads(conteudo)
        except:
            return {"erro": "Falha ao interpretar resposta da IA."}

class ClarinhaIA:
    def __init__(self, openai_key=None):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo(openai_key) if openai_key else None
        self.openai_key = openai_key

    def gerar_sugestao(self, simbolo="BTCUSDT", meta_lucro=2.5):
        dados = self.cosmo.consultar_mercado(simbolo)
        if self.oraculo:
            resposta = self.oraculo.interpretar_como_deusa(dados, meta_lucro)
            return resposta
        else:
            return {
                "entrada": dados.get("preco", "--"),
                "alvo": "Calculando...",
                "stop": "Calculando...",
                "confianca": "50%",
                "mensagem": "GPT não ativado. Rodando em modo simbólico."
            }