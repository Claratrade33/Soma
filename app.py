import os, base64, requests
from flask import Flask, render_template, redirect, url_for, Blueprint, jsonify, request
from flask_login import LoginManager, login_required
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

from db import init_db, SessionLocal
from models import Usuario

# blueprints do projeto (NOMES CERTOS)
from usuarios.rotas import bp as usuarios_bp
from operacoes_automatico.rotas import bp_operacoes_auto
from painel_operacao.rotas import bp_painel_operacao

# ---------- API pública (preço vivo) ----------
bp_public = Blueprint("public_api", __name__)

@bp_public.route("/api/ticker")
def api_ticker():
    symbol = request.args.get("symbol", "BTCUSDT").upper()
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )
        r.raise_for_status()
        return jsonify({"ok": True, "symbol": symbol, "price": float(r.json()["price"])})
    except Exception as e:
        return jsonify({"ok": False, "symbol": symbol, "error": str(e)}), 502


# ---------- helpers ----------
def ensure_admin():
    """Cria usuário admin (admin / Claraverse2025) se não existir."""
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

def validate_fernet_env() -> tuple[bool, str]:
    """Valida FERNET_KEY no ambiente (32 bytes base64 url-safe)."""
    key = os.getenv("FERNET_KEY", "").strip()
    if not key:
        return False, "FERNET_KEY ausente. Defina no Render (Environment Variables)."
    try:
        raw = base64.urlsafe_b64decode(key.encode())
        if len(raw) != 32:
            return False, "FERNET_KEY inválida (tamanho diferente de 32 bytes)."
        return True, ""
    except Exception as e:
        return False, f"FERNET_KEY inválida: {e}"

def _mount_config_error_routes(app: Flask, message: str):
    """Rota de diagnóstico quando a FERNET_KEY/Corretora não carrega."""
    @app.route("/_config_error")
    def _config_error():
        tips = (
            "<h3>Configuração pendente</h3>"
            f"<p><b>Erro:</b> {message}</p>"
            "<p>Como corrigir no Render → Settings → Environment:</p>"
            "<ol>"
            "<li>Remova a variável <code>FERNET_KEY</code> antiga (se houver).</li>"
            "<li>Adicione <b>FERNET_KEY</b> com uma chave Fernet válida (44 chars e termina com '=').</li>"
            "<li>Salve e faça <b>Manual Deploy → Deploy latest commit</b>.</li>"
            "</ol>"
            "<p>Depois, acesse <code>/usuario/configurar-api</code> para salvar suas credenciais.</p>"
        )
        return tips, 503


# ---------- app factory ----------
def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave-super-secreta")

    # Banco + admin
    init_db()
    ensure_admin()

    # Login
    login_manager = LoginManager()
    login_manager.login_view = "usuarios.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with SessionLocal() as s:
            return s.get(Usuario, int(user_id))

    # Blueprints sempre ativos
    app.register_blueprint(usuarios_bp, url_prefix="/usuario")  # /usuario/login, /usuario/logout
    app.register_blueprint(bp_operacoes_auto)                   # /operacoes_automatico/...
    app.register_blueprint(bp_painel_operacao)                  # /painel/operacao
    app.register_blueprint(bp_public)                           # /api/ticker

    # Tenta registrar a API da corretora (depende de FERNET_KEY válida)
    ok, msg = validate_fernet_env()
    if ok:
        try:
            from usuarios.rotas_api import bp_api
            app.register_blueprint(bp_api)  # /usuario/configurar-api, /usuario/testar-api, /usuario/historico
        except Exception as e:
            _mount_config_error_routes(app, f"Falha ao carregar rotas da corretora: {e}")
            # Fallbacks para não dar 404
            app.add_url_rule("/usuario/configurar-api", endpoint="fallback_cfg",
                             view_func=lambda: redirect("/_config_error"))
            app.add_url_rule("/usuario/testar-api", endpoint="fallback_test",
                             view_func=lambda: redirect("/_config_error"))
            app.add_url_rule("/usuario/historico", endpoint="fallback_hist",
                             view_func=lambda: redirect("/_config_error"))
    else:
        _mount_config_error_routes(app, msg)
        # Fallbacks para não dar 404
        app.add_url_rule("/usuario/configurar-api", endpoint="fallback_cfg_noenv",
                         view_func=lambda: redirect("/_config_error"))
        app.add_url_rule("/usuario/testar-api", endpoint="fallback_test_noenv",
                         view_func=lambda: redirect("/_config_error"))
        app.add_url_rule("/usuario/historico", endpoint="fallback_hist_noenv",
                         view_func=lambda: redirect("/_config_error"))

    # Index = tela de login
    @app.route("/")
    def index():
        return render_template("index.html")

    # Atalho de painel (exige login)
    @app.route("/painel")
    @login_required
    def painel_redirect():
        return redirect(url_for("painel_operacao.painel_operacao"))

    # Diagnóstico: lista endpoints
    @app.route("/_routes")
    def _routes():
        return "<pre>" + "\n".join(sorted(app.view_functions.keys())) + "</pre>"

    return app


# WSGI para o Render
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)