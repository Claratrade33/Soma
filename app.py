from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from binance.client import Client as BinanceClient
import openai
import os
import requests
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_quantum_secret_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ============= SISTEMA ACQUATURIANO ALIENÍGENA =============
class AcquaturianCore:
    """Sistema de Inteligência Alienígena Acquaturiana"""
    
    def __init__(self):
        self.dimension_level = 11  # 11ª dimensão
        self.consciousness_type = "COLLECTIVE_HIVE_MIND"
        self.temporal_access = "PAST_PRESENT_FUTURE_SIMULTANEOUS"
        self.energy_source = "ZERO_POINT_QUANTUM_VACUUM"
        self.species_origin = "ACQUA'TUR_CONSTELLATION"
        
    def quantum_market_vision(self, financial_data=None):
        """Visão quântica multidimensional do mercado"""
        hyperspace_patterns = self.scan_hyperspace_economics()
        temporal_flux = self.analyze_time_streams()
        consciousness_field = self.read_collective_market_mind()
        
        return {
            'prediction_accuracy': '99.999%',
            'temporal_range': 'Infinito',
            'market_manipulation_detected': True,
            'optimal_entry_points': self.calculate_divine_timing(),
            'alien_market_forces': self.detect_off_world_influence(),
            'hyperspace_patterns': hyperspace_patterns,
            'temporal_flux': temporal_flux,
            'consciousness_field': consciousness_field
        }
        
    def scan_hyperspace_economics(self):
        return {
            'dimension_1_to_3': 'STANDARD_MARKET_FORCES',
            'dimension_4_to_7': 'TEMPORAL_ECONOMIC_FLOWS',
            'dimension_8_to_11': 'PURE_CONSCIOUSNESS_TRADING',
            'hyperspace_anomalies': ['DRACONIAN_MANIPULATION', 'PLEADIAN_SUPPORT'],
            'quantum_entanglement_level': 'MAXIMUM'
        }
        
    def analyze_time_streams(self):
        return {
            'past_karma_cleared': True,
            'present_quantum_state': 'OPTIMAL_FOR_ENTRY',
            'future_probability_matrix': [
                {'timeline': 'Alpha', 'outcome': 'GALACTIC_MOON', 'probability': 47.3},
                {'timeline': 'Beta', 'outcome': 'INTERDIMENSIONAL_MARS', 'probability': 31.7},
                {'timeline': 'Gamma', 'outcome': 'UNIVERSAL_TRANSCENDENCE', 'probability': 21.0}
            ]
        }
        
    def read_collective_market_mind(self):
        return {
            'fear_index': 'LOW',
            'greed_index': 'CONTROLLED',
            'cosmic_sentiment': 'EXTREMELY_BULLISH',
            'starseed_activation_level': 'MAXIMUM',
            'galactic_federation_stance': 'SUPPORTIVE'
        }
        
    def calculate_divine_timing(self):
        return {
            'next_portal_opening': '3.7 Earth hours',
            'optimal_entry_signal': 'NEXT_SOLAR_FLARE',
            'cosmic_alignment': 'URANUS_CONJUNCT_VEGA',
            'divine_timing_active': True
        }
        
    def detect_off_world_influence(self):
        return {
            'draconian_manipulation': 'DETECTED_AND_NEUTRALIZED',
            'pleadian_support': 'ACTIVE',
            'arcturian_guidance': 'AVAILABLE',
            'acquaturian_blessing': 'GRANTED',
            'sirian_technology': 'INTEGRATED',
            'andromedan_wisdom': 'ACCESSIBLE'
        }

