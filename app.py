import os
import logging
import warnings
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
import random

# === CONFIG
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_real_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# === MODELOS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(255))
    binance_api_secret = db.Column(db.String(255))
    saldo_simulado = db.Column(db.Float, default=10000.0)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symbol = db.Column(db.String(20))
    side = db.Column(db.String(10))
    quantity = db.Column(db.Float)
    entry_price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# === IA CLARINHA
class ClarinhaCosmo:
    def analyze(self, symbol):
        return {
            'cosmic_signal': random.choice(['BUY', 'SELL']),
            'confidence': round(random.uniform(0.5, 0.95), 2)
        }

class ClarinhaOraculo:
    def predict(self, symbol):
        return {
            'prediction': random.choice(['BUY', 'SELL']),
            'score': round(random.uniform(-1, 1), 2)
        }

clarinha_cosmo = ClarinhaCosmo()
clarinha_oraculo = ClarinhaOraculo()

# === LOGIN REQUIRED
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# === ROTAS
@app.route('/')
def index():
    return redirect(url_for('painel_operacao')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
        else:
            user = User(
                username=request.form['username'],
                email=email,
                password=generate_password_hash(request.form['password'])
            )
            db.session.add(user)
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
        user.binance_api_key = request.form.get('binance_api_key')
        user.binance_api_secret = request.form.get('binance_api_secret')
        db.session.commit()
        flash('Configurações salvas!', 'success')
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    saldo = 0.0
    try:
        client = Client(user.binance_api_key, user.binance_api_secret)
        account_info = client.get_account()
        saldo = next(float(a['free']) for a in account_info['balances'] if a['asset'] == 'USDT')
    except Exception as e:
        flash('Erro ao conectar com Binance', 'error')
    analise = clarinha_oraculo.predict("BTCUSDT")
    cosmo = clarinha_cosmo.analyze("BTCUSDT")
    return render_template('painel_operacao.html', user=user, saldo=round(saldo, 2), oraculo=analise, cosmo=cosmo)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    lado = request.form['lado']
    quantidade = float(request.form['quantidade'])
    try:
        client = Client(user.binance_api_key, user.binance_api_secret)
        order = client.create_order(
            symbol='BTCUSDT',
            side=lado,
            type='MARKET',
            quantity=quantidade
        )
        flash(f'Ordem de {lado} executada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro na ordem: {str(e)}', 'error')
    return redirect(url_for('painel_operacao'))

# === INICIALIZA
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)