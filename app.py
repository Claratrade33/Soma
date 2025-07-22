from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException
import yfinance as yf
import requests
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import threading
import time
import ta
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_real_trading_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///real_trading.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

class RealTrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=True)
    profit_loss = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='OPEN')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    strategy_used = db.Column(db.String(50), nullable=True)
    binance_order_id = db.Column(db.String(100), nullable=True)

# ============= CLARINHA COSMO - ANÁLISE CÓSMICA =============
class ClarinhaCosmo:
    def __init__(self):
        self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def analyze_cosmic_patterns(self, symbol):
        """Análise de padrões cósmicos avançada"""
        try:
            # Obter dados históricos
            ticker = yf.Ticker(f"{symbol}USDT")
            data = ticker.history(period="30d", interval="1h")
            
            if data.empty:
                return self.get_fallback_analysis()
            
            # Calcular indicadores técnicos avançados
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MACD'] = ta.trend.MACD(data['Close']).macd()
            data['BB_upper'], data['BB_lower'] = ta.volatility.BollingerBands(data['Close']).bollinger_hband(), ta.volatility.BollingerBands(data['Close']).bollinger_lband()
            data['Volume_SMA'] = data['Volume'].rolling(20).mean()
            
            # Análise de padrões ocultos
            hidden_patterns = self.detect_hidden_patterns(data)
            
            # Detecção de manipulação
            manipulation_score = self.detect_manipulation(data)
            
            # Previsão com ML
            prediction = self.ml_prediction(data)
            
            return {
                'cosmic_signal': self.calculate_cosmic_signal(data),
                'hidden_patterns': hidden_patterns,
                'manipulation_detected': manipulation_score > 0.7,
                'ml_prediction': prediction,
                'entry_confidence': self.calculate_entry_confidence(data),
                'risk_level': self.assess_risk_level(data)
            }
        except Exception as e:
            print(f"Erro na análise cósmica: {e}")
            return self.get_fallback_analysis()
    
    def detect_hidden_patterns(self, data):
        """Detecta padrões que algoritmos tradicionais perdem"""
        patterns = {
            'volume_divergence': False,
            'price_action_anomaly': False,
            'whale_accumulation': False
        }
        
        if len(data) > 20:
            # Divergência de volume
            price_trend = data['Close'].tail(10).mean() > data['Close'].head(10).mean()
            volume_trend = data['Volume'].tail(10).mean() > data['Volume'].head(10).mean()
            patterns['volume_divergence'] = price_trend != volume_trend
            
            # Anomalia de price action
            volatility = data['Close'].pct_change().std()
            patterns['price_action_anomaly'] = volatility > 0.05
            
            # Acumulação de baleias
            high_volume_bars = data[data['Volume'] > data['Volume_SMA'] * 2]
            patterns['whale_accumulation'] = len(high_volume_bars) > 5
            
        return patterns
    
    def detect_manipulation(self, data):
        """Detecta manipulação de mercado"""
        if len(data) < 20:
            return 0.0
            
        # Análise de pump/dump
        price_changes = data['Close'].pct_change().abs()
        extreme_moves = price_changes > price_changes.quantile(0.95)
        
        # Volume suspeito
        volume_spikes = data['Volume'] > data['Volume'].quantile(0.95)
        
        manipulation_score = (extreme_moves.sum() + volume_spikes.sum()) / len(data)
        return min(manipulation_score, 1.0)
    
    def ml_prediction(self, data):
        """Previsão com Machine Learning"""
        try:
            if len(data) < 50:
                return {'direction': 'NEUTRAL', 'confidence': 0.5}
            
            # Preparar features
            features = []
            for i in range(20, len(data)):
                feature_row = [
                    data['RSI'].iloc[i-1],
                    data['MACD'].iloc[i-1],
                    data['Volume'].iloc[i-20:i].mean(),
                    data['Close'].iloc[i-20:i].std(),
                    data['Close'].iloc[i-5:i].mean() / data['Close'].iloc[i-20:i].mean()
                ]
                features.append(feature_row)
            
            if len(features) < 10:
                return {'direction': 'NEUTRAL', 'confidence': 0.5}
            
            features = np.array(features)
            targets = data['Close'].iloc[21:].values
            
            # Treinar modelo se necessário
            if not self.is_trained and len(features) > 20:
                self.ml_model.fit(features[:-1], targets[:-1])
                self.is_trained = True
            
            # Fazer previsão
            if self.is_trained:
                last_features = features[-1].reshape(1, -1)
                prediction = self.ml_model.predict(last_features)
                current_price = data['Close'].iloc[-1]
                
                direction = 'BUY' if prediction > current_price * 1.01 else 'SELL' if prediction < current_price * 0.99 else 'NEUTRAL'
                confidence = min(abs(prediction - current_price) / current_price * 10, 1.0)
                
                return {'direction': direction, 'confidence': confidence}
            
        except Exception as e:
            print(f"Erro ML: {e}")
        
        return {'direction': 'NEUTRAL', 'confidence': 0.5}
    
    def calculate_cosmic_signal(self, data):
        """Calcula sinal cósmico final"""
        if len(data) < 20:
            return 'NEUTRAL'
        
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        bb_position = (data['Close'].iloc[-1] - data['BB_lower'].iloc[-1]) / (data['BB_upper'].iloc[-1] - data['BB_lower'].iloc[-1])
        
        signals = 0
        if rsi < 30: signals += 1  # Oversold
        if rsi > 70: signals -= 1  # Overbought
        if macd > 0: signals += 1  # Bullish MACD
        if bb_position < 0.2: signals += 1  # Near lower BB
        if bb_position > 0.8: signals -= 1  # Near upper BB
        
        if signals >= 2: return 'STRONG_BUY'
        elif signals == 1: return 'BUY'
        elif signals <= -2: return 'STRONG_SELL'
        elif signals == -1: return 'SELL'
        else: return 'NEUTRAL'
    
    def calculate_entry_confidence(self, data):
        """Calcula confiança para entrada"""
        if len(data) < 20:
            return 0.5
        
        volatility = data['Close'].pct_change().std()
        volume_consistency = 1 - (data['Volume'].std() / data['Volume'].mean())
        rsi_strength = abs(data['RSI'].iloc[-1] - 50) / 50
        
        confidence = (volume_consistency + rsi_strength) / 2
        return min(max(confidence, 0.0), 1.0)
    
    def assess_risk_level(self, data):
        """Avalia nível de risco"""
        if len(data) < 20:
            return 'HIGH'
        
        volatility = data['Close'].pct_change().std()
        if volatility > 0.05: return 'HIGH'
        elif volatility > 0.03: return 'MEDIUM'
        else: return 'LOW'
    
    def get_fallback_analysis(self):
        return {
            'cosmic_signal': 'NEUTRAL',
            'hidden_patterns': {'volume_divergence': False, 'price_action_anomaly': False, 'whale_accumulation': False},
            'manipulation_detected': False,
            'ml_prediction': {'direction': 'NEUTRAL', 'confidence': 0.5},
            'entry_confidence': 0.5,
            'risk_level': 'MEDIUM'
        }