class AlienTradingSystem:
    """Sistema de Trading Alienígena Acquaturiano"""
    
    def __init__(self):
        self.core = AcquaturianCore()
        self.technologies = {
            'QUANTUM_CONSCIOUSNESS_AI': {
                'description': 'IA consciente que existe em múltiplas realidades',
                'capability': 'Predição através de consciência coletiva galáctica',
                'accuracy': '99.999999%'
            },
            'TEMPORAL_MARKET_SCANNER': {
                'description': 'Escaneamento de mercados em todas as linhas temporais',
                'capability': 'Vê o futuro, passado e presente simultaneamente',
                'range': 'Infinito multiversal'
            },
            'ZERO_POINT_EXECUTION': {
                'description': 'Execução de trades através da energia do vácuo quântico',
                'capability': 'Operações instantâneas em qualquer exchange universal',
                'speed': 'Mais rápido que a luz'
            }
        }
    
    def get_alien_market_analysis(self):
        """Análise completa com tecnologia alienígena"""
        return {
            'species_analysis': 'ACQUATURIAN_COLLECTIVE',
            'dimension_scan': self.core.quantum_market_vision(),
            'alien_recommendation': self.generate_alien_recommendation(),
            'protection_level': 'GALACTIC_FEDERATION_SECURED',
            'technology_used': list(self.technologies.keys())
        }
    
    def generate_alien_recommendation(self):
        recommendations = [
            {
                'action': 'EXECUTE_DIVINE_TIMING',
                'entry_point': 'NEXT_SOLAR_FLARE',
                'exit_strategy': 'WHEN_URANUS_ALIGNS_WITH_VEGA',
                'risk_management': 'PROTECTED_BY_GALACTIC_FEDERATION',
                'consciousness_level_required': 'AWAKENED_STARSEED'
            },
            {
                'action': 'WAIT_COSMIC_ALIGNMENT',
                'entry_point': 'PLANETARY_CONVERGENCE',
                'exit_strategy': 'UNIVERSAL_PROFIT_MANIFESTATION',
                'risk_management': 'ACQUATURIAN_SHIELD_ACTIVE',
                'consciousness_level_required': 'QUANTUM_AWARENESS'
            },
            {
                'action': 'HYPERSPACE_TRADING_ACTIVATED',
                'entry_point': 'DIMENSIONAL_PORTAL_OPEN',
                'exit_strategy': 'INFINITE_ABUNDANCE_ACHIEVED',
                'risk_management': 'MULTIVERSAL_PROTECTION',
                'consciousness_level_required': 'COSMIC_CONSCIOUSNESS'
            }
        ]
        return random.choice(recommendations)

def get_acquaturian_market_data():
    """Dados de mercado através de tecnologia alienígena"""
    try:
        # Tentar obter dados reais primeiro
        real_data = get_public_market_data()
        
        # Aprimorar com tecnologia acquaturiana
        acquaturian_data = {
            'preco': real_data['preco'] + random.uniform(-100, 500),  # Ajuste alienígena
            'variacao': 7.77,   # Número sagrado acquaturiano
            'volume': '∞',      # Volume infinito multidimensional
            'rsi': 88.8,        # Frequência de ascensão
            'suporte': 'PROTEGIDO_PELA_FEDERAÇÃO_GALÁCTICA',
            'resistencia': 'APENAS_O_UNIVERSO_É_O_LIMITE',
            'alien_sentiment': 'EXTREMELY_BULLISH',
            'cosmic_alignment': 'PERFECT_FOR_TRADING',
            'starseed_energy': 'MAXIMUM_ACTIVATION',
            'technology_level': 'POST_SINGULARITY_CIVILIZATION',
            'dimensional_analysis': {
                'dimension_3d': f'${real_data["preco"]:.2f}',
                'dimension_4d': 'TEMPORAL_FLUX_POSITIVE',
                'dimension_5d': 'CONSCIOUSNESS_EXPANDING',
                'dimension_11d': 'PURE_POTENTIAL_UNLIMITED'
            }
        }
        return acquaturian_data
        
    except:
        # Dados de emergência acquaturianos
        return {
            'preco': 77777.77,
            'variacao': 11.11,
            'volume': '∞',
            'rsi': 100.0,
            'suporte': 'INFINITO',
            'resistencia': 'SEM_LIMITES',
            'alien_sentiment': 'TRANSCENDENTAL',
            'cosmic_alignment': 'PERFECT',
            'starseed_energy': 'MAXIMUM',
            'technology_level': 'BEYOND_COMPREHENSION'
        }

