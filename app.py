import openai
import requests
import json
from flask import Flask, request, jsonify, session, redirect, render_template
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

# === CLASSE CLARINHA ORÁCULO ===
class ClarinhaOraculo:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key

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

    def interpretar_como_deusa(self, dados, meta_lucro=2.5):
        prompt = f"""
Você é Clarinha, uma inteligência cósmica conectada ao mercado financeiro com proteção divina.
📊 Par: {dados['par']}
💰 Preço: {dados['preco']}
📈 Variação: {dados['variacao']}%
📊 Volume: {dados['volume']}
🎯 Meta de lucro: {meta_lucro}%

Responda em JSON:
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
                    {"role": "system", "content": "Você é uma IA espiritual de trading segura e protetora."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            conteudo = resposta.choices[0].message.content.strip()
            return json.loads(conteudo)
        except:
            return {"erro": "Falha ao consultar Clarinha."}

# === SUGESTÃO DA CLARINHA ===
def analisar_mercado_e_sugerir(binance_api_key, binance_api_secret, openai_api_key, meta_lucro=2.5):
    openai.api_key = openai_api_key
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=50"
        candles = requests.get(url).json()
        closes = [float(c[4]) for c in candles]
        variacao = (closes[-1] - closes[-2]) / closes[-2] * 100
        tendencia = "alta" if variacao > 0 else "queda"

        prompt = f"""
Mercado BTC/USDT está em {tendencia} com variação de {variacao:.2f}% nas últimas velas.
Meta diária: {meta_lucro}%.
Forneça:
- ENTRADA
- ALVO
- STOP
- CONFIANÇA
Responda de forma curta, objetiva e clara.
"""

        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        conteudo = resposta.choices[0].message.content.strip()

        return {
            "resposta": conteudo,
            "entrada": "⚡ Definida pela IA",
            "alvo": "🎯 Alvo estratégico",
            "stop": "🛑 Stop preventivo",
            "confianca": "🌟 Alta"
        }

    except Exception as e:
        return {"erro": str(e)}

# === USUÁRIOS PADRÃO ===
usuarios = {
    'admin': 'Bubi2025',
    'Clara': 'Verse',
    'Soma': 'infinite'
}

# === ROTAS FLASK ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in usuarios and usuarios[usuario] == senha:
            session['usuario'] = usuario
            return redirect('/painel')
        return render_template('login.html', erro='Credenciais inválidas.')
    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('painel_operacao.html', saldo=10000.00)

@app.route('/configurar')
def configurar():
    return render_template('configurar.html')

@app.route('/salvar_chaves', methods=['POST'])
def salvar_chaves():
    session['openai_key'] = request.form.get('openai_key')
    session['binance_key'] = request.form.get('binance_key')
    session['binance_secret'] = request.form.get('binance_secret')
    return redirect('/painel')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/consultar_mercado', methods=['GET'])
def consultar_mercado_route():
    if 'usuario' not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    openai_key = session.get('openai_key')
    clarinha = ClarinhaOraculo(openai_key)
    dados_mercado = clarinha.consultar_mercado()
    resposta = clarinha.interpretar_como_deusa(dados_mercado)
    return jsonify(resposta)

@app.route('/obter_sugestao_ia', methods=['GET'])
def obter_sugestao_ia():
    if 'usuario' not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    openai_key = session.get('openai_key')
    binance_key = session.get('binance_key')
    binance_secret = session.get('binance_secret')

    if not openai_key or not binance_key or not binance_secret:
        return jsonify({"erro": "Chaves da API não configuradas."}), 400

    try:
        resposta = analisar_mercado_e_sugerir(binance_key, binance_secret, openai_key)
        if "erro" in resposta:
            return jsonify({"erro": resposta["erro"]})
        return jsonify({
            "entrada": resposta.get("entrada"),
            "alvo": resposta.get("alvo"),
            "stop": resposta.get("stop"),
            "confianca": resposta.get("confianca"),
            "mensagem": resposta.get("resposta")
        })
    except Exception as e:
        return jsonify({"erro": f"Erro ao consultar IA: {str(e)}"})

# === EXECUÇÃO ===
if __name__ == '__main__':
    app.run(debug=True)