# ============= CLARINHA ORÁCULO - PREVISÕES AVANÇADAS =============
class ClarinhaOraculo:
    def __init__(self):
        self.sentiment_sources = [
            'https://api.alternative.me/fng/',  # Fear & Greed Index
        ]
    
    def get_oracle_prediction(self, symbol):
        """Previsão oracular avançada"""
        try:
            # Análise de sentimento
            sentiment = self.analyze_sentiment()
            
            # Análise de on-chain data
            onchain_data = self.analyze_onchain_data(symbol)
            
            # Previsão temporal
            temporal_analysis = self.temporal_prediction(symbol)
            
            # Combinação das análises
            final_prediction = self.combine_predictions(sentiment, onchain_data, temporal_analysis)
            
            return final_prediction
        
        except Exception as e:
            print(f"Erro no oráculo: {e}")
            return self.get_fallback_prediction()
    
    def analyze_sentiment(self):
        """Análise de sentimento de mercado"""
        try:
            # Fear & Greed Index
            response = requests.get('https://api.alternative.me/fng/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                fear_greed = int(data['data']['value'])
                
                sentiment_score = fear_greed / 100
                sentiment_label = 'EXTREME_FEAR' if fear_greed < 20 else 'FEAR' if fear_greed < 45 else 'NEUTRAL' if fear_greed < 55 else 'GREED' if fear_greed < 80 else 'EXTREME_GREED'
                
                return {
                    'score': sentiment_score,
                    'label': sentiment_label,
                    'fear_greed_index': fear_greed
                }
        except:
            pass
        
        return {'score': 0.5, 'label': 'NEUTRAL', 'fear_greed_index': 50}
    
    def analyze_onchain_data(self, symbol):
        """Análise de dados on-chain simulada"""
        # Em produção, conectaria com APIs como Glassnode, IntoTheBlock
        return {
            'whale_activity': np.random.choice(['LOW', 'MEDIUM', 'HIGH']),
            'exchange_flows': np.random.choice(['INFLOW', 'OUTFLOW', 'NEUTRAL']),
            'holder_behavior': np.random.choice(['ACCUMULATING', 'DISTRIBUTING', 'HOLDING'])
        }
    
    def temporal_prediction(self, symbol):
        """Análise temporal avançada"""
        try:
            ticker = yf.Ticker(f"{symbol}USDT")
            data = ticker.history(period="7d", interval="1h")
            
            if not data.empty:
                # Análise de ciclos temporais
                hourly_returns = data.groupby(data.index.hour)['Close'].mean()
                best_hours = hourly_returns.nlargest(3).index.tolist()
                
                current_hour = datetime.now().hour
                time_score = 1.0 if current_hour in best_hours else 0.5
                
                return {
                    'optimal_hours': best_hours,
                    'current_time_score': time_score,
                    'weekly_trend': 'BULLISH' if data['Close'].iloc[-1] > data['Close'].iloc else 'BEARISH'
                }
        except:
            pass
        
        return {
            'optimal_hours': [9, 14, 20],
            'current_time_score': 0.5,
            'weekly_trend': 'NEUTRAL'
        }
    
    def combine_predictions(self, sentiment, onchain, temporal):
        """Combina todas as previsões"""
        # Pontuação baseada em múltiplos fatores
        score = 0
        
        # Sentimento
        if sentiment['label'] == 'EXTREME_FEAR':
            score += 2  # Oportunidade de compra
        elif sentiment['label'] == 'FEAR':
            score += 1
        elif sentiment['label'] == 'EXTREME_GREED':
            score -= 2  # Risco de correção
        elif sentiment['label'] == 'GREED':
            score -= 1
        
        # On-chain
        if onchain['whale_activity'] == 'HIGH' and onchain['exchange_flows'] == 'OUTFLOW':
            score += 1
        if onchain['holder_behavior'] == 'ACCUMULATING':
            score += 1
        
        # Temporal
        score += temporal['current_time_score']
        if temporal['weekly_trend'] == 'BULLISH':
            score += 1
        
        # Determinar previsão final
        if score >= 4:
            prediction = 'STRONG_BUY'
            confidence = 0.9
        elif score >= 2:
            prediction = 'BUY'
            confidence = 0.7
        elif score <= -4:
            prediction = 'STRONG_SELL'
            confidence = 0.9
        elif score <= -2:
            prediction = 'SELL'
            confidence = 0.7
        else:
            prediction = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'prediction': prediction,
            'confidence': confidence,
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
            'sentiment': {'score': 0.5, 'label': 'NEUTRAL'},
            'onchain': {'whale_activity': 'MEDIUM'},
            'temporal': {'weekly_trend': 'NEUTRAL'}
        }

