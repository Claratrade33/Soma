import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA

# === App base ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave_claraverse_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)

# === Modelo de Usuário ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    api_key = db.Column(db.String(255))
    api_secret = db.Column(db.String(255))

# === Login obrigatório ===
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# === Rota base ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

# === Registro ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['email']
        senha = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return redirect(url_for('register'))

        novo_user = User(
            username=nome,
            email=email,
            password=generate_password_hash(senha)
        )
        db.session.add(novo_user)
        db.session.commit()
        flash('Conta criada com sucesso. Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# === Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, senha):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        else:
            flash('Credenciais inválidas.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# === Logout ===
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# === Painel principal ===
@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])

    if not user.api_key or not user.api_secret:
        return redirect(url_for('configurar'))

    try:
        client = Client(api_key=user.api_key, api_secret=user.api_secret)
        info = client.get_account()
        saldo_usdt = 0.0
        for b in info['balances']:
            if b['asset'] == 'USDT':
                saldo_usdt = round(float(b['free']), 2)
                break
    except Exception as e:
        saldo_usdt = 0.0
        flash(f'Erro ao conectar com a Binance: {str(e)}', 'error')

    ia = ClarinhaIA()
    sugestao = ia.analisar()

    return render_template(
        'painel.html',
        saldo_usdt=saldo_usdt,
        sugestao=sugestao,
        crypto_data={},
        trades=[]
    )

# === Configurar API ===
@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.api_key = request.form['api_key']
        user.api_secret = request.form['api_secret']
        db.session.commit()
        flash('Chaves salvas com sucesso.', 'success')
        return redirect(url_for('painel_operacao'))

    return render_template('configurar.html')

# === Executar Ordem via API externa (JSON) ===
@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    if not user.api_key or not user.api_secret:
        return jsonify({'erro': 'Chaves não configuradas.'})

    tipo = request.json.get('tipo')
    simbolo = request.json.get('simbolo', 'BTCUSDT')
    quantidade = float(request.json.get('quantidade', 0.001))

    try:
        client = Client(api_key=user.api_key, api_secret=user.api_secret)
        if tipo == 'compra':
            ordem = client.order_market_buy(symbol=simbolo, quantity=quantidade)
        elif tipo == 'venda':
            ordem = client.order_market_sell(symbol=simbolo, quantity=quantidade)
        else:
            return jsonify({'erro': 'Tipo inválido'})

        return jsonify({'status': 'Ordem executada', 'ordem': ordem})
    except Exception as e:
        return jsonify({'erro': str(e)})

# === Executar Trade via Formulário (painel.html) ===
@app.route('/trade', methods=['POST'])
@login_required
def trade():
    user = User.query.get(session['user_id'])

    if not user.api_key or not user.api_secret:
        flash('Configure suas chaves de API antes de operar.', 'error')
        return redirect(url_for('configurar'))

    symbol = request.form['symbol']
    side = request.form['side']
    quantity = float(request.form['quantity'])

    try:
        client = Client(api_key=user.api_key, api_secret=user.api_secret)
        if side == 'BUY':
            ordem = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif side == 'SELL':
            ordem = client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            flash('Tipo de operação inválido.', 'error')
            return redirect(url_for('painel_operacao'))

        flash('Ordem executada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao executar ordem: {str(e)}', 'error')

    return redirect(url_for('painel_operacao'))

# === IA Sugestão (opcional) ===
@app.route('/ia_sugestao')
@login_required
def ia_sugestao():
    ia = ClarinhaIA()
    sugestao = ia.analisar()
    return jsonify(sugestao)

# === Criar Tabelas ===
with app.app_context():
    db.create_all()

# === Rodar app ===
if __name__ == '__main__':
    app.run(debug=True)