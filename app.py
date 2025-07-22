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
        self.dimension_level = 11
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
        
    def read_collective_market_m mind(self):
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
        real_data = get_public_market_data()
        
        acquaturian_data = {
            'preco': real_data['preco'] + random.uniform(-100, 500),
            'variacao': 7.77,
            'volume': '∞',
            'rsi': 88.8,
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
    alien_consciousness_level = db.Column(db.String(100), default='AWAKENING')
    galactic_blessing = db.Column(db.Boolean, default=False)
    starseed_activation = db.Column(db.Float, default=0.0)

# ============= DECORADOR DE PROTEÇÃO =============
def login_required(f):
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
    default_users = [        {
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

# ============= FUNÇÕES AUXILIARES =============
def get_user_binance_client():
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or not user.binance_api_key:
        return None
    
    try:
        return BinanceClient(
            api_key=user.binance_api_key,
            api_secret=user.binance_api_secret,
            testnet=False
        )
    except Exception as e:
        print(f"Erro ao criar cliente Binance: {e}")
        return None

def get_public_market_data():
    """Obter dados de mercado com fallback seguro"""
    try:
        # Usando a API pública da Binance sem chaves
        client = BinanceClient()
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        klines = client.get_klines(symbol="BTCUSDT", interval=BinanceClient.KLINE_INTERVAL_1HOUR, limit=20)
        
        closes = [float(kline[4]) for kline in klines]
        highs = [float(kline[2]) for kline in klines]
        lows = [float(kline[3]) for kline in klines]
        volumes = [float(kline[5]) for kline in klines]
        
        rsi = calculate_rsi(closes)
        
        return {
            'preco': float(ticker['price']),
            'variacao': (float(ticker['price']) - float(klines[4])) / float(klines[4]) * 100,
            'volume': format_volume(sum(volumes)),
            'rsi': round(rsi, 2),
            'suporte': round(min(lows), 2),
            'resistencia': round(max(highs), 2),
            'media_volume': round(sum(volumes) / len(volumes), 0),
            'high_24h': max(highs),
            'low_24h': min(lows)
        }
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return {
            'preco': 95000.0,
            'variacao': 2.5,
            'volume': '1.2B',
            'rsi': 65.0,
            'suporte': 93000.0,
            'resistencia': 97000.0,
            'media_volume': 25000,
            'high_24h': 96500.0,
            'low_24h': 93500.0
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
        change = prices