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

# === Configurações iniciais ===
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret_key_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# === Modelos de dados ===
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

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'saldo_simulado': self.saldo_simulado,
            'profit_loss': self.profit_loss,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate
        }


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

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'profit_loss': self.profit_loss,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'strategy_used': self.strategy_used
        }


# === IA Clarinha (sem sklearn) ===
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


# === Simulação de Mercado ===
class MarketSystem:
    def __init__(self):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo()

    def get_crypto_data(self):
        return {
            'BTC': {'price': round(random.uniform(95000, 105000), 2)},
            'ETH': {'price': round(random.uniform(3000, 3800), 2)}
        }

    def get_brazilian_data(self):
        return {
            'IBOV': {'price': 134000 + random.randint(-1000, 1000)},
            'USD_BRL': {'price': round(5.5 + random.uniform(-0.2, 0.2), 2)}
        }


market_system = MarketSystem()

# === Decorador de login ===
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
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p):
            session['user_id'] = user.id
            session.permanent = True
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas!', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        e = request.form.get('email','').strip()
        p = request.form.get('password','').strip()
        if User.query.filter_by(username=u).first():
            flash('Usuário já existe!', 'error')
        else:
            user = User(username=u, email=e, password=generate_password_hash(p))
            db.session.add(user)
            db.session.commit()
            flash('Conta criada!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    crypto = market_system.get_crypto_data()
    brazil = market_system.get_brazilian_data()
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()
    return render_template('painel_operacao.html', user=user, crypto_data=crypto, br_data=brazil, trades=trades)


@app.route('/configurar', methods=['GET','POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key = request.form.get('binance_api_key','').strip()
        user.binance_api_secret = request.form.get('binance_api_secret','').strip()
        s = request.form.get('saldo_simulado')
        if s:
            user.saldo_simulado = float(s)
        db.session.commit()
        flash('Configurações salvas!', 'success')
    return render_template('configurar.html', user=user)


@app.route('/api/market_data')
@login_required
def api_market_data():
    return jsonify({
        'crypto': market_system.get_crypto_data(),
        'brazilian': market_system.get_brazilian_data(),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/intelligent_analysis', methods=['POST'])
@login_required
def api_intelligent_analysis():
    data = request.get_json() or {}
    symbol = data.get('symbol','BTC')
    cosmic = market_system.cosmo.analyze(symbol)
    oracle = market_system.oraculo.predict(symbol)
    return jsonify({
        'cosmic': cosmic,
        'oracle': oracle,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/execute_trade', methods=['POST'])
@login_required
def api_execute_trade():
    data = request.get_json() or {}
    user = User.query.get(session['user_id'])
    sym = data.get('symbol')
    side = data.get('side')
    qty = float(data.get('quantity', 0))

    price = market_system.get_crypto_data().get(sym, {}).get('price', 100)
    trade_value = qty * price

    if side == 'BUY':
        if user.saldo_simulado < trade_value:
            return jsonify({'success': False, 'error': 'Saldo insuficiente'}), 400
        user.saldo_simulado -= trade_value
    else:
        user.saldo_simulado += trade_value

    pnl = random.uniform(-trade_value*0.03, trade_value*0.05)
    user.profit_loss += pnl
    user.total_trades += 1
    win_count = Trade.query.filter(Trade.user_id==user.id, Trade.profit_loss>0).count()
    user.win_rate = (win_count / user.total_trades)*100 if user.total_trades else 0

    trade = Trade(user_id=user.id, symbol=sym, side=side, quantity=qty, entry_price=price, profit_loss=pnl)
    db.session.add(trade)
    db.session.commit()

    return jsonify({'success': True, 'pnl': pnl, 'price': price})


# === WebSocket ===
@socketio.on('connect')
def ws_connect():
    emit('connected', {'status': 'success'})


@socketio.on('subscribe_market')
def ws_subscribe_market():
    emit('market_update', {
        'crypto': market_system.get_crypto_data(),
        'brazilian': market_system.get_brazilian_data(),
        'timestamp': datetime.utcnow().isoformat()
    })


# === Inicializar DB e rodar ===
def initialize_database():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin', email='admin@clara.com', password=generate_password_hash('admin123'))
            db.session.add(u)
            db.session.commit()

if __name__ == '__main__':
    initialize_database()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)