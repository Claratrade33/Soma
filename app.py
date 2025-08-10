import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("SECRET_KEY", "dev-key")

    # ---- Blueprints (registram rotas). Se algum módulo faltar, o app não quebra.
    try:
        from usuarios.rotas_api import bp_api  # /usuario/...
        app.register_blueprint(bp_api)
        print("✔ Blueprint 'usuario_api' registrado")
    except Exception as e:
        print("⚠ Não registrou 'usuario_api':", e)

    try:
        from operacoes.rotas import bp_operacao  # /painel/operacao
        app.register_blueprint(bp_operacao)
        print("✔ Blueprint 'operacoes' registrado")
    except Exception as e:
        print("⚠ Não registrou 'operacoes':", e)

    try:
        from operacoes_automatico.rotas import bp_auto  # /operacoes_automatico/painel
        app.register_blueprint(bp_auto)
        print("✔ Blueprint 'operacoes_automatico' registrado")
    except Exception as e:
        print("⚠ Não registrou 'operacoes_automatico':", e)

    # ---- Home
    @app.route("/")
    def index():
        # Precisa existir templates/index.html. Se não existir, mostra um fallback simples.
        try:
            return render_template("index.html")
        except Exception:
            return "<h1>ClaraVerse</h1><p>App no ar. Crie templates/index.html.</p>"

    # ---- Diagnóstico: lista todas as rotas
    @app.route("/_routes")
    def _routes():
        rules = sorted([f"{r.rule}  →  {r.endpoint}" for r in app.url_map.iter_rules()])
        return "<pre>" + "\n".join(rules) + "</pre>"

    return app

# A instância que o gunicorn procura
app = create_app()