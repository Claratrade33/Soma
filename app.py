import os
from datetime import timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
import openai

# ===== APP BASE =====
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'claraverse_secret_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
db = SQLAlchemy(app)


# ===== MODEL =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(255), default='')
    binance_api_secret = db.Column(db.String(255), default='')
    gpt_api_key = db.Column(db.String(255), default='')


def criar_usuarios_iniciais():
    iniciais = [
        {"username": "admin", "password": "Bubi2025"},
        {"username": "Soma",  "password": "123456"},
        {"username": "Clara", "password": "verse"},
    ]
    for u in iniciais:
        if not User.query.filter_by(username=u["username"]).first():
            novo = User(
                username=u["username"],
                password=generate_password_hash(u["password"])
            )
            db.session.add(novo)
    db.session.commit()


with app.app_context():
    db.create_all()
    criar_usuarios_iniciais()


# ===== AUTENTICAÇÃO =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None


# ===== ROTAS =====
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session.permanent = True
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))

        flash('Usuário ou senha inválidos.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash('Preencha todos os campos.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'error')
            return render_template('register.html')

        novo = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(novo)
        db.session.commit()

        flash('Registro criado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = get_user()
    if request.method == 'POST':
        user.binance_api_key = request.form['binance_api_key'].strip()
        user.binance_api_secret = request.form['binance_api_secret'].strip()
        user.gpt_api_key = request.form['gpt_api_key'].strip()
        db.session.commit()

        flash('Chaves salvas com sucesso!', 'success')
        return redirect(url_for('painel_operacao'))

    return render_template('configurar.html', user=user)


@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = get_user()
    if not (user.binance_api_key and user.binance_api_secret and user.gpt_api_key):
        flash('Configure suas chaves para operar!', 'info')
        return redirect(url_for('configurar'))

    try:
        client = Client(user.binance_api_key, user.binance_api_secret)
        account = client.get_account()
        balances = account.get('balances', [])
        saldo_btc = next((b['free'] for b in balances if b['asset'] == 'BTC'), '0')
        saldo_usdt = next((b['free'] for b in balances if b['asset'] == 'USDT'), '0')
    except Exception as e:
        saldo_btc = saldo_usdt = '0'
        flash(f'Erro ao conectar na Binance: {e}', 'error')

    return render_template(
        'painel_operacao.html',
        user=user,
        saldo_btc=saldo_btc,
        saldo_usdt=saldo_usdt
    )


@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = get_user()
    if not (user.binance_api_key and user.binance_api_secret):
        return jsonify({'status': 'erro', 'mensagem': 'Chaves Binance não configuradas.'}), 400

    data = request.get_json(silent=True) or request.form
    tipo_ordem = data.get('tipo_ordem', '').lower()
    simbolo = data.get('simbolo', 'BTCUSDT').upper()

    try:
        quantidade = float(data.get('quantidade', '0.001'))
    except ValueError:
        return jsonify({'status': 'erro', 'mensagem': 'Quantidade inválida.'}), 400

    try:
        client = Client(user.binance_api_key, user.binance_api_secret)
        if tipo_ordem == 'compra':
            ordem = client.create_order(
                symbol=simbolo, side='BUY', type='MARKET', quantity=quantidade
            )
        elif tipo_ordem == 'venda':
            ordem = client.create_order(
                symbol=simbolo, side='SELL', type='MARKET', quantity=quantidade
            )
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Tipo de ordem inválido.'}), 400

        return jsonify({
            'status': 'sucesso',
            'mensagem': f'Ordem executada: {tipo_ordem.upper()} {quantidade} {simbolo}',
            'ordem': ordem
        })

    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': f'Erro ao executar ordem: {e}'}), 400


@app.route('/sugestao_gpt', methods=['POST'])
@login_required
def sugestao_gpt():
    user = get_user()
    if not user.gpt_api_key:
        return jsonify({'erro': 'Chave GPT não configurada.'}), 400

    prompt = request.json.get(
        'prompt',
        'Faça uma sugestão de operação para BTCUSDT com análise técnica.'
    )
    openai.api_key = user.gpt_api_key

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma IA especialista em operações de criptomoedas, "
                        "foco em sinais claros, alvo, stop e explicação breve."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        texto = resposta.choices[0].message.content.strip()
        return jsonify({'sugestao': texto})

    except Exception as e:
        return jsonify({'erro': f'Erro GPT: {e}'}), 400


# ===== ERROS =====
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", mensagem="Página não encontrada."), 404


@app.errorhandler(500)
def erro_interno(e):
    return render_template(
        "error.html",
        mensagem="Erro interno do servidor. Tente novamente mais tarde."
    ), 500


# ===== EXECUTAR =====
if __name__ == '__main__':
    app.run(debug=True)
```
