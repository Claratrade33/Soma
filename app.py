import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from binance.client import Client
from clarinha_ia import ClarinhaIA
from galactic_bot import iniciar_galactic_bot

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_real_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///real_claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# === MODELO DE USUÁRIO REAL ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_key = db.Column(db.String(300))
    binance_secret = db.Column(db.String(300))

with app.app_context():
    db.create_all()

# === AUTENTICAÇÃO ===
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# === ROTAS PRINCIPAIS ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/painel_operacao')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            return 'Email já registrado'
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect('/painel_operacao')
        return 'Credenciais inválidas'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    saldo_usdt = '0.00'
    if user and user.binance_key and user.binance_secret:
        try:
            client = Client(user.binance_key, user.binance_secret)
            conta = client.get_asset_balance(asset='USDT')
            saldo_usdt = conta['free']
        except Exception as e:
            saldo_usdt = f"Erro: {e}"
    return render_template('painel_operacao.html', saldo=saldo_usdt)

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        key = request.form['binance_key']
        secret = request.form['binance_secret']
        user.binance_key = key
        user.binance_secret = secret
        db.session.commit()
        return redirect('/painel_operacao')
    return render_template('configurar.html')

# === EXECUÇÃO REAL COM CLARINHA ===
@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    if not user.binance_key or not user.binance_secret:
        return jsonify({'erro': 'Chaves não configuradas'}), 400

    client = Client(user.binance_key, user.binance_secret)
    simbolo = request.json.get('simbolo', 'BTCUSDT')
    acao = request.json.get('acao')  # 'BUY' ou 'SELL'
    quantidade = float(request.json.get('quantidade', 0.001))

    try:
        ordem = client.create_order(
            symbol=simbolo,
            side=acao.upper(),
            type='MARKET',
            quantity=quantidade
        )
        return jsonify({'sucesso': True, 'ordem': ordem})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/ia_sugestao')
@login_required
def ia_sugestao():
    user = User.query.get(session['user_id'])
    if not user.binance_key or not user.binance_secret:
        return jsonify({'erro': 'Sem API configurada'}), 400

    try:
        clarinha = ClarinhaIA(user.binance_key, user.binance_secret)
        resposta = clarinha.analisar()
        return jsonify(resposta)
    except Exception as e:
        return jsonify({'erro': str(e)})

# === GALACTIC BOT DE SEGURANÇA ===
iniciar_galactic_bot()

# === EXECUÇÃO FINAL ===
if __name__ == '__main__':
    socketio.run(app, debug=True)