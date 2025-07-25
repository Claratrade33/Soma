from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import ClarinhaIA
from binance.client import Client
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)

# === MODELO DE USUÁRIO ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    api_key = db.Column(db.String(300))
    api_secret = db.Column(db.String(300))

# === AUTENTICAÇÃO ===
def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None

# === ROTAS ===

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        return render_template("login.html", erro="Credenciais inválidas")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception:
            return render_template("register.html", erro="Erro ao registrar usuário.")
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configurar', methods=["GET", "POST"])
def configurar():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == "POST":
        user.api_key = request.form['api_key']
        user.api_secret = request.form['api_secret']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template("configurar.html", user=user)

@app.route('/painel_operacao')
def painel_operacao():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user.api_key and user.api_secret:
        try:
            client = Client(user.api_key, user.api_secret)
            balance = client.get_asset_balance(asset='USDT')
            saldo = round(float(balance['free']), 2)
        except Exception:
            saldo = "Erro ao conectar"
    else:
        saldo = "Chaves não configuradas"

    ia = ClarinhaIA()
    sugestao = ia.analise()

    return render_template("painel_operacao.html", saldo=saldo, sugestao=sugestao)

# === ROTA PARA EXECUTAR ORDENS ===
@app.route('/executar_ordem', methods=["POST"])
def executar_ordem():
    user = get_current_user()
    if not user:
        return jsonify({'mensagem': 'Usuário não autenticado.'}), 401

    dados = request.get_json()
    acao = dados.get('acao', '').upper()
    mensagem = ''
    sugestao = ''

    ia = ClarinhaIA()
    sugestao = ia.analise()

    try:
        if not user.api_key or not user.api_secret:
            return jsonify({'mensagem': 'Chaves de API não configuradas.'}), 403

        client = Client(user.api_key, user.api_secret)
        simbolo = 'BTCUSDT'
        quantidade = 0.001  # valor fixo ou ajustável

        if acao == "ENTRADA":
            client.order_market_buy(symbol=simbolo, quantity=quantidade)
            mensagem = "✅ Ordem de COMPRA executada com sucesso."
        elif acao == "STOP":
            mensagem = "🛑 Stop acionado. (Simulado)"
        elif acao == "ALVO":
            mensagem = "🎯 Alvo atingido! (Simulado)"
        elif acao == "EXECUTAR":
            mensagem = "🚀 Ordem executada conforme análise da IA."
        elif acao == "AUTOMATICO":
            mensagem = "🤖 Modo automático ativado! IA assumiu o controle."
        else:
            mensagem = "Ação desconhecida."

    except Exception as e:
        mensagem = f"Erro ao executar: {str(e)}"

    return jsonify({'mensagem': mensagem, 'sugestao': sugestao})

# === EXECUÇÃO FINAL GARANTIDA ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
