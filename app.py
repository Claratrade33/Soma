import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "claraverse_secret_2025")

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
FERNET_KEY_FILE = os.path.join(BASE_DIR, "fernet.key")

# Geração/Carregamento da chave Fernet
if os.path.exists(FERNET_KEY_FILE):
    key = open(FERNET_KEY_FILE, "rb").read()
else:
    key = Fernet.generate_key()
    with open(FERNET_KEY_FILE, "wb") as f:
        f.write(key)
fernet = Fernet(key)

def encrypt(text): return fernet.encrypt(text.encode()).decode()
def decrypt(text): return fernet.decrypt(text.encode()).decode()

def load_users():
    if not os.path.exists(USERS_FILE): return []
    with open(USERS_FILE, "r") as f: return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f, indent=2)

def find_user(username):
    users = load_users()
    for u in users:
        if "usuario" in u and decrypt(u["usuario"]) == username:
            return u
    return None

# Cria admin fixo
def criar_admin_default():
    users = load_users()
    for u in users:
        if decrypt(u["usuario"]) == "admin": return
    users.append({
        "usuario": encrypt("admin"),
        "senha": encrypt("claraverse2025"),
        "email": encrypt("admin@claraverse.com"),
        "binance_key": "",
        "binance_secret": "",
        "openai_key": ""
    })
    save_users(users)
criar_admin_default()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        user = find_user(usuario)
        if user and decrypt(user["senha"]) == senha:
            session["usuario"] = usuario
            return redirect(url_for("painel_operacao"))
        flash("Usuário ou senha inválidos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    if request.method == "POST":
        bin_key    = request.form.get("binance_api_key", "").strip()
        bin_secret = request.form.get("binance_api_secret", "").strip()
        oaikey     = request.form.get("openai_api_key", "").strip()
        updated = False
        if bin_key and bin_secret:
            user["binance_key"] = encrypt(bin_key)
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
        "openai_api_key": decrypt(user["openai_key"]) if user.get("openai_key") else "",
    })

@app.route("/painel_operacao", methods=["GET", "POST"])
def painel_operacao():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    saldo_btc = "0"
    saldo_usdt = "0"
    error_msg = ""
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
            error_msg = f"Erro ao consultar saldo Binance: {e}"
    return render_template("painel_operacao.html",
        user={"username": username},
        saldo_btc=saldo_btc, saldo_usdt=saldo_usdt, error_msg=error_msg
    )

# Executa ordem (buy/sell) real via API
@app.route("/executar_ordem", methods=["POST"])
def executar_ordem():
    if not session.get("usuario"):
        return "Não autenticado", 401
    tipo = request.form.get("tipo")
    quantidade = request.form.get("quantidade")
    symbol = request.form.get("symbol", "BTCUSDT")
    username = session["usuario"]
    user = find_user(username)
    if not (user.get("binance_key") and user.get("binance_secret")):
        return "API não configurada", 400
    try:
        from binance.client import Client
        client = Client(
            decrypt(user["binance_key"]),
            decrypt(user["binance_secret"])
        )
        if tipo == "compra":
            order = client.order_market_buy(symbol=symbol, quantity=float(quantidade))
        elif tipo == "venda":
            order = client.order_market_sell(symbol=symbol, quantity=float(quantidade))
        else:
            return "Tipo inválido", 400
        return json.dumps({"status": "ok", "order": order}), 200
    except Exception as e:
        return f"Erro ao executar ordem: {e}", 500

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("error.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)