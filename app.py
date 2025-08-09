import os
import requests
from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

from db import init_db, SessionLocal
from models import Usuario
from operacoes_automatico.rotas import bp_operacoes_auto
from painel_operacao.rotas import bp_painel_operacao
from usuarios.rotas import bp as usuarios_bp
from usuarios.rotas_api import bp_api

# API pública simples para preço ao vivo (proxy da Binance)
bp_public = Blueprint("public_api", __name__)
@bp_public.route("/api/ticker")
def api_ticker():
    symbol = request.args.get("symbol", "BTCUSDT").upper()
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price",
                         params={"symbol": symbol}, timeout=5)
        r.raise_for_status()
        return jsonify({"ok": True, "symbol": symbol, "price": float(r.json()["price"])})
    except Exception as e:
        return jsonify({"ok": False, "symbol": symbol, "error": str(e)}), 502

def ensure_admin():
    with SessionLocal() as s:
        admin = s.query(Usuario).filter(Usuario.username == "admin").one_or_none()
        if not admin:
            admin = Usuario(
                username="admin",
                password_hash=generate_password_hash("Claraverse2025"),
                is_active=True
            )
            s.add(admin); s.commit()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave-super-secreta")

    init_db()
    ensure_admin()

    login_manager = LoginManager()
    login_manager.login_view = "usuarios.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with SessionLocal() as s:
            return s.get(Usuario, int(user_id))

    app.register_blueprint(usuarios_bp, url_prefix="/usuario")
    app.register_blueprint(bp_operacoes_auto)
    app.register_blueprint(bp_painel_operacao)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_public)  # /api/ticker

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/painel")
    @login_required
    def painel_redirect():
        return redirect(url_for("painel_operacao.painel_operacao"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)