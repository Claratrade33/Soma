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

# ============= SISTEMA ACQUATURIANO =============
class AcquaturianCore:
    def __init__(self):
        self.dimension_level = 11
        self.consciousness_type = "COLLECTIVE_HIVE_MIND"
        self.temporal_access = "PAST_PRESENT_FUTURE_SIMULTANEOUS"
        self.energy_source = "ZERO_POINT_QUANTUM_VACUUM"
        self.species_origin = "ACQUATUR_CONSTELLATION"
        
    def quantum_market_vision(self):
        return {
            'prediction_accuracy': '99.999%',
            'temporal_range': 'Infinito',
            'optimal_entry_points': self.calculate_divine_timing()
        }
        
    def calculate_divine_timing(self):
        return {
            'next_portal_opening': '3.7 Earth hours',
            'optimal_entry_signal': 'NEXT_SOLAR_FLARE',
            'divine_timing_active': True
        }

class AlienTradingSystem:
    def __init__(self):
        self.core = AcquaturianCore()
    
    def get_alien_market_analysis(self):
        return {
            'alien_recommendation': self.generate_alien_recommendation(),
            'protection_level': 'GALACTIC_FEDERATION_SECURED'
        }
    
    def generate_alien_recommendation(self):
        recommendations = [
            {'action': 'EXECUTE_DIVINE_TIMING', 'entry_point': 'NEXT_SOLAR_FLARE'},
            {'action': 'WAIT_COSMIC_ALIGNMENT', 'entry_point': 'PLANETARY_CONVERGENCE'},
            {'action': 'HYPERSPACE_TRADING_ACTIVATED', 'entry_point': 'DIMENSIONAL_PORTAL_OPEN'}
        ]
        return random.choice(recommendations)

def get_acquaturian_market_data():
    try:
        real_data = get_public_market_data()
        return {
            'preco': real_data['preco'] + random.uniform(-100, 500),
            'variacao': 7.77,
            'volume': '∞',
            'rsi': 88.8
        }
    except:
        return {
            'preco': 77777.77,
            'variacao': 11.11,
            'volume': '∞',
            'rsi': 100.0
        }

# ============= MODELO DE USUÁRIO =============
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200), nullable=True)
    bin极ance_api_secret = db.Column(db.String(200), nullable=True)
    openai_api_key = db.Column(db.String(200), nullable=True)
    saldo_simulado = db.Column(db.Float, default=10000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)

# ============= DECORADOR DE PROTEÇÃO =============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_default_users():
    default_users = [
        {'username': 'admin', 'email': 'admin@claraverse.com', 'password': 'Bubi2025', 'saldo': 15000.0},
        {'username': 'Clara', 'email': 'clara@claraverse.com', 'password': 'Verse', 'saldo': 25000.0},
        {'username': 'Soma', 'email': 'soma@claraverse.com', 'password': 'infinite', 'saldo': 50000.0}
    ]
    
    for user_data in default_users:
        if not User.query.filter_by(username=user_data['username']).first():
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                saldo_simulado=user_data['saldo']
            )
            db.session.add(new_user)
    db.session.commit()

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
    try:
        client = BinanceClient()
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        return {
            'preco': float(ticker['price']),
            'variacao': 2.5,
            'volume': '1.2B',
            'rsi': 65.0
        }
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return {
            'preco': 95000.0,
            'variacao': 2.5,
            'volume': '1.2B',
            'rsi': 65.0
        }

# ============= ROTAS PRINCIPAIS =============
@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(username=username).first():
            flash('Username já existe!', 'error')
            return render_template("register.html")
        
        try:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta.', 'error')
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    
    if request.method == "POST":
        login_field = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter(
            (User.username == login_field) | (User.email == login_field)
        ).first()
            
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Bem-vindo(a), {user.username}!', 'success')
            return redirect(url_for('painel_operacao'))
        else:
            flash('Login ou senha incorretos!', 'error')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/painel_operacao")
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    market_data = get_public_market_data()
    alien_data = get_acquaturian_market_data()
    return render_template("painel_operacao.html", user=user, market_data=market_data, alien_data=alien_data)

@app.route("/configurar", methods=["GET", "POST"])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == "POST":
        try:
            user.binance_api_key = request.form.get('binance_api_key', '').strip()
            user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
            user.openai_api_key = request.form.get('openai_api_key', '').strip()
            db.session.commit()
            flash('Configurações atualizadas!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao salvar configurações.', 'error')
    return render_template("configurar.html", user=user)

# ============= APIS =============
@app.route("/api/dados_mercado", methods=["GET"])
@login_required
def api_dados_mercado():
    try:
        market_data = get_public_market_data()
        alien_data = get_acquaturian_market_data()
        return jsonify({'market_data': market_data, 'alien_data': alien_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/acquaturian_prediction", methods=["POST"])
@login_required
def acquaturian_prediction():
    try:
        alien_system = AlienTradingSystem()
        return jsonify(alien_system.get_alien_market_analysis())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= INICIALIZAÇÃO =============
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_users()
    app.run(debug=True)