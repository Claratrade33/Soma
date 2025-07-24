import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA
from galactic_bot import iniciar_galactic_bot

# === CONFIG ===
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)

# === MODELOS ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    api_secret = db.Column(db.String(255), nullable=False)
    openai_key = db.Column(db.String(255), nullable=True)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    symbol = db.Column(db.String(20))
    side = db.Column(db.String(10))
    entry_price = db.Column(db.String(50))
    exit_price = db.Column(db.String(50), nullable=True)
    profit_loss = db.Column(db.String(50), nullable=True)
    strategy_used = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# === FUNÇÕES ===
def get_binance_client(user_id):
    config = Configuracao.query.filter_by(user_id=user_id).first()
    if config:
        return Client(config.api_key, config.api_secret)
    return None

def get_openai_key(user_id):
    config = Configuracao.query.filter_by(user_id=user_id).first()
    return config.openai_key if config else None

# === ROTAS ===
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'error')
            return redirect(url_for('register'))

        senha_hash = generate_password_hash(senha)
        novo_user = User(username=username, email=email, password=senha_hash)
        db.session.add(novo_user)
        db.session.commit()

        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, senha):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('painel_operacao'))
        else:
            flash('Credenciais inválidas.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configurar', methods=['GET', 'POST'])
def configurar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        api_key = request.form['api_key']
        api_secret = request.form['api_secret']
        openai_key = request.form['openai_key']
        user_id = session['user_id']

        config = Configuracao.query.filter_by(user_id=user_id).first()
        if config:
            config.api_key = api_key
            config.api_secret = api_secret
            config.openai_key = openai_key
        else:
            config = Configuracao(user_id=user_id, api_key=api_key, api_secret=api_secret, openai_key=openai_key)
            db.session.add(config)

        db.session.commit()
        return redirect(url_for('painel_operacao'))

    return render_template('configurar.html')

@app.route('/painel_operacao')
def painel_operacao():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    client = get_binance_client(user_id)

    if not client:
        return redirect(url_for('configurar'))

    try:
        saldo_usdt = client.get_asset_balance(asset='USDT')['free']
    except:
        saldo_usdt = "0.00"

    trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.desc()).limit(10).all()
    crypto_data = {
        "BTCUSDT": {"price": "0", "change_24h": 0, "volume_24h": 0, "rsi": 50},
        "ETHUSDT": {"price": "0", "change_24h": 0, "volume_24h": 0, "rsi": 50},
    }

    return render_template('painel_operacao.html', saldo_usdt=saldo_usdt, trades=trades, crypto_data=crypto_data)

@app.route('/executar_ordem', methods=['POST'])
def trade():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    symbol = request.form['symbol']
    side = request.form['side']
    quantity = float(request.form['quantity'])
    user_id = session['user_id']
    client = get_binance_client(user_id)

    if not client:
        flash("Configuração inválida", "error")
        return redirect(url_for('configurar'))

    try:
        ordem = client.create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        preco_executado = ordem['fills'][0]['price']

        novo_trade = Trade(
            user_id=user_id,
            symbol=symbol,
            side=side,
            entry_price=preco_executado,
            strategy_used='Manual'
        )
        db.session.add(novo_trade)
        db.session.commit()

        flash("Ordem executada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro: {str(e)}", "error")

    return redirect(url_for('painel_operacao'))

@app.route('/sugestao_ia')
def sugestao_ia():
    if 'user_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'})

    openai_key = get_openai_key(session['user_id'])
    clarinha = ClarinhaIA(openai_key=openai_key)
    resposta = clarinha.gerar_sugestao(simbolo="BTCUSDT")
    return jsonify(resposta)

# === INICIAR PROTEÇÃO GALÁCTICA ===
iniciar_galactic_bot()

# === EXECUÇÃO PRINCIPAL ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)