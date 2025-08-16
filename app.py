from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os, importlib, json

from models import db, Usuario, BinanceKey
from crypto_utils import criptografar
from binance_client import get_client
from clarinha_ia import solicitar_analise_json
from tasks import start_auto_mode, stop_auto_mode

# Carrega .env local e, se existir, o Secret File do Render
load_dotenv(".env")
load_dotenv("/etc/secrets/.env")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "acessos.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # módulos com rotas (blueprints)
    modules = [
        "acessos","anjos","clientes","conectores","configuracao","comunicacao",
        "comando","conhecimento","documentos","estatisticas","estrategias",
        "executores","feedbacks","financeiro","guardian","historicos",
        "indicadores","inteligencia","inteligencia_financeira","infinity",
        "monitoramento","notificacoes","operacoes","operacoes_automatico",
        "oraculo","painel_operacao","previsoes","recompensas","recursos",
        "registro","resgates","rotas_publicas","servicos","sinais","tarefas",
        "treinamentos","tokens","usuarios","vendedores"
    ]
    for m in modules:
        try:
            mod = importlib.import_module(f"{m}.rotas")
            bp = getattr(mod, "bp", None)
            if bp and bp.name not in app.blueprints:
                app.register_blueprint(bp)
        except ImportError:
            pass

    def criar_admin():
        db.create_all()
        admin = Usuario.query.filter_by(usuario="admin").first()
        if not admin:
            senha_hash = generate_password_hash("claraverse2025")
            db.session.add(Usuario(usuario="admin", senha_hash=senha_hash))
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
            openai_key = request.form["openai_key"]
            testnet = request.form.get("testnet", "on") in ("on", "true", "1")

            api_key_enc = criptografar(api_key, usuario.usuario)
            api_secret_enc = criptografar(api_secret, usuario.usuario)
            openai_key_enc = criptografar(openai_key, usuario.usuario)

            if cred:
                cred.api_key = api_key_enc
                cred.api_secret = api_secret_enc
                cred.openai_key = openai_key_enc
                cred.testnet = testnet
            else:
                db.session.add(BinanceKey(
                    user_id=usuario.id,
                    api_key=api_key_enc,
                    api_secret=api_secret_enc,
                    openai_key=openai_key_enc,
                    testnet=testnet
                ))
            db.session.commit()
            flash("Chaves atualizadas!", "success")
            return redirect(url_for("painel_operacao.index"))
        return render_template("conectores/configurar_api.html", binance_key=cred)

    @app.route("/historico")
    @login_required
    def historico():
        if os.path.exists("orders.json"):
            with open("orders.json","r") as f:
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
            ordem = client.create_order(symbol="BTCUSDT", side=side, type="MARKET", quantity=quantidade)
            return jsonify({"status":"ok","order":ordem})
        except Exception as e:
            return str(e), 500

    @app.route("/sugestao_ia")
    @login_required
    def sugestao_ia():
        quantidade = request.args.get("quantidade","0.001")
        analise = solicitar_analise_json()
        texto = analise.get("sugestao","").lower()
        tipo = "compra" if "compra" in texto else ("venda" if "venda" in texto else None)
        return jsonify({"status":"ok" if tipo else "erro","tipo":tipo,"quantidade":quantidade,"analise":analise})

    @app.route("/modo_automatico", methods=["POST"])
    @login_required
    def modo_automatico():
        acao = request.form.get("acao")
        usuario = current_user.usuario
        if acao == "start":
            start_auto_mode(usuario)
        elif acao == "stop":
            stop_auto_mode(usuario)
        return jsonify({"status":"ok","acao":acao})

    return app

# >>> Deixa o app exposto para o Gunicorn <<<
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)