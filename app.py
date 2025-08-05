from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from binance.client import Client
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import json
import requests
import os

# Carregar variáveis de ambiente do .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

# Chaves reais (Render)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Clientes externos
client_binance = Client(BINANCE_API_KEY, BINANCE_SECRET)
client_openai = OpenAI(api_key=OPENAI_API_KEY)

# Histórico de ordens (temporário)
historico_ordens = []

@app.route("/")
def index():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return redirect(url_for("painel_operacao"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == "admin" and senha == "claraverse2025":
            session["logado"] = True
            return redirect(url_for("painel_operacao"))
        return render_template("login.html", error_msg="Credenciais inválidas.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/painel_operacao")
def painel_operacao():
    if not session.get("logado"):
        return redirect(url_for("login"))
    try:
        saldo_spot = client_binance.get_account()
        saldo_futures = client_binance.futures_account_balance()
        saldo_btc = next((a["free"] for a in saldo_spot["balances"] if a["asset"] == "BTC"), "0")
        saldo_usdt = next((a["free"] for a in saldo_spot["balances"] if a["asset"] == "USDT"), "0")
        saldo_futures_usdt = next((a["balance"] for a in saldo_futures if a["asset"] == "USDT"), "0")
    except Exception as e:
        return render_template("painel_operacao.html", error_msg=str(e), saldo_btc="0", saldo_usdt="0", saldo_futures_usdt="0")

    return render_template("painel_operacao.html",
                           saldo_btc=saldo_btc,
                           saldo_usdt=saldo_usdt,
                           saldo_futures_usdt=saldo_futures_usdt)

@app.route("/executar_ordem", methods=["POST"])
def executar_ordem():
    if not session.get("logado"):
        return "Não autorizado", 403
    tipo = request.form.get("tipo")
    quantidade = request.form.get("quantidade", "0.001")
    try:
        if tipo == "compra":
            ordem = client_binance.order_market_buy(symbol="BTCUSDT", quantity=quantidade)
        elif tipo == "venda":
            ordem = client_binance.order_market_sell(symbol="BTCUSDT", quantity=quantidade)
        else:
            return "Tipo de ordem inválido", 400

        historico_ordens.insert(0, {
            "tipo": tipo.title(),
            "ativo": "BTCUSDT",
            "valor": quantidade,
            "preco": ordem["fills"][0]["price"],
            "hora": datetime.now().strftime("%H:%M")
        })
        return "Ordem executada", 200
    except Exception as e:
        return str(e), 500

@app.route("/historico")
def historico():
    return jsonify(historico_ordens)

@app.route("/sugestao_ia")
def sugestao_ia():
    quantidade = request.args.get("quantidade", "0.001")
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        dados = requests.get(url).json()
        preco = float(dados["lastPrice"])
        variacao = float(dados["priceChangePercent"])
        volume = float(dados["volume"])
        rsi = min(max(50 + variacao * 0.5, 0), 100)

        prompt = f"""
Você é Clarinha, a IA espiritualista da ClaraVerse. Com base nos dados abaixo, diga se devemos comprar ou vender agora.

DADOS:
- Preço Atual: {preco}
- Variação 24h: {variacao}%
- Volume: {volume}
- RSI: {rsi}

Responda somente com JSON estruturado assim:
{{
  "tipo": "compra" ou "venda",
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": 0-100,
  "sugestao": "..."
}}
"""

        resposta = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )
        conteudo = resposta.choices[0].message.content.strip()
        analise = json.loads(conteudo)
        analise["status"] = "ok"
        return jsonify(analise)
    except Exception as e:
        return jsonify({"status": "erro", "erro": str(e)})

@app.route("/modo_automatico", methods=["POST"])
def modo_automatico():
    try:
        # Aqui você pode ativar um loop de execução automática se desejar
        return jsonify({"status": "ok", "mensagem": "Modo automático ativado."})
    except Exception as e:
        return jsonify({"status": "erro", "erro": str(e)})

if __name__ == "__main__":
    app.run(debug=True)