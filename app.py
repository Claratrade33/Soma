import openai
import requests
import json
from flask import Flask, request, jsonify, session, redirect, render_template
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

class ClarinhaOraculo:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key

    def consultar_mercado(self, par="BTCUSDT"):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Erro na resposta da API: {response.status_code}")
                return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

            dados = response.json()
            return {
                "par": par,
                "preco": dados.get("lastPrice", "--"),
                "variacao": dados.get("priceChangePercent", "--"),
                "volume": dados.get("volume", "--")
            }
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API da Binance: {e}")
            return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

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
            try:
                resposta_json = json.loads(conteudo)
                return resposta_json
            except json.JSONDecodeError:
                return {"erro": "Falha ao decodificar a resposta JSON."}
        except Exception as e:
            return {"erro": f"Erro ao consultar Clarinha: {e}"}

@app.route('/consultar_mercado', methods=['GET'])
def consultar_mercado():
    openai_key = session.get('openai_key')
    if not openai_key:
        return jsonify({"erro": "Chave da API não configurada."}), 400

    clarinha = ClarinhaOraculo(openai_key)
    dados_mercado = clarinha.consultar_mercado()
    resposta = clarinha.interpretar_como_deusa(dados_mercado)

    return jsonify(resposta)

@app.route('/salvar_chaves', methods=['POST'])
def salvar_chaves_route():
    # Aqui você deve implementar a lógica para salvar as chaves da API
    pass

@app.route('/configurar')
def configurar():
    return render_template('configurar_chaves.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)