# app.py
import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import ClarinhaIA
from binance.client import Client
from clara_bunker import BunkerSeguro

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
bunker = BunkerSeguro()

# ----------------------------------------------------------------
# MODELS
# ----------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    # campos criptografados para API keys
    openai_key_enc     = db.Column(db.LargeBinary, nullable=True)
    binance_key_enc    = db.Column(db.LargeBinary, nullable=True)
    binance_secret_enc = db.Column(db.LargeBinary, nullable=True)

    def set_keys(self, openai_key, bin_key, bin_secret):
        self.openai_key_enc     = bunker.criptografar(openai_key)
        self.binance_key_enc    = bunker.criptografar(bin_key)
        self.binance_secret_enc = bunker.criptografar(bin_secret)

    def get_openai_key(self):
        return bunker.descriptografar(self.openai_key_enc) if self.openai_key_enc else None

    def get_binance_keys(self):
        if not (self.binance_key_enc and self.binance_secret_enc):
            return None, None
        return (
            bunker.descriptografar(self.binance_key_enc),
            bunker.descriptografar(self.binance_secret_enc)
        )

class Operacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entrada   = db.Column(db.String(50))
    alvo      = db.Column(db.String(50))
    stop      = db.Column(db.String(50))
    confianca = db.Column(db.String(50))
    sugestao  = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# ----------------------------------------------------------------
# AUTH DECORATOR
# ----------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id']   = user.id
            session['username']  = user.username
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login agora.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        # coleta do formulário
        openai_key = request.form['openai_key']
        bin_key    = request.form['binance_key']
        bin_secret = request.form['binance_secret']

        # salva criptografado no banco
        user.set_keys(openai_key, bin_key, bin_secret)
        db.session.commit()

        flash('Chaves configuradas e criptografadas com sucesso!')
        return redirect(url_for('painel_operacao'))

    return render_template('configurar.html')

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    # monta IA com chave do usuário
    ia = ClarinhaIA(user.get_openai_key())
    sugestao = ia.gerar_sugestao()

    # salva operação
    op = Operacao(
        usuario_id=session['user_id'],
        entrada  = sugestao.get("entrada"),
        alvo     = sugestao.get("alvo"),
        stop     = sugestao.get("stop"),
        confianca= sugestao.get("confianca"),
        sugestao = sugestao.get("sugestao")
    )
    db.session.add(op)
    db.session.commit()

    operacoes = Operacao.query\
        .filter_by(usuario_id=session['user_id'])\
        .order_by(Operacao.timestamp.desc())\
        .all()

    return render_template('painel_operacao.html', sugestao=sugestao, operacoes=operacoes)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    api_key, api_secret = user.get_binance_keys()
    if not api_key or not api_secret:
        return jsonify({"erro": "Chaves da Binance não configuradas"}), 400

    dados = request.json
    tipo  = dados.get("tipo")
    cliente = Client(api_key, api_secret)

    try:
        if tipo == "entrada":
            ordem = cliente.order_market_buy(symbol="BTCUSDT", quantity=0.001)
        elif tipo == "stop":
            ordem = cliente.order_market_sell(symbol="BTCUSDT", quantity=0.001)
        elif tipo == "alvo":
            ordem = cliente.order_limit_sell(
                symbol="BTCUSDT",
                quantity=0.001,
                price="70000",
                timeInForce="GTC"
            )
        else:
            return jsonify({"erro": "Tipo de ordem inválido"}), 400

        return jsonify({"status": "Ordem executada", "ordem": ordem})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ----------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