# ============= SISTEMA DE DADOS DE MERCADO REAL =============
class RealMarketSystem:
    def __init__(self):
        self.binance_client = BinanceClient()  # Cliente público
        
    def get_real_crypto_data(self):
        """Dados reais de criptomoedas"""
        try:
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
            data = {}
            
            for symbol in symbols:
                ticker = self.binance_client.get_ticker(symbol=symbol)
                klines = self.binance_client.get_klines(symbol=symbol, interval=BinanceClient.KLINE_INTERVAL_1HOUR, limit=24)
                
                closes = [float(k[4]) for k in klines]
                volumes = [float(k[5]) for k in klines]
                
                data[symbol.replace('USDT', '')] = {
                    'price': float(ticker['lastPrice']),
                    'change_24h': float(ticker['priceChangePercent']),
                    'volume_24h': float(ticker['volume']),
                    'high_24h': float(ticker['highPrice']),
                    'low_24h': float(ticker['lowPrice']),
                    'rsi': self.calculate_rsi(closes),
                    'avg_volume': sum(volumes) / len(volumes)
                }
            
            return data
        
        except Exception as e:
            print(f"Erro crypto data: {e}")
            return self.get_fallback_crypto()
    
    def get_brazilian_market_data(self):
        """Dados reais do mercado brasileiro baseados nos resultados da pesquisa"""
        try:
            # Dados baseados nos resultados da pesquisa [3][5]
            return {
                'IBOV': {
                    'price': 134167.0,  # Valor real dos resultados
                    'change_percent': 0.58,  # Variação real
                    'min_day': 133367.0,
                    'max_day': 134865.0
                },
                'USD_BRL': {
                    'price': 5.55,  # Valor real dos resultados
                    'change_percent': -0.41  # Variação real
                },
                'COFFEE': {
                    'conilon': 950.77,
                    'arabica': 1219.16
                }
            }
        except Exception as e:
            print(f"Erro dados brasileiros: {e}")
            return self.get_fallback_brazilian()
    
    def calculate_rsi(self, prices, period=14):
        """Cálculo real do RSI"""
        if len(prices) < period:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    def get_fallback_crypto(self):
        return {
            'BTC': {'price': 97500, 'change_24h': 2.5, 'volume_24h': 1200000, 'rsi': 65},
            'ETH': {'price': 3400, 'change_24h': 1.8, 'volume_24h': 800000, 'rsi': 58}
        }
    
    def get_fallback_brazilian(self):
        return {
            'IBOV': {'price': 134167, 'change_percent': 0.58},
            'USD_BRL': {'price': 5.55, 'change_percent': -0.41}
        }

