import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for,
    request, session, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client

from clarinha_ia import ClarinhaIA

# === Configuração do app ===
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_claraverse_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
ia = ClarinhaIA()

# === Modelos ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200))
    binance_api_secret = db.Column(db.String(200))
    saldo_simulado = db.Column(db.Float, default=10000.0)

# === Login obrigatório ===
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

# === Rotas ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, senha):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
        else:
            novo = User(username=username, email=email, password=senha)
            db.session.add(novo)
            db.session.commit()
            flash('Cadastro realizado. Faça login.', 'success')
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
        user.binance_api_key = request.form['binance_api_key']
        user.binance_api_secret = request.form['binance_api_secret']
        user.saldo_simulado = float(request.form['saldo_simulado'])
        db.session.commit()
        flash("🔐 Chaves salvas com sucesso!", "success")
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    if not user.binance_api_key or not user.binance_api_secret:
        flash('Configure suas chaves da Binance para operar.', 'error')
        return redirect(url_for('configurar'))

    client = Client(user.binance_api_key, user.binance_api_secret)
    saldo = client.get_asset_balance(asset='USDT')
    saldo_real = float(saldo['free']) if saldo else 0.0
    sugestao = ia.gerar_sugestao('BTCUSDT')
    preco_atual = client.get_symbol_ticker(symbol='BTCUSDT')['price']

    return render_template(
        'painel_operacao.html',
        user=user,
        saldo_real=round(saldo_real, 2),
        sugestao=sugestao,
        preco_atual=round(float(preco_atual), 2)
    )

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    client = Client(user.binance_api_key, user.binance_api_secret)

    tipo = request.form.get('tipo')  # COMPRAR ou VENDER
    quantidade = float(request.form.get('quantidade', 0.001))

    try:
        if tipo == 'COMPRAR':
            ordem = client.order_market_buy(
                symbol='BTCUSDT',
                quantity=quantidade
            )
        elif tipo == 'VENDER':
            ordem = client.order_market_sell(
                symbol='BTCUSDT',
                quantity=quantidade
            )
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Tipo inválido'})

        return jsonify({'status': 'sucesso', 'dados': ordem})

    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)})

# === Inicializar Banco ===
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)