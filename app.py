import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from clarinha_core import clarinha_responder
from crypto_utils import criptografar

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_super_secreta_local")

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
        # TODO: Substituir por validação real em banco de dados
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
        # TODO: Salvar novo usuário em banco de dados
        flash("Cadastro concluído! Agora faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    if request.method == "POST":
        usuario         = session["usuario"]
        binance_key     = request.form.get("binance_key")
        binance_secret  = request.form.get("binance_secret")
        openai_key      = request.form.get("openai_key")

        # Criptografa e salva as chaves no sistema local
        criptografar(binance_key, usuario)
        criptografar(binance_secret, usuario)
        criptografar(openai_key, usuario)

        flash("Chaves salvas com sucesso!", "success")
    return render_template("configurar.html")

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
