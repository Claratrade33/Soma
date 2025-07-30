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
    jsonify,
)
from cryptography.fernet import Fernet

# -------- Logger --------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("Iniciando ClaraVerse app.py")

# -------- App & Configs --------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_super_secreta_local")

BASE_DIR    = os.path.dirname(__file__)
USERS_FILE  = os.path.join(BASE_DIR, "users.json")
KEY_FILE    = os.path.join(BASE_DIR, "fernet.key")

# Gera ou carrega chave Fernet
if os.path.exists(KEY_FILE):
    key = open(KEY_FILE, "rb").read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
fernet = Fernet(key)

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(text: str) -> str:
    return fernet.decrypt(text.encode()).decode()

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def find_user(username):
    users = load_users()
    for u in users:
        if "usuario" in u and decrypt(u["usuario"]) == username:
            return u
    return None

# -------- Criação automática do admin --------
def criar_admin_default():
    users = load_users()
    for u in users:
        if decrypt(u["usuario"]) == "admin":
            return
    admin_user = {
        "usuario": encrypt("admin"),
        "senha": encrypt("Bubi"),
        "email": encrypt("admin@clara.verse"),
        "binance_key": "",
        "binance_secret": "",
        "openai_key": ""
    }
    users.append(admin_user)
    save_users(users)
criar_admin_default()

# -------- Rotas --------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha   = request.form.get("senha")
        user = find_user(usuario)
        if user and decrypt(user["senha"]) == senha:
            session["usuario"] = usuario
            flash("Login realizado com sucesso!", "success")
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
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        if not username or not password or not email or not confirm:
            flash("Preencha todos os campos.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("As senhas não coincidem.", "danger")
            return render_template("register.html")
        if find_user(username):
            flash("Usuário já existe.", "danger")
            return render_template("register.html")
        # Checa se o e-mail já existe
        users = load_users()
        for u in users:
            if "email" in u and decrypt(u["email"]) == email:
                flash("Este email já está cadastrado.", "danger")
                return render_template("register.html")
        new_user = {
            "usuario": encrypt(username),
            "senha": encrypt(password),
            "email": encrypt(email),
            "binance_key": "",
            "binance_secret": "",
            "openai_key": ""
        }
        users.append(new_user)
        save_users(users)
        flash("Cadastro realizado! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    if request.method == "POST":
        bin_key    = request.form.get("binance_api_key", "").strip()
        bin_secret = request.form.get("binance_api_secret", "").strip()
        oaikey     = request.form.get("gpt_api_key", "").strip()
        updated = False
        if bin_key:
            user["binance_key"] = encrypt(bin_key)
            updated = True
        if bin_secret:
            user["binance_secret"] = encrypt(bin_secret)
            updated = True
        if oaikey:
            user["openai_key"] = encrypt(oaikey)
            updated = True
        if updated:
            users = load_users()
            for idx, u in enumerate(users):
                if decrypt(u["usuario"]) == username:
                    users[idx] = user
            save_users(users)
            flash("Chaves salvas com sucesso!", "success")
            return redirect(url_for("painel_operacao"))
        else:
            flash("Preencha todos os campos de chave!", "danger")
    return render_template("configurar.html", user={
        "binance_api_key": decrypt(user["binance_key"]) if user.get("binance_key") else "",
        "binance_api_secret": decrypt(user["binance_secret"]) if user.get("binance_secret") else "",
        "gpt_api_key": decrypt(user["openai_key"]) if user.get("openai_key") else "",
    })

@app.route("/painel_operacao")
def painel_operacao():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    saldo_btc = "0"
    saldo_usdt = "0"
    # Só consulta a Binance se o usuário tiver chave salva!
    if user.get("binance_key") and user.get("binance_secret"):
        try:
            from binance.client import Client
            client = Client(
                decrypt(user["binance_key"]),
                decrypt(user["binance_secret"])
            )
            account = client.get_account()
            for b in account["balances"]:
                if b["asset"] == "BTC":
                    saldo_btc = b["free"]
                if b["asset"] == "USDT":
                    saldo_usdt = b["free"]
        except Exception as e:
            flash(f"Erro ao consultar saldo Binance: {e}", "danger")
    return render_template("painel_operacao.html", user={
        "username": username,
        "email": decrypt(user["email"]) if user.get("email") else ""
    }, saldo_btc=saldo_btc, saldo_usdt=saldo_usdt)

@app.route('/executar_ordem', methods=['POST'])
def executar_ordem():
    if not session.get("usuario"):
        return jsonify({"mensagem": "Não autenticado"}), 403
    user = find_user(session["usuario"])
    if not (user and user.get("binance_key") and user.get("binance_secret")):
        return jsonify({"mensagem": "Chaves Binance não configuradas!"}), 400

    data = request.json
    tipo_ordem = data.get('tipo_ordem')  # 'compra' ou 'venda'
    simbolo = data.get('simbolo', 'BTCUSDT')
    quantidade = data.get('quantidade', '0.001')
    try:
        from binance.client import Client
        client = Client(decrypt(user["binance_key"]), decrypt(user["binance_secret"]))
        if tipo_ordem == 'compra':
            order = client.create_order(
                symbol=simbolo,
                side='BUY',
                type='MARKET',
                quantity=float(quantidade)
            )
            return jsonify({"mensagem": f"Compra executada com sucesso! Ordem: {order['orderId']}"})
        elif tipo_ordem == 'venda':
            order = client.create_order(
                symbol=simbolo,
                side='SELL',
                type='MARKET',
                quantity=float(quantidade)
            )
            return jsonify({"mensagem": f"Venda executada com sucesso! Ordem: {order['orderId']}"})
        else:
            return jsonify({"mensagem": "Tipo de ordem inválido"}), 400
    except Exception as e:
        return jsonify({"mensagem": f"Erro na execução: {str(e)}"}), 500

@app.route('/sugestao_gpt', methods=['POST'])
def sugestao_gpt():
    if not session.get("usuario"):
        return jsonify({"erro": "Não autenticado"}), 403
    user = find_user(session["usuario"])
    if not user.get("openai_key"):
        return jsonify({"erro": "Chave OpenAI não configurada!"}), 400

    data = request.json
    prompt = data.get("prompt", "Dê uma sugestão de operação para BTC/USDT.")
    try:
        import openai
        openai.api_key = decrypt(user["openai_key"])
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=100
        )
        sugestao = completion.choices[0].message.content
        return jsonify({"sugestao": sugestao})
    except Exception as e:
        return jsonify({"erro": f"Erro na IA: {str(e)}"}), 500

@app.route("/icons")
def icons():
    return render_template("icons.html")

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("error.html"), 404

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Iniciando servidor dev em {host}:{port}")
    app.run(debug=True, host=host, port=port)
