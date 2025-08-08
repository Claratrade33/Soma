from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import importlib

from models import db, Usuario, BinanceKey
from crypto_utils import criptografar
from binance_client import get_client
from clarinha_ia import solicitar_analise_json
from tasks import start_auto_mode, stop_auto_mode

load_dotenv()

def create_app():
    """Cria e configura a aplicação Flask, registrando todos os blueprints disponíveis."""
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")
    # Banco de dados SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "acessos.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Lista de módulos que possuem rotas a serem registradas
    modules = [
        "acessos", "anjos", "clientes", "conectores", "configuracao",
        "comunicacao", "comando", "conhecimento", "documentos",
        "estatisticas", "estrategias", "executores", "feedbacks",
        "financeiro", "guardian", "historicos", "indicadores",
        "inteligencia", "inteligencia_financeira", "infinity",
        "monitoramento", "notificacoes", "operacoes",
        "operacoes_automatico", "oraculo", "painel_operacao",
        "previsoes", "recompensas", "recursos", "registro",
        "resgates", "rotas_publicas", "servicos", "sinais",
        "tarefas", "treinamentos", "tokens", "usuarios", "vendedores"
    ]

    # Importa e registra cada blueprint encontrado
    for module_name in modules:
        try:
            module = importlib.import_module(f"{module_name}.rotas")
            bp = getattr(module, "bp", None)
            if bp and bp.name not in app.blueprints:
                app.register_blueprint(bp)
        except ImportError:
            # Caso o módulo não exista ou não possua rotas, segue para o próximo
            continue

    # Criação do usuário admin caso ainda não exista
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
        """Redireciona para o painel de operações se o usuário estiver logado."""
        if current_user.is_authenticated:
            return redirect(url_for("painel_operacao.index"))
        return redirect(url_for("acessos.login"))

    @app.route("/config_api", methods=["GET", "POST"])
    @login_required
    def config_api():
        """Exibe e processa o formulário para configurar Binance e OpenAI."""
        usuario = current_user
        cred = BinanceKey.query.filter_by(user_id=usuario.id).first()
        if request.method == "POST":
            api_key = request.form["api_key"]
            api_secret = request.form["api_secret"]
            openai_key = request.form["openai_key"]
            testnet = bool(request.form.get("testnet"))

            api_key_enc = criptografar(api_key, usuario.usuario)
            api_secret_enc = criptografar(api_secret, usuario.usuario)
            openai_key_enc = criptografar(openai_key, usuario.usuario)

            if cred:
                cred.api_key = api_key_enc
                cred.api_secret = api_secret_enc
                cred.openai_key = openai_key_enc
                cred.testnet = testnet
            else:
                cred = BinanceKey(
                    user_id=usuario.id,
                    api_key=api_key_enc,
                    api_secret=api_secret_enc,
                    openai_key=openai_key_enc,
                    testnet=testnet
                )
                db.session.add(cred)

            db.session.commit()
            flash("Chaves atualizadas!", "success")
            return redirect(url_for("painel_operacao.index"))

        return render_template("conectores/configurar_api.html", binance_key=cred)

    @app.route("/historico")
    @login_required
    def historico():
        """Retorna o histórico de ordens em formato JSON."""
        if os.path.exists("orders.json"):
            with open("orders.json", "r") as f:
                data = json.load(f)
        else:
            data = []
        return jsonify(data)

    @app.route("/executar_ordem", methods=["POST"])
    @login_required
    def executar_ordem():
        """Executa uma ordem de compra ou venda na Binance."""
        tipo = request.form.get("tipo")
        quantidade = request.form.get("quantidade", "0.001")
        side = "BUY" if tipo == "compra" else "SELL"
        try:
            client = get_client(current_user.usuario)
            ordem = client.create_order(
                symbol="BTCUSDT",
                side=side,
                type="MARKET",
                quantity=quantidade
            )
            return jsonify({"status": "ok", "order": ordem})
        except Exception as e:
            return str(e), 500

    @app.route("/sugestao_ia")
    @login_required
    def sugestao_ia():
        """Retorna sugestão gerada pela IA e classifica como compra/venda."""
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
        """Ativa ou desativa o modo automático de operações."""
        acao = request.form.get("acao")
        usuario_id = current_user.usuario
        if acao == "start":
            start_auto_mode(usuario_id)
        elif acao == "stop":
            stop_auto_mode(usuario_id)
        return jsonify({"status": "ok", "acao": acao})

    return app

if __name__ == "__main__":
    # Inicializa a app e executa em modo debug
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
