import os
import json
import logging
from cryptography.fernet import Fernet
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from binance.client import Client
import openai

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SomaApp")

# === CONFIGURAÇÕES ===
BASE_DIR    = os.path.dirname(__file__)
DATA_FILE   = os.path.join(BASE_DIR, "usuarios.dat")
FERNET_KEY  = os.path.join(BASE_DIR, "fernet.key")

# === GERAR/RECUPERAR CHAVE FERNET ===
if os.path.exists(FERNET_KEY):
    key = open(FERNET_KEY, "rb").read()
else:
    key = Fernet.generate_key()
    with open(FERNET_KEY, "wb") as f:
        f.write(key)
fernet = Fernet(key)

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

# === BANCO DE USUÁRIOS (CRIPTOGRAFADO) ===
def load_users() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("usuarios", [])

def save_users(users: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"usuarios": users}, f, ensure_ascii=False, indent=2)

def find_user(username):
    users = load_users()
    for user in users:
        if decrypt(user["usuario"]) == username:
            return user
    return None

# === FLASK APP ===
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_super_secreta_local")

# === ROTAS ===

@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("painel_operacao"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Preencha todos os campos.", "danger")
            return render_template("register.html")
        if find_user(username):
            flash("Usuário já existe.", "danger")
            return render_template("register.html")
        users = load_users()
        new_user = {
            "usuario": encrypt(username),
            "senha": encrypt(password),
            "binance_key": "",
            "binance_secret": "",
            "openai_key": ""
        }
        users.append(new_user)
        save_users(users)
        flash("Cadastro realizado! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = find_user(username)
        if user and decrypt(user["senha"]) == password:
            session["usuario"] = username
            flash("Login realizado!", "success")
            return redirect(url_for("painel_operacao"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("login"))

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    if request.method == "POST":
        binance_key    = request.form.get("binance_api_key", "").strip()
        binance_secret = request.form.get("binance_api_secret", "").strip()
        openai_key     = request.form.get("gpt_api_key", "").strip()
        updated = False
        if binance_key:
            user["binance_key"] = encrypt(binance_key)
            updated = True
        if binance_secret:
            user["binance_secret"] = encrypt(binance_secret)
            updated = True
        if openai_key:
            user["openai_key"] = encrypt(openai_key)
            updated = True
        if updated:
            # Atualiza usuário
            users = load_users()
            for u in users:
                if decrypt(u["usuario"]) == username:
                    u.update(user)
            save_users(users)
            flash("Chaves atualizadas!", "success")
            return redirect(url_for("painel_operacao"))
        else:
            flash("Preencha pelo menos um campo para atualizar.", "danger")
    has_binance = bool(user["binance_key"] and user["binance_secret"])
    has_openai  = bool(user["openai_key"])
    return render_template(
        "configurar.html",
        user={
            "binance_api_key": decrypt(user["binance_key"]) if user["binance_key"] else "",
            "binance_api_secret": decrypt(user["binance_secret"]) if user["binance_secret"] else "",
            "gpt_api_key": decrypt(user["openai_key"]) if user["openai_key"] else ""
        },
        has_binance=has_binance,
        has_openai=has_openai
    )

@app.route("/painel_operacao")
def painel_operacao():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    user = find_user(username)
    saldo_btc = saldo_usdt = "0"
    erro_binance = None
    # Busca saldo real na Binance
    try:
        if user["binance_key"] and user["binance_secret"]:
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
        else:
            erro_binance = "Chaves Binance não configuradas."
    except Exception as e:
        erro_binance = f"Erro Binance: {e}"

    return render_template(
        "painel_operacao.html",
        user={"username": username},
        saldo_btc=saldo_btc,
        saldo_usdt=saldo_usdt,
        erro_binance=erro_binance
    )

@app.route("/executar_ordem", methods=["POST"])
def executar_ordem():
    if "usuario" not in session:
        return jsonify({"status": "erro", "mensagem": "Não autenticado"}), 401
    username = session["usuario"]
    user = find_user(username)
    if not (user["binance_key"] and user["binance_secret"]):
        return jsonify({"status": "erro", "mensagem": "Chaves Binance não configuradas."}), 400
    data = request.get_json(force=True)
    tipo_ordem = data.get("tipo_ordem")
    simbolo = data.get("simbolo", "BTCUSDT")
    quantidade = data.get("quantidade", "0.001")
    try:
        client = Client(
            decrypt(user["binance_key"]),
            decrypt(user["binance_secret"])
        )
        if tipo_ordem == "compra":
            ordem = client.create_order(
                symbol=simbolo, side="BUY", type="MARKET", quantity=quantidade
            )
        elif tipo_ordem == "venda":
            ordem = client.create_order(
                symbol=simbolo, side="SELL", type="MARKET", quantity=quantidade
            )
        else:
            return jsonify({"status": "erro", "mensagem": "Tipo de ordem inválido."}), 400
        return jsonify({"status": "sucesso", "mensagem": f"Ordem executada: {tipo_ordem.upper()} {quantidade} {simbolo}", "ordem": ordem})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao executar ordem: {e}"}), 400

@app.route("/sugestao_gpt", methods=["POST"])
def sugestao_gpt():
    if "usuario" not in session:
        return jsonify({"erro": "Não autenticado"}), 401
    username = session["usuario"]
    user = find_user(username)
    if not user["openai_key"]:
        return jsonify({"erro": "Chave GPT não configurada."}), 400
    prompt = request.json.get("prompt", "Faça uma sugestão de operação para BTCUSDT com análise técnica.")
    openai.api_key = decrypt(user["openai_key"])
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é uma IA especialista em operações de criptomoedas, foque em sinais claros de compra/venda, alvo, stop e explicação breve."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        texto = resposta.choices[0].message.content.strip()
        return jsonify({"sugestao": texto})
    except Exception as e:
        return jsonify({"erro": f"Erro GPT: {str(e)}"}), 400

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", mensagem="Página não encontrada."), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template("error.html", mensagem="Erro interno do servidor. Tente novamente mais tarde."), 500

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host=host, port=port)