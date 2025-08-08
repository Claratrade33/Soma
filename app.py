from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import json

from clarinha_ia import solicitar_analise_json
from models import db, Usuario, BinanceKey
from crypto_utils import criptografar
from binance_client import get_client
from tasks import start_auto_mode, stop_auto_mode

# Importe cada blueprint apenas uma vez
from acessos import bp as acessos_bp
from clientes import bp as clientes_bp
from conectores import bp as conectores_bp
from configuracao import bp as configuracao_bp
from painel_operacao import bp as painel_operacao_bp
from resgates import bp as resgates_bp
from inteligencia_financeira import bp as inteligencia_financeira_bp
from operacoes import bp as operacoes_bp
from tokens import bp as tokens_bp
from usuarios import bp as usuarios_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

# Configuração do banco SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "acessos.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registre os blueprints (uma única vez cada)
app.register_blueprint(acessos_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(conectores_bp)
app.register_blueprint(configuracao_bp)
app.register_blueprint(painel_operacao_bp)
app.register_blueprint(inteligencia_financeira_bp)
app.register_blueprint(tokens_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(operacoes_bp)
app.register_blueprint(resgates_bp)

# Função para criar banco de dados e usuário admin, se necessário
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
    if current_user.is_authenticated:
        return redirect(url_for("painel_operacao.index"))
    return redirect(url_for("acessos.login"))

@app.route("/config_api", methods=["GET", "POST"])
@login_required
def config_api():
    usuario = current_user
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
            cred = BinanceKey(
                user_id=usuario.id,
                api_key=api_key_enc,
                api_secret=api_secret_enc,
                testnet=testnet,
            )
            db.session.add(cred)
        db.session.commit()
        flash("Chaves atualizadas!", "success")
        return redirect(url_for("painel_operacao.index"))
    return render_template("conectores/configurar_api.html", binance_key=cred)

@app.route("/historico")
@login_required
def historico():
    if os.path.exists("orders.json"):
        with open("orders.json", "r") as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

@app.route("/executar_ordem", methods=["POST"])
@login_required
def executar_ordem():
    tipo = request.form.get("tipo")
    quantidade = request.form.get("quantidade", "0.001")
    side = "BUY" if tipo == "compra" else "SELL"
    try:
        client = get_client(current_user.usuario)
        ordem = client.create_order(
            symbol="BTCUSDT", side=side, type="MARKET", quantity=quantidade
        )
        return jsonify({"status": "ok", "order": ordem})
    except Exception as e:
        return str(e), 500

@app.route("/sugestao_ia")
@login_required
def sugestao_ia():
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
    return jsonify({
        "status": status,
        "tipo": tipo,
        "quantidade": quantidade,
        "analise": analise,
    })

@app.route("/modo_automatico", methods=["POST"])
@login_required
def modo_automatico():
    acao = request.form.get("acao")
    usuario = current_user.usuario
    if acao == "start":
        start_auto_mode(usuario)
    elif acao == "stop":
        stop_auto_mode(usuario)
    return jsonify({"status": "ok", "acao": acao})

if __name__ == "__main__":
    app.run(debug=True)
