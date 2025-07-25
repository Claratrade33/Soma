# clarinha_ia.py

import openai
from binance.client import Client
import statistics
import numpy as np
import os

class ClarinhaIA:
    def __init__(self, api_key=None, api_secret=None, openai_key=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.openai_key = openai_key
        self.symbolo = "BTCUSDT"

    def pegar_dados_binance(self):
        try:
            client = Client(self.api_key, self.api_secret)
            klines = client.get_klines(symbol=self.symbolo, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100)
            closes = [float(k[4]) for k in klines]
            volumes = [float(k[5]) for k in klines]
            rsi = self.calcular_rsi(closes)
            suporte = min(closes[-20:])
            resistencia = max(closes[-20:])
            preco_atual = closes[-1]
            variacao = closes[-1] - closes[-2]
            return {
                "preco": preco_atual,
                "rsi": round(rsi, 2),
                "suporte": round(suporte, 2),
                "resistencia": round(resistencia, 2),
                "variacao": round(variacao, 2),
                "volume": round(statistics.mean(volumes[-5:]), 2)
            }
        except Exception as e:
            return {"erro": str(e)}

    def calcular_rsi(self, precos, periodo=14):
        ganhos, perdas = [], []
        for i in range(1, periodo + 1):
            delta = precos[i] - precos[i - 1]
            if delta >= 0:
                ganhos.append(delta)
                perdas.append(0)
            else:
                ganhos.append(0)
                perdas.append(-delta)
        media_ganho = sum(ganhos) / periodo
        media_perda = sum(perdas) / periodo
        if media_perda == 0:
            return 100
        rs = media_ganho / media_perda
        return 100 - (100 / (1 + rs))

    def analise(self):
        dados = self.pegar_dados_binance()
        if "erro" in dados:
            return {"erro": "Erro ao obter dados da Binance"}

        prompt = (
            f"Você é uma IA de trading chamada Clarinha. Com base nos seguintes dados reais de mercado:\n"
            f"Preço atual: {dados['preco']}\n"
            f"RSI: {dados['rsi']}\n"
            f"Suporte: {dados['suporte']}\n"
            f"Resistência: {dados['resistencia']}\n"
            f"Variação: {dados['variacao']}\n"
            f"Volume: {dados['volume']}\n"
            f"Dê uma sugestão clara de entrada, alvo, stop e direção. Formato JSON puro com campos: "
            f"'simbolo', 'entrada', 'alvo', 'stop', 'direcao', 'confianca', 'mensagem'."
        )

        openai.api_key = self.openai_key
        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            texto = resposta.choices[0].message['content']
            return eval(texto)  # Espera JSON válido retornado pela IA
        except Exception as e:
            return {"erro": "Erro na IA Clarinha", "detalhe": str(e)}

