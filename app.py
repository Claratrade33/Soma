from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import json
from clarinha_ia import solicitar_analise_json
from models import db, Usuario, BinanceKey
from crypto_utils import criptografar
from binance_client import get_client
from tasks import start_auto_mode, stop_auto_mode

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

# Configuração do banco SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Criar banco e garantir admin
def criar_admin():
    db.create_all()
    admin = Usuario.query.filter_by(usuario="admin").first()
    if not admin:
        senha_hash = generate_password_hash("claraverse2025")
        novo_admin = Usuario(usuario="admin", senha_hash=senha_hash)
        db.session.add(novo_admin)
        db.session.commit()

with app.app_context():
    criar_admin()

@app.route("/")
def index():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return redirect(url_for("painel_operacao"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha_hash, senha):
            session["logado"] = True
            session["usuario"] = usuario
            return redirect(url_for("painel_operacao"))
        flash("Credenciais inválidas.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if Usuario.query.filter_by(usuario=usuario).first():
            flash("Usuário já existe.", "error")
        else:
            senha_hash = generate_password_hash(senha)
            novo_user = Usuario(usuario=usuario, senha_hash=senha_hash)
            db.session.add(novo_user)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/painel_operacao")
def painel_operacao():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return render_template("painel_operacao.html")


@app.route("/config_api", methods=["GET", "POST"])
def config_api():
    if not session.get("logado"):
        return redirect(url_for("login"))
    usuario = Usuario.query.filter_by(usuario=session["usuario"]).first()
    cred = BinanceKey.query.filter_by(user_id=usuario.id).first()
    if request.method == "POST":
        api_key = request.form["api_key"]
        api_secret = request.form["api_secret"]
        testnet = bool(request.form.get("testnet"))
        api_key_enc = criptografar(api_key, usuario.usuario)
        api_secret_enc = criptografar(api_secret, usuario.usuario)
        if cred:
            cred.api_key = api_key_enc
            cred.api_secret = api_secret_enc
            cred.testnet = testnet
        else:
            cred = BinanceKey(user_id=usuario.id, api_key=api_key_enc, api_secret=api_secret_enc, testnet=testnet)
            db.session.add(cred)
        db.session.commit()
        flash("Chaves atualizadas!", "success")
        return redirect(url_for("painel_operacao"))
    return render_template("config_api.html", binance_key=cred)


@app.route("/historico")
def historico():
    if not session.get("logado"):
        return jsonify([]), 401
    if os.path.exists("orders.json"):
        with open("orders.json", "r") as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

@app.route("/executar_ordem", methods=["POST"])
def executar_ordem():
    if not session.get("logado"):
        return "Não autenticado", 401
    tipo = request.form.get("tipo")
    quantidade = request.form.get("quantidade", "0.001")
    side = "BUY" if tipo == "compra" else "SELL"
    try:
        client = get_client(session["usuario"])
        ordem = client.create_order(symbol="BTCUSDT", side=side, type="MARKET", quantity=quantidade)
        return jsonify({"status": "ok", "order": ordem})
    except Exception as e:
        return str(e), 500


@app.route("/sugestao_ia")
def sugestao_ia():
    if not session.get("logado"):
        return jsonify({"status": "erro", "mensagem": "não autenticado"}), 401
    quantidade = request.args.get("quantidade", "0.001")
    analise = solicitar_analise_json()
    texto = analise.get("sugestao", "").lower()
    if "compra" in texto:
        tipo = "compra"
    elif "venda" in texto:
        tipo = "venda"
    else:
        tipo = None
    status = "ok" if tipo else "erro"
    return jsonify({"status": status, "tipo": tipo, "quantidade": quantidade, "analise": analise})


@app.route("/modo_automatico", methods=["POST"])
def modo_automatico():
    if not session.get("logado"):
        return jsonify({"erro": "não autenticado"}), 401
    acao = request.form.get("acao")
    usuario = session["usuario"]
    if acao == "start":
        start_auto_mode(usuario)
    elif acao == "stop":
        stop_auto_mode(usuario)
    return jsonify({"status": "ok", "acao": acao})

if __name__ == "__main__":
    app.run(debug=True)
