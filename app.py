import os
import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from clarinha_core import clarinha_responder
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_super_secreta_local")

# Diretórios e arquivos de configuração
BASE_DIR    = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "user_configs.json")
KEY_FILE    = os.path.join(BASE_DIR, "fernet.key")

# Inicializa chave de encriptação (gera se não existir)
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
fernet = Fernet(key)

def criptografar(text: str) -> str:
    """Encripta texto e retorna string base64."""
    return fernet.encrypt(text.encode()).decode()

def load_configs() -> dict:
    """Carrega configurações do JSON, retorna {} se não existir."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_configs(configs: dict):
    """Salva todas as configurações no arquivo JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        pergunta     = request.form.get("pergunta", "")
        simbolo      = request.form.get("simbolo", "BTCUSDT")
        gerar_imagem = request.form.get("imagem") == "on"
        resultado    = clarinha_responder(pergunta, simbolo, gerar_imagem)
    return render_template("index.html", resultado=resultado)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha   = request.form.get("senha")
        # TODO: usar validação em banco de dados real
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
        # TODO: inserir novo usuário no DB
        flash("Cadastro concluído! Agora faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if not session.get("usuario"):
        return redirect(url_for("login"))

    usuario    = session["usuario"]
    configs    = load_configs()
    user_conf  = configs.get(usuario, {})

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

    # No GET, apenas renderiza form (podemos mostrar placeholders se já configurado)
    return render_template(
        "configurar.html",
        has_binance = "binance_key" in user_conf,
        has_openai  = "openai_key" in user_conf
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
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host=host, port=port)
