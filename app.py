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
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Configuração inicial
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_real_key')
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === AUTENTICAÇÃO ===
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_client(user):
    if not user.binance_api_key or not user.binance_api_secret:
        return None
    return Client(user.binance_api_key, user.binance_api_secret)

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
            flash('Cadastro realizado com sucesso.', 'success')
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
    saldo_real = 0.0
    try:
        client = get_client(user)
        if client:
            info = client.get_asset_balance(asset='USDT')
            saldo_real = float(info['free'])
    except Exception as e:
        flash('Erro ao acessar saldo na Binance: ' + str(e), 'error')

    return render_template('painel_operacao.html', user=user, saldo_real=saldo_real)

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key = request.form.get('binance_api_key', '').strip()
        user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
        db.session.commit()
        flash('Chaves salvas com sucesso!', 'success')
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    client = get_client(user)
    if not client:
        return jsonify({'error': 'API da Binance não configurada'})

    symbol = request.json.get('symbol', 'BTCUSDT')
    side = request.json.get('side', 'BUY')
    quantity = float(request.json.get('quantity', 0.001))

    try:
        ordem = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type='MARKET',
            quantity=quantity
        )
        return jsonify({'success': True, 'ordem': ordem})
    except BinanceAPIException as e:
        return jsonify({'error': str(e)})

# === BANCO DE DADOS ===
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)