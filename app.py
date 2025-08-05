from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key")

# Configuração do banco SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

# Criar banco e garantir admin
@app.before_first_request
def criar_admin():
    db.create_all()
    admin = Usuario.query.filter_by(usuario="admin").first()
    if not admin:
        senha_hash = generate_password_hash("claraverse2025")
        novo_admin = Usuario(usuario="admin", senha_hash=senha_hash)
        db.session.add(novo_admin)
        db.session.commit()

@app.route("/")
def index():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return redirect(url_for("painel_operacao"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha_hash, senha):
            session["logado"] = True
            session["usuario"] = usuario
            return redirect(url_for("painel_operacao"))
        flash("Credenciais inválidas.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if Usuario.query.filter_by(usuario=usuario).first():
            flash("Usuário já existe.", "error")
        else:
            senha_hash = generate_password_hash(senha)
            novo_user = Usuario(usuario=usuario, senha_hash=senha_hash)
            db.session.add(novo_user)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/painel_operacao")
def painel_operacao():
    if not session.get("logado"):
        return redirect(url_for("login"))
    return render_template("painel_operacao.html")

if __name__ == "__main__":
    app.run(debug=True)