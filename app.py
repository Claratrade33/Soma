import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")  # CORRIGIDO

# MODELO DE USUÁRIO
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# DECORADOR DE LOGIN
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ROTA PRINCIPAL
@app.route('/')
def index():
    return redirect(url_for('login'))

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas')
    return render_template('login.html')

# REGISTRO
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Conta criada com sucesso!')
        return redirect(url_for('login'))
    return render_template('register.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ROTA DO PAINEL
@app.route('/painel_operacao')
@login_required
def painel_operacao():
    return render_template('painel_operacao.html')

# ROTA DE CONFIGURAR API
@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    if request.method == 'POST':
        session['binance_api'] = request.form.get('binance_api')
        session['binance_secret'] = request.form.get('binance_secret')
        session['openai_key'] = request.form.get('openai_key')
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html')

# ROTA PARA EXECUTAR ORDENS
@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    dados = request.json
    acao = dados.get('acao')

    api_key = session.get('binance_api')
    api_secret = session.get('binance_secret')

    if not api_key or not api_secret:
        return jsonify({'erro': 'Chaves da Binance não configuradas.'}), 400

    client = Client(api_key, api_secret)
    try:
        if acao == 'comprar':
            order = client.order_market_buy(symbol='BTCUSDT', quantity=0.001)
        elif acao == 'vender':
            order = client.order_market_sell(symbol='BTCUSDT', quantity=0.001)
        else:
            return jsonify({'erro': 'Ação inválida'}), 400
        return jsonify({'mensagem': 'Ordem executada com sucesso!', 'ordem': order})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# SUGESTÃO DA IA CLARINHA
@app.route('/sugestao_ia')
@login_required
def sugestao_ia():
    openai_key = session.get('openai_key')
    if not openai_key:
        return jsonify({'erro': 'Chave OpenAI não configurada'}), 400
    ia = ClarinhaIA(openai_key)
    resultado = ia.gerar_sugestao()
    return jsonify(resultado)