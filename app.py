# app.py (com execução real de ordens Binance integrada)
import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import ClarinhaIA
from binance.client import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# Modelo de operação
class Operacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entrada = db.Column(db.String(50))
    alvo = db.Column(db.String(50))
    stop = db.Column(db.String(50))
    confianca = db.Column(db.String(50))
    sugestao = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota inicial
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login
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

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        novo_usuario = User(username=username, email=email, password=password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login agora.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Painel de operação com IA e relatório
@app.route('/painel_operacao')
@login_required
def painel_operacao():
    ia = ClarinhaIA(os.getenv("OPENAI_API_KEY"))
    sugestao = ia.gerar_sugestao()

    nova_operacao = Operacao(
        usuario_id=session['user_id'],
        entrada=sugestao.get("entrada"),
        alvo=sugestao.get("alvo"),
        stop=sugestao.get("stop"),
        confianca=sugestao.get("confianca"),
        sugestao=sugestao.get("sugestao")
    )
    db.session.add(nova_operacao)
    db.session.commit()

    operacoes = Operacao.query.filter_by(usuario_id=session['user_id']).order_by(Operacao.timestamp.desc()).all()

    return render_template('painel_operacao.html', sugestao=sugestao, operacoes=operacoes)

# Execução real de ordens na Binance
@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    dados = request.json
    tipo = dados.get("tipo")  # entrada, stop, alvo
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        return jsonify({"erro": "Chaves da Binance não configuradas"}), 400

    try:
        cliente = Client(api_key, api_secret)

        if tipo == "entrada":
            ordem = cliente.order_market_buy(symbol="BTCUSDT", quantity=0.001)
        elif tipo == "stop":
            ordem = cliente.order_market_sell(symbol="BTCUSDT", quantity=0.001)
        elif tipo == "alvo":
            ordem = cliente.order_limit_sell(
                symbol="BTCUSDT",
                quantity=0.001,
                price="70000",
                timeInForce="GTC")
        else:
            return jsonify({"erro": "Tipo de ordem inválido"}), 400

        return jsonify({"status": "Ordem executada com sucesso", "ordem": ordem})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)