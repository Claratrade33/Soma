import os
import random
import logging
import warnings
from datetime import datetime, timedelta
from functools import wraps

import numpy as np
from flask import (
    Flask, render_template, redirect, url_for, request,
    jsonify, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

# === CONFIGURAÇÃO DO APP ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret_key_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# === MODELOS ===
class User(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(150), nullable=False, unique=True)
    email               = db.Column(db.String(150), nullable=False, unique=True)
    password            = db.Column(db.String(200), nullable=False)
    binance_api_key     = db.Column(db.String(200), nullable=True)
    binance_api_secret  = db.Column(db.String(200), nullable=True)
    saldo_simulado      = db.Column(db.Float, default=10000.0)
    profit_loss         = db.Column(db.Float, default=0.0)
    total_trades        = db.Column(db.Integer, default=0)
    win_rate            = db.Column(db.Float, default=0.0)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

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
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol       = db.Column(db.String(20), nullable=False)
    side         = db.Column(db.String(10), nullable=False)
    quantity     = db.Column(db.Float, nullable=False)
    entry_price  = db.Column(db.Float, nullable=False)
    exit_price   = db.Column(db.Float, nullable=True)
    profit_loss  = db.Column(db.Float, nullable=True)
    status       = db.Column(db.String(20), default='FILLED')
    timestamp    = db.Column(db.DateTime, default=datetime.utcnow)
    strategy_used= db.Column(db.String(50), nullable=True)

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


# === IA AVANÇADA: ClarinhaCosmo ===
class ClarinhaCosmo:
    def __init__(self):
        self.ml_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False

    def analyze_cosmic_patterns(self, symbol):
        try:
            data = self._generate_market_data(symbol)
            hidden_patterns = self._detect_hidden_patterns(data)
            manipulation_score = self._detect_manipulation(data)
            ml_prediction = self._ml_prediction(data)
            cosmic_signal = self._calculate_cosmic_signal(data)

            return {
                'cosmic_signal': cosmic_signal,
                'hidden_patterns': hidden_patterns,
                'manipulation_detected': manipulation_score > 0.7,
                'ml_prediction': ml_prediction,
                'entry_confidence': random.uniform(0.6, 0.95),
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            app.logger.error(f"Erro ClarinhaCosmo: {e}")
            return self._fallback_analysis()

    def _generate_market_data(self, symbol):
        prices = [100 + random.uniform(-5, 5) for _ in range(100)]
        volumes = [random.uniform(1000, 10000) for _ in range(100)]
        return {'prices': prices, 'volumes': volumes}

    def _detect_hidden_patterns(self, data):
        return {
            'volume_divergence': random.choice([True, False]),
            'price_action_anomaly': random.choice([True, False]),
            'whale_accumulation': random.choice([True, False])
        }

    def _detect_manipulation(self, data):
        return random.uniform(0.1, 0.9)

    def _ml_prediction(self, data):
        directions = ['BUY', 'SELL', 'NEUTRAL']
        return {
            'direction': random.choice(directions),
            'confidence': random.uniform(0.5, 0.9)
        }

    def _calculate_cosmic_signal(self, data):
        signals = ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']
        return random.choice(signals)

    def _fallback_analysis(self):
        return {
            'cosmic_signal': 'NEUTRAL',
            'hidden_patterns': {
                'volume_divergence': False,
                'price_action_anomaly': False,
                'whale_accumulation': False
            },
            'manipulation_detected': False,
            'ml_prediction': {'direction': 'NEUTRAL', 'confidence': 0.5},
            'entry_confidence': 0.5,
            'risk_level': 'MEDIUM'
        }


# === PREVISÃO: ClarinhaOraculo ===
class ClarinhaOraculo:
    def get_oracle_prediction(self, symbol):
        try:
            sentiment = self._analyze_sentiment()
            onchain = self._analyze_onchain_data()
            temporal = self._temporal_prediction()
            final = self._combine_predictions(sentiment, onchain, temporal)
            return final
        except Exception as e:
            app.logger.error(f"Erro ClarinhaOraculo: {e}")
            return self._fallback_prediction()

    def _analyze_sentiment(self):
        fg = random.randint(0, 100)
        labels = ['EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'EXTREME_GREED']
        if fg < 20: label = labels[0]
        elif fg < 45: label = labels[1]
        elif fg < 55: label = labels[2]
        elif fg < 80: label = labels[3]
        else: label = labels[4]
        return {'score': fg/100, 'label': label, 'fear_greed_index': fg}

    def _analyze_onchain_data(self):
        return {
            'whale_activity': random.choice(['LOW','MEDIUM','HIGH']),
            'exchange_flows': random.choice(['INFLOW','OUTFLOW','NEUTRAL']),
            'holder_behavior': random.choice(['ACCUMULATING','DISTRIBUTING','HOLDING'])
        }

    def _temporal_prediction(self):
        return {
            'optimal_hours': [9,14,20],
            'current_time_score': random.uniform(0.3,1.0),
            'weekly_trend': random.choice(['BULLISH','BEARISH','NEUTRAL'])
        }

    def _combine_predictions(self, sent, onchain, temp):
        score = random.randint(-5,5)
        preds = ['STRONG_BUY','BUY','NEUTRAL','SELL','STRONG_SELL']
        if score >= 3: p='STRONG_BUY'
        elif score >= 1: p='BUY'
        elif score <= -3: p='STRONG_SELL'
        elif score <= -1: p='SELL'
        else: p='NEUTRAL'
        return {
            'prediction': p,
            'confidence': random.uniform(0.6,0.95),
            'score': score,
            'sentiment': sent,
            'onchain': onchain,
            'temporal': temp
        }

    def _fallback_prediction(self):
        return {
            'prediction':'NEUTRAL','confidence':0.5,'score':0,
            'sentiment':{'score':0.5,'label':'NEUTRAL','fear_greed_index':50},
            'onchain':{'whale_activity':'MEDIUM'},
            'temporal':{'weekly_trend':'NEUTRAL'}
        }


# === SISTEMA DE MERCADO SIMULADO ===
class MarketSystem:
    def __init__(self):
        self.cosmo    = ClarinhaCosmo()
        self.oraculo  = ClarinhaOraculo()

    def get_crypto_data(self):
        base = {'BTC':97500,'ETH':3400,'BNB':720,'ADA':1.25,'SOL':145,'XRP':0.85}
        out = {}
        for sym, price in base.items():
            var = random.uniform(-5,5)
            cp  = price*(1+var/100)
            out[sym] = {
                'price': round(cp,2),
                'change_24h': round(var,2),
                'volume_24h': random.randint(500000,2000000),
                'high_24h': round(cp*1.05,2),
                'low_24h': round(cp*0.95,2),
                'rsi': round(random.uniform(20,80),1)
            }
        return out

    def get_brazilian_data(self):
        return {
            'IBOV':  {'price':134167+random.randint(-1000,1000),'change_percent':round(random.uniform(-2,2),2)},
            'USD_BRL':{'price':5.55+random.uniform(-0.1,0.1),'change_percent':round(random.uniform(-1,1),2)}
        }

market_system = MarketSystem()


# === DECORADOR DE LOGIN ===
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# === TRATAMENTO DE ERROS ===
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message="Página não encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return render_template('error.html', error_code=500, error_message="Erro interno do servidor"), 500


# === ROTAS PRINCIPAIS ===
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
        if not u or not e or not p:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('register.html')
        if len(p) < 6:
            flash('Senha deve ter >= 6 caracteres!', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=u).first():
            flash('Usuário já existe!', 'error')
            return render_template('register.html')
        user = User(
            username=u,
            email=e,
            password=generate_password_hash(p)
        )
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))


@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    crypto = market_system.get_crypto_data()
    brazil = market_system.get_brazilian_data()
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()
    return render_template(
        'painel_operacao.html',
        user=user,
        crypto_data=crypto,
        br_data=brazil,
        trades=trades
    )


@app.route('/configurar', methods=['GET','POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key    = request.form.get('binance_api_key','').strip()
        user.binance_api_secret = request.form.get('binance_api_secret','').strip()
        s = request.form.get('saldo_simulado')
        if s:
            user.saldo_simulado = float(s)
        db.session.commit()
        flash('Configurações salvas!', 'success')
    return render_template('configurar.html', user=user)


# === APIs REST ===
@app.route('/api/market_data')
@login_required
def api_market_data():
    try:
        return jsonify({
            'success': True,
            'crypto': market_system.get_crypto_data(),
            'brazilian': market_system.get_brazilian_data(),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intelligent_analysis', methods=['POST'])
@login_required
def api_intelligent_analysis():
    data = request.get_json() or {}
    sym  = data.get('symbol','BTC')
    cosmic = market_system.cosmo.analyze_cosmic_patterns(sym)
    oracle = market_system.oraculo.get_oracle_prediction(sym)
    return jsonify({
        'success': True,
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
    qty  = float(data.get('quantity', 0))

    if not sym or not side or qty <= 0:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

    # Simula preço atual
    cd = market_system.get_crypto_data()
    key = sym.replace('USDT','')
    price = cd.get(key, {}).get('price', 100)

    trade_value = qty * price
    if side == 'BUY':
        if user.saldo_simulado < trade_value:
            return jsonify({'success': False, 'error': 'Saldo insuficiente'}), 400
        user.saldo_simulado -= trade_value
    else:
        user.saldo_simulado += trade_value

    user.total_trades += 1
    pnl = random.uniform(-trade_value*0.05, trade_value*0.08)
    user.profit_loss += pnl
    win_count = Trade.query.filter(Trade.user_id==user.id, Trade.profit_loss>0).count()
    user.win_rate = (win_count / user.total_trades)*100 if user.total_trades else 0

    trade = Trade(
        user_id=user.id,
        symbol=sym,
        side=side,
        quantity=qty,
        entry_price=price,
        profit_loss=pnl,
        strategy_used='Intelligent_System'
    )
    db.session.add(trade)
    db.session.commit()

    return jsonify({
        'success': True,
        'trade_id': trade.id,
        'price': price,
        'pnl': pnl
    })


@app.route('/api/user_trades')
@login_required
def api_user_trades():
    trades = Trade.query.filter_by(user_id=session['user_id'])\
                        .order_by(Trade.timestamp.desc()).limit(50).all()
    return jsonify([t.to_dict() for t in trades])


@app.route('/api/account_info')
@login_required
def api_account_info():
    u = User.query.get(session['user_id'])
    return jsonify({
        'success': True,
        'profit_loss': u.profit_loss,
        'win_rate': u.win_rate,
        'total_trades': u.total_trades,
        'saldo_simulado': u.saldo_simulado
    })


# === WEBSOCKET ===
@socketio.on('connect')
def ws_connect():
    app.logger.info(f'Cliente conectado: {request.sid}')
    emit('connected', {'status': 'success'})


@socketio.on('disconnect')
def ws_disconnect():
    app.logger.info(f'Cliente desconectado: {request.sid}')


@socketio.on('subscribe_market')
def ws_subscribe_market():
    try:
        emit('market_update', {
            'crypto': market_system.get_crypto_data(),
            'brazilian': market_system.get_brazilian_data(),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        emit('error', {'message': str(e)})


# === INICIALIZAÇÃO DO BANCO E USUÁRIOS PADRÃO ===
def create_default_users():
    defaults = [
        {'username':'admin','email':'admin@claraverse.com','password':'admin123'},
        {'username':'Clara','email':'clara@claraverse.com','password':'Verse'},
        {'username':'trader','email':'trader@claraverse.com','password':'trading123'},
        {'username':'demo','email':'demo@claraverse.com','password':'demo123'}
    ]
    for u in defaults:
        if not User.query.filter_by(username=u['username']).first():
            user = User(
                username=u['username'],
                email=u['email'],
                password=generate_password_hash(u['password'])
            )
            db.session.add(user)
    db.session.commit()
    app.logger.info("✅ Usuários padrão criados.")


def initialize_database():
    with app.app_context():
        db.create_all()
        create_default_users()


# === EXECUÇÃO ===
if __name__ == '__main__':
    initialize_database()

    host       = os.environ.get('FLASK_HOST', '127.0.0.1')
    port       = int(os.environ.get('FLASK_PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print("="*50)
    print("🌌 CLARAVERSE TRADING SYSTEM INICIANDO")
    print(f"📍 Host: {host}:{port} | Debug: {debug_mode}")
    print("👥 Usuários de teste:")
    print("   • admin / admin123")
    print("   • Clara / Verse")
    print("   • trader / trading123")
    print("   • demo / demo123")
    print("="*50)

    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True)