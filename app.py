import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
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

# === Modelos ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    api_key_binance = db.Column(db.String(200))
    api_secret_binance = db.Column(db.String(200))
    openai_key = db.Column(db.String(200))

# === Login obrigatório ===
def login_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view_func(**kwargs)
    return wrapped_view

# === Rotas ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = request.form['password']
        if User.query.filter_by(email=email).first():
            return render_template('register.html', erro='Email já cadastrado')
        hash_senha = generate_password_hash(senha)
        novo = User(username=username, email=email, password=hash_senha)
        db.session.add(novo)
        db.session.commit()
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
        user.api_key_binance = request.form['api_key']
        user.api_secret_binance = request.form['api_secret']
        user.openai_key = request.form['openai_key']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html', user=user)

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    if not user.api_key_binance or not user.api_secret_binance or not user.openai_key:
        return redirect(url_for('configurar'))

    try:
        client = Client(user.api_key_binance, user.api_secret_binance)
        saldo = client.get_asset_balance(asset='USDT')
        valor = saldo['free'] if saldo else '0.00'
    except Exception as e:
        valor = "Erro ao conectar"

    return render_template('painel_operacao.html', saldo=valor)

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    tipo = request.form.get('tipo')  # 'compra', 'venda', 'auto'
    if not all([user.api_key_binance, user.api_secret_binance, user.openai_key]):
        return 'Chaves não configuradas', 400

    client = Client(user.api_key_binance, user.api_secret_binance)

    try:
        if tipo == 'auto':
            clarinha = ClarinhaIA(user.openai_key)
            sugestao = clarinha.gerar_sugestao("BTCUSDT")
            if sugestao['entrada'] and sugestao['direcao'] == 'compra':
                client.order_market_buy(symbol="BTCUSDT", quantity=15)
            elif sugestao['direcao'] == 'venda':
                client.order_market_sell(symbol="BTCUSDT", quantity=15)
            return 'Ordem automática executada'
        elif tipo == 'compra':
            client.order_market_buy(symbol="BTCUSDT", quantity=15)
            return 'Compra executada com sucesso'
        elif tipo == 'venda':
            client.order_market_sell(symbol="BTCUSDT", quantity=15)
            return 'Venda executada com sucesso'
        else:
            return 'Tipo de ordem inválido', 400
    except Exception as e:
        return f'Erro: {str(e)}', 500

# === Inicialização ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
