import os
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_required, current_user

load_dotenv()

from db import init_db, SessionLocal
from models import Usuario
from operacoes_automatico.rotas import bp_operacoes_auto
from painel_operacao.rotas import bp_painel_operacao
from usuarios.rotas import bp as usuarios_bp   # login/cadastro/logout
from usuarios.rotas_api import bp_api          # API da corretora + ordens

from werkzeug.security import generate_password_hash

def ensure_admin():
    """Cria o usuário admin com senha Claraverse2025 se não existir."""
    with SessionLocal() as s:
        admin = s.query(Usuario).filter(Usuario.username == "admin").one_or_none()
        if not admin:
            admin = Usuario(
                username="admin",
                password_hash=generate_password_hash("Claraverse2025"),
                is_active=True
            )
            s.add(admin)
            s.commit()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave-super-secreta")

    # DB: cria tabelas
    init_db()
    ensure_admin()

    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "usuarios.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with SessionLocal() as s:
            return s.get(Usuario, int(user_id))

    # Blueprints
    app.register_blueprint(usuarios_bp, url_prefix="/usuario")        # /usuario/login, /usuario/logout
    app.register_blueprint(bp_operacoes_auto)                         # /operacoes_automatico/...
    app.register_blueprint(bp_painel_operacao)                        # /painel/operacao
    app.register_blueprint(bp_api)                                    # /usuario/configurar-api, /usuario/testar-api, etc.

    # INDEX = Login (tela inicial)
    @app.route("/")
    def index():
        # Renderiza o formulário de login diretamente
        return render_template("index.html")

    # Rota “atalho” para o painel (exige login)
    @app.route("/painel")
    @login_required
    def painel_redirect():
        return redirect(url_for("painel_operacao.painel_operacao"))

    return app

# WSGI para Render (gunicorn app:app)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)