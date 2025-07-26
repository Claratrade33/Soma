import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import gerar_sugestao_ia
from binance.client import Client

# === Inicialização do App ===
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)

db = SQLAlchemy(app)

# === Modelo de Usuário ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

# === Rota Inicial ===
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel_operacao'))
    return redirect(url_for('login'))

# === Login ===
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash("Login inválido.")
    return render_template("login.html")

# === Registro ===
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        if User.query.filter_by(email=email).first():
            flash("Email já registrado.")
        else:
            user = User(email=email, senha=senha)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html")

# === Configurar Chaves ===
@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if request.method == "POST":
        session['binance_key'] = request.form['binance_key']
        session['binance_secret'] = request.form['binance_secret']
        session['openai_key'] = request.form['openai_key']
        return redirect(url_for("painel_operacao"))
    return render_template("configurar.html")

# === Painel Operação ===
@app.route("/painel_operacao")
def painel_operacao():
    if 'user_id' not in session:
        return redirect(url_for("login"))

    binance_key = session.get("binance_key")
    binance_secret = session.get("binance_secret")
    openai_key = session.get("openai_key")

    if not binance_key or not binance_secret or not openai_key:
        return redirect(url_for("configurar"))

    try:
        client = Client(binance_key, binance_secret)
        saldo = client.get_asset_balance(asset='USDT')
        saldo_real = round(float(saldo['free']), 2)
    except Exception:
        saldo_real = "Erro"

    try:
        sugestao = gerar_sugestao_ia(openai_key)
    except:
        sugestao = {"sinal": "Erro", "confianca": 0, "stop": 0, "alvo": 0}

    return render_template("painel_operacao.html", saldo=saldo_real, sugestao=sugestao)

# === Executar Ordem ===
@app.route("/executar_ordem", methods=["POST"])
def executar_ordem():
    if 'user_id' not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 403

    tipo = request.json.get("tipo")
    if tipo not in ['entrada', 'stop', 'alvo', 'automatico']:
        return jsonify({"erro": "Tipo inválido"}), 400

    # Aqui pode adicionar lógica real de execução (ex: Binance)
    return jsonify({"mensagem": f"Ação '{tipo}' executada com sucesso."})

# === Logout ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# === Criar Banco ===
with app.app_context():
    db.create_all()