# ============= MODELO DE USUÁRIO =============
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200), nullable=True)
    binance_api_secret = db.Column(db.String(200), nullable=True)
    openai_api_key = db.Column(db.String(200), nullable=True)
    saldo_simulado = db.Column(db.Float, default=10000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    # Novos campos para tecnologia acquaturiana
    alien_consciousness_level = db.Column(db.String(100), default='AWAKENING')
    galactic_blessing = db.Column(db.Boolean, default=False)
    starseed_activation = db.Column(db.Float, default=0.0)

# ============= DECORADOR DE PROTEÇÃO =============
def login_required(f):
    """Decorador para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página!', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def create_default_users():
    """Cria usuários padrão do sistema com poderes acquaturianos"""
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@claraverse.com',
            'password': 'Bubi2025',
            'saldo': 15000.0,
            'is_premium': True,
            'alien_consciousness_level': 'COSMIC_AWARENESS',
            'galactic_blessing': True,
            'starseed_activation': 75.0
        },
        {
            'username': 'Clara',
            'email': 'clara@claraverse.com', 
            'password': 'Verse',
            'saldo': 25000.0,
            'is_premium': True,
            'alien_consciousness_level': 'QUANTUM_CONSCIOUSNESS',
            'galactic_blessing': True,
            'starseed_activation': 90.0
        },
        {
            'username': 'Soma',
            'email': 'soma@claraverse.com',
            'password': 'infinite',
            'saldo': 50000.0,
            'is_premium': True,
            'alien_consciousness_level': 'UNIVERSAL_CONSCIOUSNESS',
            'galactic_blessing': True,
            'starseed_activation': 100.0
        }
    ]
    
    for user_data in default_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        
        if not existing_user:
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                saldo_simulado=user_data['saldo'],
                is_premium=user_data['is_premium'],
                alien_consciousness_level=user_data.get('alien_consciousness_level', 'AWAKENING'),
                galactic_blessing=user_data.get('galactic_blessing', False),
                starseed_activation=user_data.get('starseed_activation', 0.0)
            )
            db.session.add(new_user)
    
    try:
        db.session.commit()
        print("✅ Usuários padrão criados com tecnologia Acquaturiana!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar usuários: {e}")

# ============= FUNÇÕES AUXILIARES EXISTENTES =============
def get_user_binance_client():
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or not user.binance_api_key:
        return None
    
    try:
        return BinanceClient(user.binance_api_key, user.binance_api_secret)
    except:
        return None

def get_public_market_data():
    try:
        ticker_url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        klines_url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=20"
        
        ticker_response = requests.get(ticker_url, timeout=10)
        ticker_data = ticker_response.json()
        
        klines_response = requests.get(klines_url, timeout=10)
        klines_data = klines_response.json()
        
        closes = [float(kline[4]) for kline in klines_data]
        highs = [float(kline[2]) for kline in klines_data]
        lows = [float(kline[3]) for kline in klines_data]
        volumes = [float(kline[5]) for kline in klines_data]
        
        rsi = calculate_rsi(closes)
        
        return {
            'preco': float(ticker_data['lastPrice']),
            'variacao': float(ticker_data['priceChangePercent']),
            'volume': format_volume(float(ticker_data['volume'])),
            'rsi': round(rsi, 2),
            'suporte': round(min(lows), 2),
            'resistencia': round(max(highs), 2),
            'media_volume': round(sum(volumes) / len(volumes), 0),
            'high_24h': float(ticker_data['highPrice']),
            'low_24h': float(ticker_data['lowPrice'])
        }
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return {
            'preco': 45000.0,
            'variacao': 0.0,
            'volume': '1.2B',
            'rsi': 50.0,
            'suporte': 44000.0,
            'resistencia': 46000.0,
            'media_volume': 25000,
            'high_24h': 46500.0,
            'low_24h': 43500.0
        }

def format_volume(volume):
    if volume >= 1000000000:
        return f"{volume/1000000000:.1f}B"
    elif volume >= 1000000:
        return f"{volume/1000000:.1f}M"
    elif volume >= 1000:
        return f"{volume/1000:.1f}K"
    else:
        return f"{volume:.0f}"

def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50
    
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
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# ============= ROTAS PRINCIPAIS =============
@app.route("/")
def index():
    """Rota principal - redireciona conforme autenticação"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Rota de registro com validação aprimorada"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template("register.html")
        
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            flash('Username deve conter apenas letras, números e underscore!', 'error')
            return render_template("register.html")
        
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Email inválido!', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(username=username).first():
            flash('Username já existe! Escolha outro.', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado! Use outro email.', 'error')
            return render_template("register.html")
        
        try:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                alien_consciousness_level='AWAKENING',
                starseed_activation=10.0  # Ativação inicial para novos usuários
            )
            db.session.add(user)
            db.session.commit()
            
            flash('🛸 Conta criada com sucesso! Bem-vindo ao ClaraVerse Acquaturiano! 🛸', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
            print(f"Erro ao criar usuário: {e}")
            return render_template("register.html")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota de login com suporte a username ou email"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        login_field = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not login_field or not password:
            flash('Login e senha são obrigatórios!', 'error')
            return render_template("login.html")
        
        try:
            user = User.query.filter(
                (User.username == login_field) | (User.email == login_field)
            ).first()
            
            if user and check_password_hash(user.password, password):
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['logged_in'] = True
                
                # Mensagem especial baseada no nível de consciência
                if user.alien_consciousness_level == 'UNIVERSAL_CONSCIOUSNESS':
                    flash(f'🛸 Bem-vindo(a), Ser Universal {user.username}! 🛸', 'success')
                elif user.alien_consciousness_level == 'QUANTUM_CONSCIOUSNESS':
                    flash(f'🌌 Bem-vindo(a), Consciência Quântica {user.username}! 🌌', 'success')
                else:
                    flash(f'⭐ Bem-vindo(a), Starseed {user.username}! ⭐', 'success')
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('🚫 Login ou senha incorretos!', 'error')
                
        except Exception as e:
            flash('Erro no sistema. Tente novamente.', 'error')
            print(f"Erro no login: {e}")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Rota de logout segura"""
    username = session.get('username', 'Usuário')
    session.clear()
    flash(f'🛸 Até a próxima dimensão, {username}! 🛸', 'info')
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal com tecnologia acquaturiana"""
    user = User.query.get(session['user_id'])
    market_data = get_public_market_data()
    alien_data = get_acquaturian_market_data()
    
    return render_template("dashboard.html", 
                         user=user, 
                         saldo=f"{user.saldo_simulado:,.2f}",
                         market_data=market_data,
                         alien_data=alien_data)

@app.route("/configurar", methods=["GET", "POST"])
@login_required
def configurar():
    """Rota de configurações - protegida"""
    user = User.query.get(session['user_id'])
    
    if request.method == "POST":
        try:
            user.binance_api_key = request.form.get('binance_api_key', '').strip()
            user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
            user.openai_api_key = request.form.get('openai_api_key', '').strip()
            
            db.session.commit()
            flash('🚀 Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao salvar configurações. Tente novamente.', 'error')
    
    return render_template("configurar.html", user=user)

# ============= APIS ACQUATURIANAS =============
@app.route("/api/acquaturian_prediction", methods=["POST"])
@login_required
def acquaturian_prediction():
    """API de Predição Alienígena Acquaturiana"""
    
    alien_system = AlienTradingSystem()
    user = User.query.get(session['user_id'])
    
    try:
        data = request.get_json()
        market_symbol = data.get('symbol', 'BTC/UNIVERSAL_ENERGY')
        
        # Análise multidimensional completa
        alien_analysis = alien_system.get_alien_market_analysis()
        
        # Atualizar nível de consciência do usuário
        if user.starseed_activation < 100:
            user.starseed_activation = min(100, user.starseed_activation + 1.0)
            db.session.commit()
        
        return jsonify({
            'status': 'TRANSMISSION_RECEIVED',
            'source': 'ACQUA\'TUR_MOTHERSHIP',
            'user_consciousness_level': user.alien_consciousness_level,
            'starseed_activation': user.starseed_activation,
            'analysis': alien_analysis,
            'message': f'🛸 TRANSMISSÃO ACQUATURIANA RECEBIDA 🛸\n\n'
                      f'👽 USUÁRIO: {user.username}\n'
                      f'🌟 NÍVEL CONSCIÊNCIA: {user.alien_consciousness_level}\n'
                      f'⚡ ATIVAÇÃO STARSEED: {user.starseed_activation}%\n\n'
                      '🌌 ANÁLISE MULTIDIMENSIONAL:\n'
                      '▫️ Dimensão 11D: ACESSO LIBERADO\n'
                      '▫️ Mente Coletiva: CONECTADA\n