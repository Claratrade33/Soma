import os
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client

from clarinha_ia import ClarinhaIA
from galactic_bot import iniciar_galactic_bot

# ===== CONFIGURAÇÃO FLASK =====
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ===== MODELOS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200))
    binance_api_secret = db.Column(db.String(200))
    openai_api_key = db.Column(db.String(200))

# ===== AUTENTICAÇÃO =====
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# ===== ROTAS =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['email']
        senha = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash('Email já registrado.')
            return redirect(url_for('register'))

        novo_usuario = User(username=nome, email=email, password=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        usuario = User.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, senha):
            session['user_id'] = usuario.id
            session.permanent = True
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    usuario = User.query.get(session['user_id'])
    if request.method == 'POST':
        usuario.binance_api_key = request.form['binance_key']
        usuario.binance_api_secret = request.form['binance_secret']
        usuario.openai_api_key = request.form['openai_key']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', usuario=usuario)

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    usuario = User.query.get(session['user_id'])

    saldo_usdt = "--"
    sugestao = {"mensagem": "Insira sua chave OpenAI para ativar a IA."}

    if usuario.binance_api_key and usuario.binance_api_secret:
        try:
            cliente = Client(api_key=usuario.binance_api_key, api_secret=usuario.binance_api_secret)
            conta = cliente.get_asset_balance(asset='USDT')
            saldo_usdt = float(conta['free'])
        except:
            saldo_usdt = "Erro"

    if usuario.openai_api_key:
        ia = ClarinhaIA(openai_key=usuario.openai_api_key)
        sugestao = ia.gerar_sugestao()

    return render_template('painel.html', saldo=saldo_usdt, sugestao=sugestao)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    usuario = User.query.get(session['user_id'])
    simbolo = request.form.get('simbolo', 'BTCUSDT')
    lado = request.form.get('lado', 'BUY')
    quantidade = float(request.form.get('quantidade', 10.0))

    if not usuario.binance_api_key or not usuario.binance_api_secret:
        return jsonify({"status": "erro", "mensagem": "Chaves Binance não configuradas."})

    try:
        cliente = Client(api_key=usuario.binance_api_key, api_secret=usuario.binance_api_secret)
        ordem = cliente.order_market(symbol=simbolo, side=lado, quantity=quantidade)
        return jsonify({"status": "ok", "ordem": ordem})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

# ===== INICIALIZAÇÃO =====
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        iniciar_galactic_bot()
    socketio.run(app, host='0.0.0.0', port=5000)