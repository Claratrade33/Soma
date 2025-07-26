import os
from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA

# === Configuração inicial ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')  # corrigido aqui

# === Modelos ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class APIKeys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    binance_key = db.Column(db.String(255))
    binance_secret = db.Column(db.String(255))
    openai_key = db.Column(db.String(255))

# === Decorador de login ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# === Rotas principais ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('painel_operacao'))
        else:
            flash('Credenciais inválidas.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Cadastro realizado com sucesso.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user_id = session['user_id']
    if request.method == 'POST':
        binance_key = request.form['binance_key']
        binance_secret = request.form['binance_secret']
        openai_key = request.form['openai_key']

        existing = APIKeys.query.filter_by(user_id=user_id).first()
        if existing:
            existing.binance_key = binance_key
            existing.binance_secret = binance_secret
            existing.openai_key = openai_key
        else:
            novo = APIKeys(
                user_id=user_id,
                binance_key=binance_key,
                binance_secret=binance_secret,
                openai_key=openai_key
            )
            db.session.add(novo)

        db.session.commit()
        return redirect(url_for('painel_operacao'))

    return render_template('configurar.html')

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user_id = session['user_id']
    keys = APIKeys.query.filter_by(user_id=user_id).first()
    saldo = 0.0
    sugestao = {}

    if keys and keys.binance_key and keys.binance_secret:
        try:
            client = Client(keys.binance_key, keys.binance_secret)
            info = client.get_asset_balance(asset='USDT')
            saldo = float(info['free']) if info else 0.0
        except Exception as e:
            print(f"[ERRO SALDO BINANCE]: {e}")
            saldo = 0.0

    if keys and keys.openai_key:
        try:
            clarinha = ClarinhaIA(keys.openai_key)
            sugestao = clarinha.obter_sugestao()
        except Exception as e:
            print(f"[ERRO GPT]: {e}")
            sugestao = {"erro": "Falha ao gerar sugestão"}

    return render_template('painel_operacao.html', saldo=saldo, sugestao=sugestao)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user_id = session['user_id']
    acao = request.json.get('acao')
    keys = APIKeys.query.filter_by(user_id=user_id).first()

    if not keys or not keys.binance_key or not keys.binance_secret:
        return jsonify({"status": "erro", "mensagem": "Chaves da Binance não configuradas."})

    try:
        client = Client(keys.binance_key, keys.binance_secret)
        if acao == 'compra':
            ordem = client.order_market_buy(symbol='BTCUSDT', quantity=0.0005)
        elif acao == 'venda':
            ordem = client.order_market_sell(symbol='BTCUSDT', quantity=0.0005)
        else:
            return jsonify({"status": "erro", "mensagem": "Ação inválida."})

        return jsonify({"status": "sucesso", "detalhes": ordem})

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

# === WebSocket básico (opcional) ===
@socketio.on('connect')
def handle_connect():
    print('Usuário conectado via WebSocket')

# === Início da aplicação ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=10000)