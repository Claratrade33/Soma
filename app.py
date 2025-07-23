import os
from datetime import datetime, timedelta
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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ======== MODELOS ========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200), nullable=True)
    binance_api_secret = db.Column(db.String(200), nullable=True)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=True)
    profit_loss = db.Column(db.Float, nullable=True)
    strategy_used = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

ia = ClarinhaIA()

# ======== AUTENTICAÇÃO ========
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return redirect(url_for('painel_operacao') if 'user_id' in session else 'login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, senha):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Login inválido.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
        else:
            user = User(username=username, email=email, password=senha)
            db.session.add(user)
            db.session.commit()
            flash('Cadastro realizado com sucesso.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ======== PAINEL COM SALDO REAL ========
@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    saldo_usdt = 0.0
    crypto_data = {}
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(10).all()

    if user and user.binance_api_key and user.binance_api_secret:
        try:
            cliente = Client(user.binance_api_key, user.binance_api_secret)
            conta = cliente.get_asset_balance(asset='USDT')
            saldo_usdt = float(conta['free']) if conta else 0.0

            ticker = cliente.get_ticker(symbol='BTCUSDT')
            crypto_data = {
                'BTCUSDT': {
                    'price': float(ticker['lastPrice']),
                    'change_24h': float(ticker['priceChangePercent']),
                    'volume_24h': float(ticker['quoteVolume']),
                    'rsi': round(ia.cosmo.analisar()['confianca'] * 100, 2)
                }
            }

        except Exception as e:
            flash(f'Erro ao conectar com Binance: {e}', 'error')

    return render_template('painel_operacao.html', user=user, saldo_usdt=saldo_usdt, crypto_data=crypto_data, trades=trades)

# ======== CONFIGURAR API KEYS ========
@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_api_key = request.form.get('binance_api_key')
        user.binance_api_secret = request.form.get('binance_api_secret')
        db.session.commit()
        flash('Chaves salvas com sucesso.', 'success')

        # Testar a conexão com a API da Binance
        try:
            cliente = Client(user.binance_api_key, user.binance_api_secret)
            cliente.ping()  # Verifica se a conexão está funcionando
            flash('Conexão com a Binance estabelecida com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao conectar com Binance: {e}', 'error')

        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

# ======== SUGESTÃO DA IA ========
@app.route('/api/sugestao')
@login_required
def sugestao():
    return jsonify(ia.gerar_sugestao())

# ======== RODAR TRADE ========
@app.route('/trade', methods=['POST'])
@login_required
def trade():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        side = request.form.get('side')  # 'BUY' ou 'SELL'
        quantity = request.form.get('quantity')

        try:
            cliente = Client(user.binance_api_key, user.binance_api_secret)
            order = cliente.order_market(
                symbol=symbol,
                side=side,
                quantity=quantity
            )

            # Salvar trade no banco de dados
            new_trade = Trade(
                user_id=user.id,
                symbol=symbol,
                side=side,
                entry_price=float(order['fills'][0]['price']),  # Preço de entrada
                timestamp=datetime.utcnow()
            )
            db.session.add(new_trade)
            db.session.commit()

            flash('Trade executada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao executar trade: {e}', 'error')

    return redirect(url_for('painel_operacao'))

# ======== RODAR APP ========
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)