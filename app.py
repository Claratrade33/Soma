import os
from flask import Flask
from dotenv import load_dotenv

# carrega variáveis do Render/local
load_dotenv()

# >>> usamos a infra do db.py e os blueprints
from db import init_db
from operacoes_automatico.rotas import bp_operacoes_auto
from painel_operacao.rotas import bp_painel_operacao
from usuarios.rotas_api import bp_api

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave-super-secreta")

    # cria tabelas se não existirem
    init_db()

    # registra blueprints
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

# <<< linha importante pro gunicorn "app:app"
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)