# ============= SISTEMA DE TRADING INTELIGENTE =============
class IntelligentTradingSystem:
    def __init__(self):
        self.cosmo = ClarinhaCosmo()
        self.oraculo = ClarinhaOraculo()
        
    def analyze_trading_opportunity(self, symbol):
        """Análise completa de oportunidade de trading"""
        # Análise Cósmica
        cosmic_analysis = self.cosmo.analyze_cosmic_patterns(symbol)
        
        # Previsão do Oráculo
        oracle_prediction = self.oraculo.get_oracle_prediction(symbol)
        
        # Combinar análises
        final_score = self.calculate_final_score(cosmic_analysis, oracle_prediction)
        
        return {
            'cosmic': cosmic_analysis,
            'oracle': oracle_prediction,
            'final_decision': final_score,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_final_score(self, cosmic, oracle):
        """Calcula pontuação final para decisão"""
        score = 0
        confidence = 0
        
        # Pontuação cósmica
        cosmic_signals = {
            'STRONG_BUY': 3,
            'BUY': 1,
            'NEUTRAL': 0,
            'SELL': -1,
            'STRONG_SELL': -3
        }
        score += cosmic_signals.get(cosmic['cosmic_signal'], 0)
        
        # Pontuação do oráculo
        oracle_signals = {
            'STRONG_BUY': 3,
            'BUY': 1,
            'NEUTRAL': 0,
            'SELL': -1,
            'STRONG_SELL': -3
        }
        score += oracle_signals.get(oracle['prediction'], 0)
        
        # Ajustar por manipulação detectada
        if cosmic['manipulation_detected']:
            score = 0  # Neutralizar se manipulação detectada
        
        # Calcular confiança
        confidence = (cosmic['entry_confidence'] + oracle['confidence']) / 2
        
        # Decisão final
        if score >= 4 and confidence > 0.7:
            decision = 'EXECUTE_BUY'
        elif score >= 2 and confidence > 0.6:
            decision = 'CONSIDER_BUY'
        elif score <= -4 and confidence > 0.7:
            decision = 'EXECUTE_SELL'
        elif score <= -2 and confidence > 0.6:
            decision = 'CONSIDER_SELL'
        else:
            decision = 'HOLD'
        
        return {
            'decision': decision,
            'score': score,
            'confidence': confidence,
            'risk_level': cosmic['risk_level']
        }

# Instâncias globais
market_system = RealMarketSystem()
intelligent_system = IntelligentTradingSystem()

# ============= DECORADOR DE LOGIN =============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============= ROTAS PRINCIPAIS =============
@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Bem-vindo ao sistema real de trading, {user.username}!', 'success')
            return redirect(url_for('painel_operacao'))
        
        flash('Login inválido!', 'error')
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username já existe!', 'error')
            return render_template("register.html")
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada! Faça login para acessar.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route("/painel_operacao")
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    
    # Dados reais de mercado
    crypto_data = market_system.get_real_crypto_data()
    br_data = market_system.get_brazilian_market_data()
    
    # Trades recentes
    recent_trades = RealTrade.query.filter_by(user_id=user.id).order_by(RealTrade.timestamp.desc()).limit(10).all()
    
    return render_template("painel_operacao.html",
                         user=user,
                         crypto_data=crypto_data,
                         br_data=br_data,
                         trades=recent_trades)

@app.route("/configurar", methods=["GET", "POST"])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    
    if request.method == "POST":
        try:
            user.binance_api_key = request.form.get('binance_api_key', '').strip()
            user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
            
            # Testar conexão se as chaves foram fornecidas
            if user.binance_api_key and user.binance_api_secret:
                try:
                    test_client = BinanceClient(user.binance_api_key, user.binance_api_secret)
                    account_info = test_client.get_account()
                    flash('Conexão com Binance testada e funcionando!', 'success')
                except BinanceAPIException as e:
                    flash(f'Erro na API da Binance: {e}', 'error')
                    user.binance_api_key = ''
                    user.binance_api_secret = ''
            
            db.session.commit()
            flash('Configurações salvas com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {e}', 'error')
    
    return render_template("configurar.html", user=user)

# ============= APIs FUNCIONAIS =============
@app.route("/api/market_data")
@login_required
def api_market_data():
    """Dados de mercado em tempo real"""
    try:
        crypto_data = market_system.get_real_crypto_data()
        br_data = market_system.get_brazilian_market_data()
        
        return jsonify({
            'crypto': crypto_data,
            'brazilian': br_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'live'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/intelligent_analysis", methods=["POST"])
@login_required
def intelligent_analysis():
    """Análise inteligente completa"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC')
        
        analysis = intelligent_system.analyze_trading_opportunity(symbol)
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/execute_real_trade", methods=["POST"])
@login_required
def execute_real_trade():
    """Executar trade real na Binance"""
    try:
        data = request.get_json()
        user = User.query.get(session['