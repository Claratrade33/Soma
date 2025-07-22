It seems like you've encountered the same SyntaxError again in your app.py file, specifically on line 525, within the user_trades() API endpoint.
The problematic line:
return jsonify([trade.to_dict() for trade inreturn jsonify([trade.to_dict() for trade in trades])

As identified previously, this line has a duplicate return jsonify([trade.to_dict() for trade in part. This causes a syntax error because Python expects the for loop to be followed by the in keyword and an iterable, not another return jsonify statement.
Here's the corrected app.py file, with the fix applied to line 525. I've also re-checked the rest of your code for any obvious syntax issues, but the primary one was that specific line.
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import traceback
from datetime import datetime, timedelta
import logging
import json
import random
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claraverse_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Inicialização das extensões
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============= MODELOS DE DADOS =============
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

# ============= CLARINHA COSMO - IA AVANÇADA =============
class ClarinhaCosmo:
    def __init__(self):
        self.ml_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        
    def analyze_cosmic_patterns(self, symbol):
        try:
            # Simulação de dados históricos
            data = self.generate_market_data(symbol)
            
            # Análise de padrões ocultos
            hidden_patterns = self.detect_hidden_patterns(data)
            
            # Detecção de manipulação
            manipulation_score = self.detect_manipulation(data)
            
            # Previsão ML
            ml_prediction = self.ml_prediction(data)
            
            # Sinal cósmico
            cosmic_signal = self.calculate_cosmic_signal(data)
            
            return {
                'cosmic_signal': cosmic_signal,
                'hidden_patterns': hidden_patterns,
                'manipulation_detected': manipulation_score > 0.7,
                'ml_prediction': ml_prediction,
                'entry_confidence': random.uniform(0.6, 0.95),
                'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            app.logger.error(f"Erro Clarinha Cosmo: {e}")
            return self.get_fallback_analysis()
    
    def generate_market_data(self, symbol):
        # Gera dados simulados para análise
        prices = [100 + random.uniform(-5, 5) for _ in range(100)]
        volumes = [random.uniform(1000, 10000) for _ in range(100)]
        return {'prices': prices, 'volumes': volumes}
    
    def detect_hidden_patterns(self, data):
        return {
            'volume_divergence': random.choice([True, False]),
            'price_action_anomaly': random.choice([True, False]),
            'whale_accumulation': random.choice([True, False])
        }
    
    def detect_manipulation(self, data):
        return random.uniform(0.1, 0.9)
    
    def ml_prediction(self, data):
        directions = ['BUY', 'SELL', 'NEUTRAL']
        return {
            'direction': random.choice(directions),
            'confidence': random.uniform(0.5, 0.9)
        }
    
    def calculate_cosmic_signal(self, data):
        signals = ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']
        return random.choice(signals)
    
    def get_fallback_analysis(self):
        return {
            'cosmic_signal': 'NEUTRAL',
            'hidden_patterns': {'volume_divergence': False, 'price_action_anomaly': False, 'whale_accumulation': False},
            'manipulation_detected': False,
            'ml_prediction': {'direction': 'NEUTRAL', 'confidence': 0.5},
            'entry_confidence': 0.5,
            'risk_level': 'MEDIUM'
        }

# ============= CLARINHA ORÁCULO - PREVISÕES =============
class ClarinhaOraculo:
    def get_oracle_prediction(self, symbol):
        try:
            # Análise de sentimento simulada
            sentiment = self.analyze_sentiment()
            
            # Dados on-chain simulados
            onchain_data = self.analyze_onchain_data()
            
            # Análise temporal
            temporal_analysis = self.temporal_prediction()
            
            # Combinar previsões
            final_prediction = self.combine_predictions(sentiment, onchain_data, temporal_analysis)
            
            return final_prediction
        except Exception as e:
            app.logger.error(f"Erro Clarinha Oráculo: {e}")
            return self.get_fallback_prediction()
    
    def analyze_sentiment(self):
        fear_greed = random.randint(0, 100)
        labels = ['EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'EXTREME_GREED']
        
        if fear_greed < 20: label = labels[0] # Corrected: labels instead of labels[0] for the first condition
        elif fear_greed < 45: label = labels[1]
        elif fear_greed < 55: label = labels[2]
        elif fear_greed < 80: label = labels[3]
        else: label = labels[4]
        
        return {
            'score': fear_greed / 100,
            'label': label,
            'fear_greed_index': fear_greed
        }
    
    def analyze_onchain_data(self):
        return {
            'whale_activity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'exchange_flows': random.choice(['INFLOW', 'OUTFLOW', 'NEUTRAL']),
            'holder_behavior': random.choice(['ACCUMULATING', 'DISTRIBUTING', 'HOLDING'])
        }
    
    def temporal_prediction(self):
        return {
            'optimal_hours': [9, 14, 20],
            'current_time_score': random.uniform(0.3, 1.0),
            'weekly_trend': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
        }
    
    def combine_predictions(self, sentiment, onchain, temporal):
        score = random.randint(-5, 5)
        predictions = ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']
        
        if score >= 3: prediction = 'STRONG_BUY'
        elif score >= 1: prediction = 'BUY'
        elif score <= -3: prediction = 'STRONG_SELL'
        elif score <= -1: prediction = 'SELL'
        else: prediction = 'NEUTRAL'
        
        return {
            'prediction': prediction,
            'confidence': random.uniform(0.6, 0.95),
            'score': score,
            'sentiment': sentiment,
            'onchain': onchain,
            'temporal': temporal
        }
    
    def get_fallback_prediction(self):
        return {
            'prediction': 'NEUTRAL',
            'confidence': 0.5,
            'score': 0,
            'sentiment': {'score': 0.5, 'label': 'NEUTRAL', 'fear_greed_index': 50},
            'onchain': {'whale_activity': 'MEDIUM'},
            'temporal': {'weekly_trend': 'NEUTRAL'}
        }

# ============= SISTEMA DE MERCADO =============
class MarketSystem:
    def __init__(self):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo()
        
    def get_crypto_data(self):
        base_prices = {
            'BTC': 97500,
            'ETH': 3400,
            'BNB': 720,
            'ADA': 1.25,
            'SOL': 145,
            'XRP': 0.85
        }
        
        crypto_data = {}
        for symbol, base_price in base_prices.items():
            variation = random.uniform(-5, 5)
            current_price = base_price * (1 + variation / 100)
            
            crypto_data[symbol] = {
                'price': round(current_price, 2),
                'change_24h': round(variation, 2),
                'volume_24h': random.randint(500000, 2000000),
                'high_24h': round(current_price * 1.05, 2),
                'low_24h': round(current_price * 0.95, 2),
                'rsi': round(random.uniform(20, 80), 1)
            }
        
        return crypto_data
    
    def get_brazilian_data(self):
        return {
            'IBOV': {
                'price': 134167 + random.randint(-1000, 1000),
                'change_percent': round(random.uniform(-2, 2), 2)
            },
            'USD_BRL': {
                'price': 5.55 + random.uniform(-0.1, 0.1),
                'change_percent': round(random.uniform(-1, 1), 2)
            }
        }

# Instâncias globais
market_system = MarketSystem()

# ============= DECORADOR DE LOGIN =============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============= TRATAMENTO DE ERROS =============
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Página não encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('error.html', error_code=500, error_message="Erro interno do servidor"), 500

# ============= ROTAS PRINCIPAIS =============
@app.route("/")
def index():
    try:
        if 'user_id' in session:
            return redirect(url_for('painel_operacao'))
        return render_template("index.html")
    except Exception as e:
        app.logger.error(f"Erro index: {e}")
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session.permanent = True
                flash(f'Bem-vindo, {user.username}!', 'success')
                return redirect(url_for('painel_operacao'))
            else:
                flash('Credenciais inválidas!', 'error')
        
        return render_template("login.html")
    except Exception as e:
        app.logger.error(f"Erro login: {e}")
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not email or not password:
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template("register.html")
            
            if len(password) < 6:
                flash('A senha deve ter pelo menos 6 caracteres!', 'error')
                return render_template("register.html")
            
            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já existe!', 'error')
                return render_template("register.html")
            
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('login'))
        
        return render_template("register.html")
    except Exception as e:
        app.logger.error(f"Erro register: {e}")
        db.session.rollback()
        flash('Erro interno. Tente novamente.', 'error')
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route("/painel_operacao")
@login_required
def painel_operacao():
    try:
        user = User.query.get(session['user_id'])
        crypto_data = market_system.get_crypto_data()
        br_data = market_system.get_brazilian_data()
        trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()
        
        return render_template("painel_operacao.html",
                             user=user,
                             crypto_data=crypto_data,
                             br_data=br_data,
                             trades=trades)
    except Exception as e:
        app.logger.error(f"Erro painel: {e}")
        return redirect(url_for('index'))

@app.route("/configurar", methods=["GET", "POST"])
@login_required
def configurar():
    try:
        user = User.query.get(session['user_id'])
        
        if request.method == "POST":
            user.binance_api_key = request.form.get('binance_api_key', '').strip()
            user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
            
            saldo = request.form.get('saldo_simulado')
            if saldo:
                user.saldo_simulado = float(saldo)
            
            db.session.commit()
            flash('Configurações salvas com sucesso!', 'success')
        
        return render_template("configurar.html", user=user)
    except Exception as e:
        app.logger.error(f"Erro configurar: {e}")
        return render_template("configurar.html", user=user)

# ============= APIs =============
@app.route("/api/market_data")
@login_required
def api_market_data():
    try:
        return jsonify({
            'success': True,
            'crypto': market_system.get_crypto_data(),
            'brazilian': market_system.get_brazilian_data(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/intelligent_analysis", methods=["POST"])
@login_required
def intelligent_analysis():
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC')
        
        cosmic_analysis = market_system.cosmo.analyze_cosmic_patterns(symbol)
        oracle_prediction = market_system.oraculo.get_oracle_prediction(symbol)
        
        return jsonify({
            'success': True,
            'cosmic': cosmic_analysis,
            'oracle': oracle_prediction,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/execute_trade", methods=["POST"])
@login_required
def execute_trade():
    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity', 0))
        
        if not symbol or not side or quantity <= 0:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
        # Simular preço
        crypto_data = market_system.get_crypto_data()
        symbol_clean = symbol.replace('USDT', '')
        price = crypto_data.get(symbol_clean, {}).get('price', 100)
        
        # Criar trade
        trade = Trade(
            user_id=user.id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=price,
            strategy_used='Intelligent_System'
        )
        
        # Atualizar saldo
        trade_value = quantity * price
        if side == 'BUY':
            if user.saldo_simulado >= trade_value:
                user.saldo_simulado -= trade_value
            else:
                return jsonify({'success': False, 'error': 'Saldo insuficiente'}), 400
        else:
            user.saldo_simulado += trade_value
        
        user.total_trades += 1
        
        # Simular P&L aleatório
        pnl = random.uniform(-trade_value * 0.05, trade_value * 0.08)
        trade.profit_loss = pnl
        user.profit_loss += pnl
        
        # Calcular win rate
        if user.total_trades > 0:
            winning_trades = Trade.query.filter(
                Trade.user_id == user.id,
                Trade.profit_loss > 0
            ).count()
            user.win_rate = (winning_trades / user.total_trades) * 100
        
        db.session.add(trade)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'trade_id': trade.id,
            'price': price,
            'status': 'FILLED',
            'pnl': pnl
        })
    except Exception as e:
        app.logger.error(f"Erro trade: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/user_trades")
@login_required
def user_trades():
    try:
        trades = Trade.query.filter_by(user_id=session['user_id']).order_by(Trade.timestamp.desc()).limit(50).all()
        # Corrected line 525: Removed the duplicate jsonify call
        return jsonify([trade.to_dict() for trade in trades])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/account_info")
@login_required
def account_info():
    try:
        user = User.query.get(session['user_id'])
        return jsonify({
            'success': True,
            'profit_loss': user.profit_loss,
            'win_rate': user.win_rate,
            'total_trades': user.total_trades,
            'saldo_simulado': user.saldo_simulado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= WEBSOCKET =============
@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('subscribe_market')
def handle_market_subscription():
    try:
        crypto_data = market_system.get_crypto_data()
        br_data = market_system.get_brazilian_data()
        
        emit('market_update', {
            'crypto': crypto_data,
            'brazilian': br_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('error', {'message': str(e)})

# ============= INICIALIZAÇÃO =============
def create_default_users():
    """Criar usuários padrão para demonstração"""
    default_users = [
        {'username': 'admin', 'email': 'admin@claraverse.com', 'password': 'admin123'},
        {'username': 'Clara', 'email': 'clara@claraverse.com', 'password': 'Verse'},
        {'username': 'trader', 'email': 'trader@claraverse.com', 'password': 'trading123'},
        {'username': 'demo', 'email': 'demo@claraverse.com', 'password': 'demo123'}
    ]
    
    for user_data in default_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password'])
            )
            db.session.add(user)
    
    try:
        db.session.commit()
        app.logger.info("✅ Usuários padrão criados com sucesso!")
    except Exception as e:
        app.logger.error(f"❌ Erro ao criar usuários: {e}")
        db.session.rollback()

def initialize_database():
    """Inicialização segura do banco de dados"""
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            
            # Criar usuários padrão
            create_default_users()
            
            app.logger.info("🗄️ Banco de dados inicializado com sucesso!")
            return True
    except Exception as e:
        app.logger.error(f"❌ Erro na inicialização do banco: {e}")
        return False

# ============= EXECUTAR APLICAÇÃO =============
if __name__ == '__main__':
    # Inicializar banco de dados
    if not initialize_database():
        print("❌ Falha na inicialização do banco de dados!")
        exit(1)
    
    # Configurações do servidor
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("=" * 60)
    print("🌌 CLARAVERSE TRADING SYSTEM - INICIANDO")
    print("=" * 60)
    print(f"🚀 Servidor: http://{host}:{port}")
    print(f"🔧 Debug: {'Ativado' if debug_mode else 'Desativado'}")
    print("👥 Usuários de teste disponíveis:")
    print("   - admin / admin123")
    print("   - Clara / Verse") 
    print("   - trader / trading123")
    print("   - demo / demo123")
    print("=" * 60)
    
    try:
        socketio.run(
            app, 
            debug=debug_mode, 
            host=host, 
            port=port, 
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")


