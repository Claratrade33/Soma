import os
import random
import logging
import warnings
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for, request,
    jsonify, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração de avisos e logging
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret_key_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# === MODELOS ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200), nullable=True)
    binance_api_secret = db.Column(db.String(200), nullable=True)
    saldo_simulado = db.Column(db.Float, default=10000.0)
    profit_loss = db.Column(db.Float, default=0.0)
    total_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=True)
    profit_loss = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='FILLED')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    strategy_used = db.Column(db.String(50), nullable=True)

# === IA FICTÍCIA ===
class ClarinhaCosmo:
    def analyze(self, symbol):
        return {
            'cosmic_signal': random.choice(['BUY', 'SELL', 'NEUTRAL']),
            'confidence': round(random.uniform(0.5, 0.9), 2),
            'risk': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'volume': random.randint(100000, 5000000)
        }

class ClarinhaOraculo:
    def predict(self, symbol):
        return {
            'prediction': random.choice(['BUY', 'SELL', 'HOLD']),
            'sentiment': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL']),
            'score': round(random.uniform(-1, 1), 2)
        }

class MarketSystem:
    def __init__(self):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo()

    def get_crypto_data(self):
        return {
            'BTCUSDT': {
                'price': round(random.uniform(25000, 35000), 2),
                'change_24h': round(random.uniform(-5, 5), 2),
                'volume_24h': round(random.uniform(1000000, 5000000), 2),
                'rsi': round(random.uniform(30, 70), 2)
            }
        }

    def get_brazilian_data(self):
        return {
            'USD/BRL': {
                'price': round(random.uniform(4.5, 5.5), 2),
                'change_24h': round(random.uniform(-2, 2), 2),
                'volume_24h': round(random.uniform(100000, 500000), 2),
                'rsi': round(random.uniform(30, 70), 2)
            }
        }

market_system = MarketSystem()

# === AUTENTICAÇÃO ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
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
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Cadastro realizado com sucesso. Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    crypto = market_system.get_crypto_data()
    brazil = market_system.get_brazilian_data()
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()
    return render_template('painel_operacao.html', user=user, crypto_data=crypto, br_data=brazil, trades=trades)

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key = request.form.get('binance_api_key', '').strip()
        user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
        s = request.form.get('saldo_simulado')
        if s:
            user.saldo_simulado = float(s)
        db.session.commit()
        flash('Configurações salvas!', 'success')
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

# === API DE DADOS ===
@app.route('/api/market_data')
@login_required
def api_market_data():
    return jsonify({
        'crypto': market_system.get_crypto_data(),
        'brazilian': market_system.get_brazilian_data(),
        'timestamp': datetime.utcnow().isoformat()
    })

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
