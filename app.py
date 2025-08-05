import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from crypto_utils import criptografar, descriptografar

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "claraverse_secret_2025")

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

def load_users():
    if not os.path.exists(USERS_FILE): return []
    with open(USERS_FILE, "r") as f: return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f, indent=2)

def load_orders():
    if not os.path.exists(ORDERS_FILE): return []
    with open(ORDERS_FILE, "r") as f: return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f: json.dump(orders, f, indent=2)

def find_user(username):
    users = load_users()
    for u in users:
        try:
            if "usuario" in u and descriptografar(u["usuario"], "admin") == username:
                return u
        except:
            continue
    return None

def criar_admin_default():
    users = load_users()
    for u in users:
        try:
            if descriptografar(u["usuario"], "admin") == "admin":
                return
        except:
            continue
    users.append({
        "usuario": criptografar("admin", "admin"),
        "senha": criptografar("claraverse2025", "admin"),
        "email": criptografar("admin@claraverse.com", "admin"),
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
        if user:
            try:
                if descriptografar(user["senha"], usuario) == senha:
                    session["usuario"] = usuario
                    return redirect(url_for("painel_operacao"))
            except:
                pass
        flash("Usuário ou senha inválidos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
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
        users = load_users()
        for u in users:
            try:
                if "email" in u and descriptografar(u["email"], username) == email:
                    flash("Este email já está cadastrado.", "danger")
                    return render_template("register.html")
            except:
                continue
        users.append({
            "usuario": criptografar(username, username),
            "senha": criptografar(password, username),
            "email": criptografar(email, username),
            "binance_key": "",
            "binance_secret": "",
            "openai_key": ""
        })
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
        bin_key = request.form.get("binance_api_key", "").strip()
        bin_sec = request.form.get("binance_api_secret", "").strip()
        openai_key = request.form.get("openai_api_key", "").strip()
        if bin_key:
            user["binance_key"] = criptografar(bin_key, username)
        if bin_sec:
            user["binance_secret"] = criptografar(bin_sec, username)
        if openai_key:
            user["openai_key"] = criptografar(openai_key, username)
        users = load_users()
        for idx, u in enumerate(users):
            try:
                if descriptografar(u["usuario"], username) == username:
                    users[idx] = user
            except:
                continue
        save_users(users)
        flash("Chaves salvas com sucesso!", "success")
        return redirect(url_for("painel_operacao"))
    return render_template("configurar.html", user={
        "binance_api_key": descriptografar(user["binance_key"], username) if user.get("binance_key") else "",
        "binance_api_secret": descriptografar(user["binance_secret"], username) if user.get("binance_secret") else "",
        "openai_api_key": descriptografar(user["openai_key"], username) if user.get("openai_key") else "",
    })

@app.route("/painel_operacao")
def painel_operacao():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    saldo_btc = "0"
    saldo_usdt = "0"
    saldo_futures_usdt = "0"
    error_msg = ""
    try:
        if user.get("binance_key") and user.get("binance_secret"):
            from binance.client import Client
            client = Client(
                descriptografar(user["binance_key"], username),
                descriptografar(user["binance_secret"], username)
            )
            account = client.get_account()
            for b in account["balances"]:
                if b["asset"] == "BTC":
                    saldo_btc = b["free"]
                if b["asset"] == "USDT":
                    saldo_usdt = b["free"]
            try:
                futures_balances = client.futures_account_balance()
                for f in futures_balances:
                    if f['asset'] == 'USDT':
                        saldo_futures_usdt = f['balance']
            except:
                saldo_futures_usdt = "N/A"
    except Exception as e:
        error_msg = f"Erro ao consultar saldo Binance: {e}"

    return render_template("painel_operacao.html", user={"username": username}, saldo_btc=saldo_btc, saldo_usdt=saldo_usdt, saldo_futures_usdt=saldo_futures_usdt, error_msg=error_msg)

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
            descriptografar(user["binance_key"], username),
            descriptografar(user["binance_secret"], username)
        )
        if tipo == "compra":
            order = client.order_market_buy(symbol=symbol, quantity=float(quantidade))
        elif tipo == "venda":
            order = client.order_market_sell(symbol=symbol, quantity=float(quantidade))
        else:
            return "Tipo inválido", 400
        preco = "N/A"
        try:
            if order.get("fills"):
                preco = order["fills"][0].get("price", "N/A")
        except Exception:
            pass
        orders = load_orders()
        orders.insert(0, {
            "tipo": "Compra" if tipo == "compra" else "Venda",
            "ativo": symbol,
            "valor": quantidade,
            "preco": preco,
            "hora": datetime.now().strftime("%H:%M")
        })
        save_orders(orders)
        return jsonify(status="ok", order=order), 200
    except Exception as e:
        return f"Erro ao executar ordem: {e}", 500

@app.route("/historico")
def historico():
    if not session.get("usuario"):
        return "Não autenticado", 401
    orders = load_orders()
    return jsonify(orders), 200

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("error.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)