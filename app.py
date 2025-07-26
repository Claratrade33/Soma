import os
import time
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_claraverse_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    api_key_binance = db.Column(db.String(200))
    api_secret_binance = db.Column(db.String(200))
    openai_key = db.Column(db.String(200))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, senha):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        return render_template('login.html', erro='Credenciais inválidas')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if User.query.filter_by(email=email).first():
            return render_template('register.html', erro='Email já cadastrado')
        hash_senha = generate_password_hash(senha)
        user = User(email=email, password=hash_senha)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/painel_operacao')
def painel_operacao():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    saldo = 0.0
    try:
        if user.api_key_binance and user.api_secret_binance:
            cliente = Client(user.api_key_binance, user.api_secret_binance)
            conta = cliente.get_asset_balance(asset='USDT')
            saldo = round(float(conta['free']), 2)
    except Exception as e:
        print("Erro ao obter saldo:", e)
    return render_template("painel_operacao.html", saldo=saldo)

@app.route('/configurar', methods=["GET", "POST"])
def configurar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.api_key_binance = request.form['api_key']
        user.api_secret_binance = request.form['api_secret']
        user.openai_key = request.form['openai_key']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/executar_ordem', methods=["POST"])
def executar_ordem():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'})
    user = User.query.get(session['user_id'])
    tipo = request.json.get("tipo")
    try:
        cliente = Client(user.api_key_binance, user.api_secret_binance)
        if tipo == "entrada":
            cliente.order_market_buy(symbol="BTCUSDT", quantity=0.001)
            return jsonify({"status": "Compra executada"})
        elif tipo == "stop":
            cliente.order_market_sell(symbol="BTCUSDT", quantity=0.001)
            return jsonify({"status": "Stop executado"})
        elif tipo == "alvo":
            cliente.order_market_sell(symbol="BTCUSDT", quantity=0.001)
            return jsonify({"status": "Alvo executado"})
        elif tipo == "automatico":
            ia = ClarinhaIA(user.api_key_binance, user.api_secret_binance, user.openai_key)
            from threading import Thread
            Thread(target=loop_automatico, args=(ia, cliente), daemon=True).start()
            return jsonify({"status": "Modo automático ativado"})
        else:
            return jsonify({"erro": "Tipo inválido"})
    except Exception as e:
        return jsonify({"erro": str(e)})

@app.route('/sugestao_ia')
def sugestao_ia():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'})
    user = User.query.get(session['user_id'])
    ia = ClarinhaIA(user.api_key_binance, user.api_secret_binance, user.openai_key)
    resultado = ia.analise()
    return jsonify(resultado)

def loop_automatico(ia, cliente):
    while True:
        try:
            sinal = ia.analise()
            print("IA:", sinal)
            if sinal.get("direcao") == "COMPRA":
                cliente.order_market_buy(symbol="BTCUSDT", quantity=0.001)
            elif sinal.get("direcao") == "VENDA":
                cliente.order_market_sell(symbol="BTCUSDT", quantity=0.001)
            with open("log_operacoes.txt", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {sinal}\n")
        except Exception as e:
            print("Erro loop automático:", e)
        time.sleep(60)
