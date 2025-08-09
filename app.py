import os
from flask import Flask
from dotenv import load_dotenv

# Carrega variáveis (no Render já vêm do ambiente; local usa .env)
load_dotenv()

# Infra do banco + blueprints
from db import init_db
from operacoes_automatico.rotas import bp_operacoes_auto
from painel_operacao.rotas import bp_painel_operacao
from usuarios.rotas_api import bp_api  # <- usamos este módulo novo

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Chave de sessão/flash (em produção vem do ENV)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave-super-secreta")

    # Cria tabelas se não existirem
    init_db()

    # Registra rotas/blueprints
    app.register_blueprint(bp_operacoes_auto)
    app.register_blueprint(bp_painel_operacao)
    app.register_blueprint(bp_api)

    @app.route("/")
    def index():
        return (
            "<h2>ClaraVerse rodando 💖</h2>"
            "<p>"
            "<a href='/operacoes_automatico/painel'>Painel Automático</a> | "
            "<a href='/painel/operacao'>Painel de Operação</a> | "
            "<a href='/usuario/configurar-api'>Configurar API da Corretora</a> | "
            "<a href='/usuario/testar-api'>Testar API / Enviar Ordem</a> | "
            "<a href='/usuario/historico'>Histórico</a>"
            "</p>"
        )

    return app

# Objeto WSGI para o gunicorn (Start Command: gunicorn app:app)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)