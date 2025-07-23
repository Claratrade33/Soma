import os
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client

# === Inicialização ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_real_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# === Modelos ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200))
    binance_api_secret = db.Column(db.String(200))
    saldo_simulado = db.Column(db.Float, default=10000.0)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symbol = db.Column(db.String(10))
    side = db.Column(db.String(10))
    quantity = db.Column(db.Float)
    entry_price = db.Column(db.Float)
    exit_price = db.Column(db.Float, nullable=True)
    profit_loss = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# === IA ===
class ClarinhaCosmo:
    def analyze(self, symbol):
        return {
            'cosmic_signal': random.choice(['BUY', 'SELL']),
            'confidence': round(random.uniform(0.6, 0.95), 2),
            'risk': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'volume': random.randint(500000, 3000000)
        }

class ClarinhaOraculo:
    def predict(self, symbol):
        return {
            'prediction': random.choice(['BUY', 'SELL', 'HOLD']),
            'sentiment': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL']),
            'score': round(random.uniform(-1, 1), 2)
        }

cosmo = ClarinhaCosmo()
oraculo = ClarinhaOraculo()

# === Autenticação ===
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# === Rotas ===
@app.route('/')
def index():
    return redirect(url_for('painel_operacao')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
        else:
            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key = request.form['binance_api_key'].strip()
        user.binance_api_secret = request.form['binance_api_secret'].strip()
        db.session.commit()
        flash("🔐 Configurações salvas com sucesso!", "success")
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/painel_operacao', methods=['GET'])
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    client = Client(user.binance_api_key, user.binance_api_secret)
    saldo_binance = client.get_asset_balance(asset='USDT')
    saldo_real = saldo_binance['free'] if saldo_binance else '0.00'

    analise = cosmo.analyze('BTCUSDT')
    previsao = oraculo.predict('BTCUSDT')
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()

    return render_template('painel_operacao.html',
        user=user, saldo_binance=saldo_real,
        analise=analise, previsao=previsao, trades=trades)

@app.route('/executar_operacao', methods=['POST'])
@login_required
def executar_operacao():
    user = User.query.get(session['user_id'])
    lado = request.form['lado']
    quantidade = float(request.form['quantidade'])
    client = Client(user.binance_api_key, user.binance_api_secret)

    symbol = 'BTCUSDT'
    price_info = client.get_symbol_ticker(symbol=symbol)
    preco = float(price_info['price'])

    ordem = client.create_order(
        symbol=symbol,
        side=lado,
        type='MARKET',
        quoteOrderQty=quantidade
    )

    trade = Trade(
        user_id=user.id,
        symbol=symbol,
        side=lado,
        quantity=quantidade / preco,
        entry_price=preco
    )
    db.session.add(trade)
    db.session.commit()

    flash("✅ Ordem executada com sucesso!", "success")
    return redirect(url_for('painel_operacao'))

# === API WS (futuro uso) ===
@app.route('/api/market_data')
@login_required
def api_market_data():
    return jsonify({
        'btc': random.uniform(25000, 35000),
        'usdbrl': random.uniform(4.5, 5.5),
        'rsi': random.randint(30, 70)
    })

# === DB Init ===
with app.app_context():
    db.create_all()

# === Run ===
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)