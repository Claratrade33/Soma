from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from clarinha_ia import solicitar_analise_json
from binance_trade import executar_ordem as executar_ordem_binance

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

# Configuração do banco SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

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
        resultado = executar_ordem_binance("BTCUSDT", side, quantidade)
        ordem = {
            "tipo": tipo,
            "ativo": "BTCUSDT",
            "valor": quantidade,
            "preco": resultado.get("fills", [{}])[0].get("price", "0"),
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if os.path.exists("orders.json"):
            with open("orders.json", "r") as f:
                historico = json.load(f)
        else:
            historico = []
        historico.append(ordem)
        with open("orders.json", "w") as f:
            json.dump(historico, f, indent=2)
        return jsonify({"status": "ok"})
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
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
