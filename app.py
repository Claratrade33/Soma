import os
import json
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from cryptography.fernet import Fernet

# -------- Logger --------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("Importando módulo app")

# -------- App & Configs --------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_super_secreta_local")

BASE_DIR    = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "user_configs.json")
KEY_FILE    = os.path.join(BASE_DIR, "fernet.key")

# Gera ou carrega chave Fernet
if os.path.exists(KEY_FILE):
    key = open(KEY_FILE, "rb").read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
fernet = Fernet(key)

def criptografar(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def load_configs() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_configs(configs: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)

# -------- Routes --------
@app.route("/health")
def health():
    return "OK", 200

@app.route("/", methods=["GET", "POST"])
def index():
    # lazy-load de clarinha_core
    from clarinha_core import clarinha_responder

    resultado = None
    if request.method == "POST":
        pergunta     = request.form.get("pergunta", "")
        simbolo      = request.form.get("simbolo", "BTCUSDT")
        gerar_imagem = request.form.get("imagem") == "on"

        logger.info(f"Recebida pergunta={pergunta!r}, símbolo={simbolo}, imagem={gerar_imagem}")
        resultado = clarinha_responder(pergunta, simbolo, gerar_imagem)

    return render_template("index.html", resultado=resultado)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha   = request.form.get("senha")
        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect(url_for("painel_operacao"))
        flash("Usuário ou senha inválidos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Você saiu da sua conta", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # TODO: Salvar usuário em banco
        flash("Cadastro concluído! Agora faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if not session.get("usuario"):
        return redirect(url_for("login"))

    usuario   = session["usuario"]
    configs   = load_configs()
    user_conf = configs.get(usuario, {})

    if request.method == "POST":
        bin_key    = request.form.get("binance_key", "").strip()
        bin_secret = request.form.get("binance_secret", "").strip()
        oaikey     = request.form.get("openai_key", "").strip()

        if bin_key and bin_secret:
            user_conf["binance_key"]    = criptografar(bin_key)
            user_conf["binance_secret"] = criptografar(bin_secret)

        if oaikey:
            user_conf["openai_key"] = criptografar(oaikey)

        configs[usuario] = user_conf
        save_configs(configs)

        flash("Chaves salvas com sucesso!", "success")
        return redirect(url_for("configurar"))

    return render_template(
        "configurar.html",
        has_binance = "binance_key" in user_conf,
        has_openai  = "openai_key" in user_conf,
    )

@app.route("/painel")
def painel_operacao():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    return render_template("painel_operacao.html")

@app.route("/icons")
def icons():
    return render_template("icons.html")

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("error.html"), 404

if __name__ == "__main__":
    # Só usado em dev. Gunicorn ignora esse bloco.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Iniciando servidor dev em {host}:{port}")
    app.run(debug=True, host=host, port=port)
