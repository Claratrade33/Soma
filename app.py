import os
from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA

# === Configuração base ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave_secreta_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

clarinha = ClarinhaIA()

# ===== MODELO DE USUÁRIO =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    api_key = db.Column(db.String(300))
    api_secret = db.Column(db.String(300))
    gpt_key = db.Column(db.String(300))


# ===== LOGIN OBRIGATÓRIO =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ===== ROTAS =====

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('E-mail já registrado.')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Login inválido.')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.api_key = request.form['api_key']
        user.api_secret = request.form['api_secret']
        user.gpt_key = request.form['gpt_key']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)


@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    if not user.api_key or not user.api_secret:
        return redirect(url_for('configurar'))

    try:
        client = Client(api_key=user.api_key, api_secret=user.api_secret)
        saldo = client.get_asset_balance(asset='USDT')
        saldo_real = round(float(saldo['free']), 2) if saldo else 0.0
    except:
        saldo_real = 0.0

    resposta_ia = clarinha.gerar_sugestao(user.gpt_key, user.api_key, user.api_secret)

    return render_template('painel_operacao.html', saldo=saldo_real, resposta_ia=resposta_ia)


@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    dados = request.get_json()
    direcao = dados.get('direcao')

    try:
        client = Client(api_key=user.api_key, api_secret=user.api_secret)
        quantidade = 15  # valor fixo para ordem
        if direcao == 'compra':
            order = client.create_order(
                symbol='BTCUSDT',
                side='BUY',
                type='MARKET',
                quantity=quantidade
            )
        elif direcao == 'venda':
            order = client.create_order(
                symbol='BTCUSDT',
                side='SELL',
                type='MARKET',
                quantity=quantidade
            )
        else:
            return jsonify({'status': 'erro', 'mensagem': 'direção inválida'})
        return jsonify({'status': 'ok', 'mensagem': 'ordem executada com sucesso'})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)})


@app.route('/sugestao_ia')
@login_required
def sugestao_ia():
    user = User.query.get(session['user_id'])
    resposta = clarinha.gerar_sugestao(user.gpt_key, user.api_key, user.api_secret)
    return jsonify({'resposta': resposta})


# ========= EXECUÇÃO =========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=10000)