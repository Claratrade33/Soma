import os
from flask import Flask, render_template, redirect
from flask_login import LoginManager
from dotenv import load_dotenv
from usuarios.rotas_usuario import bp_usuarios
from painel.rotas_painel import bp_painel

load_dotenv()

# -------------------
# Validação FERNET_KEY
# -------------------
from services.crypto import validate_fernet_env

def _mount_config_error_routes(app, msg):
    @app.route("/_config_error")
    def _config_error():
        return render_template("config_error.html", mensagem=msg)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "default-secret")

# Login manager
login_manager = LoginManager()
login_manager.login_view = "usuarios.login"
login_manager.init_app(app)

# Blueprints básicos
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_painel)

# -------------------
# Rotas API/Corretora
# -------------------
ok, msg = validate_fernet_env()
if ok:
    try:
        from usuarios.rotas_api import bp_api
        app.register_blueprint(bp_api)  # /usuario/configurar-api, etc
    except Exception as e:
        _mount_config_error_routes(app, f"Falha ao carregar rotas da corretora: {e}")
        # Fallbacks para evitar 404
        app.add_url_rule("/usuario/configurar-api", view_func=lambda: redirect("/_config_error"))
        app.add_url_rule("/usuario/testar-api", view_func=lambda: redirect("/_config_error"))
        app.add_url_rule("/usuario/historico", view_func=lambda: redirect("/_config_error"))
else:
    _mount_config_error_routes(app, msg)
    app.add_url_rule("/usuario/configurar-api", view_func=lambda: redirect("/_config_error"))
    app.add_url_rule("/usuario/testar-api", view_func=lambda: redirect("/_config_error"))
    app.add_url_rule("/usuario/historico", view_func=lambda: redirect("/_config_error"))

# -------------------
# Rotas principais
# -------------------
@app.route("/")
def index():
    return render_template("index.html")

# Debug: lista todas rotas
@app.route("/_routes")
def listar_rotas():
    links = []
    for rule in app.url_map.iter_rules():
        links.append(f"{rule.endpoint} -> {rule.rule}")
    return "<br>".join(links)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))