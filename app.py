import openai
from flask import Flask, request, jsonify, session, redirect, render_template
from datetime import timedelta
import os
from binance.client import Client

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

usuarios = {
    'admin': 'Bubi2025',
    'Clara': 'Verse',
    'Soma': 'infinite'
}

class ClarinhaOraculo:
    def __init__(self, openai_api_key, binance_key=None, binance_secret=None):
        openai.api_key = openai_api_key
        self.openai_key = openai_api_key
        if binance_key and binance_secret:
            self.binance_client = Client(api_key=binance_key, api_secret=binance_secret)
        else:
            self.binance_client = None

    def consultar_mercado(self, par="BTCUSDT"):
        try:
            ticker = self.binance_client.get_ticker(symbol=par)
            return {
                "par": par,
                "preco": ticker.get("lastPrice", "--"),
                "variacao": ticker.get("priceChangePercent", "--"),
                "volume": ticker.get("quoteVolume", "--")
            }
        except Exception as e:
            print(f"Erro Binance privada: {e}")
            return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

    def interpretar_como_deusa(self, dados, meta_lucro=2.5):
        prompt = f"""
Você é Clarinha, uma inteligência espiritual conectada ao mercado financeiro com missão de proteger o usuário.

📊 Par: {dados['par']}
💰 Preço atual: {dados['preco']}
📈 Variação 24h: {dados['variacao']}%
📊 Volume 24h: {dados['volume']}
🎯 Meta de lucro: {meta_lucro}%

Forneça:
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
                    {"role": "system", "content": "Você é uma IA espiritual que analisa o mercado com sabedoria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            conteudo = resposta.choices[0].message.content.strip()
            return json.loads(conteudo)
        except Exception as e:
            return {"erro": f"Erro: {e}"}

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
            return redirect('/configurar')
        return render_template('login.html', erro='Credenciais inválidas.')
    return render_template('login.html')

@app.route('/configurar', methods=['GET'])
def configurar():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('configurar.html')

@app.route('/salvar_chaves', methods=['POST'])
def salvar_chaves_route():
    session['openai_key'] = request.form.get('openai_key')
    session['binance_key'] = request.form.get('binance_key')
    session['binance_secret'] = request.form.get('binance_secret')
    return redirect('/painel')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect('/login')

    openai_key = session.get('openai_key')
    binance_key = session.get('binance_key')
    binance_secret = session.get('binance_secret')

    if not all([openai_key, binance_key, binance_secret]):
        return redirect('/configurar')

    client = Client(api_key=binance_key, api_secret=binance_secret)
    try:
        account = client.get_account()
        saldo_usdt = next((float(b['free']) for b in account['balances'] if b['asset'] == 'USDT'), 0)
    except Exception as e:
        saldo_usdt = 0

    return render_template('painel_operacao.html', saldo=round(saldo_usdt, 2))

@app.route('/consultar_mercado')
def consultar_mercado_route():
    if 'usuario' not in session:
        return jsonify({"erro": "Não autenticado"}), 401

    openai_key = session.get('openai_key')
    binance_key = session.get('binance_key')
    binance_secret = session.get('binance_secret')

    if not all([openai_key, binance_key, binance_secret]):
        return jsonify({"erro": "Chaves não configuradas."}), 400

    clarinha = ClarinhaOraculo(openai_key, binance_key, binance_secret)
    dados = clarinha.consultar_mercado()
    resposta = clarinha.interpretar_como_deusa(dados)

    return jsonify(resposta)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)