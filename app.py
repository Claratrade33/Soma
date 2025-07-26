from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import ClarinhaIA
from binance.client import Client
import threading
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
threads_automaticas = {}

# === MODELO DE USUÁRIO ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    api_key = db.Column(db.String(300))
    api_secret = db.Column(db.String(300))

# === USUÁRIO ATUAL ===
def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None

# === ROTAS ===

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        return render_template("login.html", erro="Credenciais inválidas")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception:
            return render_template("register.html", erro="Erro ao registrar usuário.")
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configurar', methods=["GET", "POST"])
def configurar():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == "POST":
        user.api_key = request.form['api_key']
        user.api_secret = request.form['api_secret']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template("configurar.html", user=user)

@app.route('/painel_operacao')
def painel_operacao():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    saldo = "Chaves não configuradas"
    if user.api_key and user.api_secret:
        try:
            client = Client(user.api_key, user.api_secret)
            balance = client.get_asset_balance(asset='USDT')
            saldo = round(float(balance['free']), 2)
        except Exception:
            saldo = "Erro ao conectar"

    try:
        ia = ClarinhaIA(api_key=user.api_key, api_secret=user.api_secret)
        sugestao = ia.analisar()
    except Exception:
        sugestao = {"sinal": "Erro", "alvo": "-", "stop": "-", "confianca": 0}

    return render_template("painel_operacao.html", saldo=saldo, sugestao=sugestao)

@app.route('/sinal_ia')
def sinal_ia():
    user = get_current_user()
    if not user:
        return jsonify({"erro": "Não autenticado"}), 401
    try:
        ia = ClarinhaIA(api_key=user.api_key, api_secret=user.api_secret)
        sugestao = ia.analisar()
        return jsonify(sugestao)
    except Exception:
        return jsonify({"erro": "Erro ao analisar mercado"}), 500

@app.route('/executar_ordem', methods=["POST"])
def executar_ordem():
    user = get_current_user()
    if not user:
        return jsonify({"erro": "Não autenticado"}), 401
    dados = request.json
    try:
        client = Client(user.api_key, user.api_secret)
        lado = dados.get("lado")
        quantidade = dados.get("quantidade", 11)
        if lado == "compra":
            ordem = client.order_market_buy(symbol="BTCUSDT", quantity=quantidade)
        elif lado == "venda":
            ordem = client.order_market_sell(symbol="BTCUSDT", quantity=quantidade)
        else:
            return jsonify({"erro": "Lado inválido"}), 400
        return jsonify({"mensagem": "Ordem executada", "ordem": ordem})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/modo_automatico', methods=["POST"])
def modo_automatico():
    user = get_current_user()
    if not user:
        return jsonify({"erro": "Não autenticado"}), 401

    user_id = user.id
    if user_id in threads_automaticas:
        return jsonify({"mensagem": "Modo automático já está ativo"})

    def executar_loop():
        ia = ClarinhaIA(api_key=user.api_key, api_secret=user.api_secret)
        client = Client(user.api_key, user.api_secret)
        while True:
            try:
                sinal = ia.analisar()
                if sinal['sinal'] == 'BUY':
                    client.order_market_buy(symbol="BTCUSDT", quantity=11)
                elif sinal['sinal'] == 'SELL':
                    client.order_market_sell(symbol="BTCUSDT", quantity=11)
                time.sleep(40)  # Aguarda 40s entre análises
            except Exception as e:
                print("Erro no modo automático:", e)
                break

    thread = threading.Thread(target=executar_loop)
    thread.daemon = True
    thread.start()
    threads_automaticas[user_id] = thread
    return jsonify({"mensagem": "Modo automático ativado"})

# === CRIAÇÃO AUTOMÁTICA DE BANCO ===
with app.app_context():
    db.create_all()
