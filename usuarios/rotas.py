# usuarios/rotas.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from db import SessionLocal
from models import Usuario

# ESTE NOME É O QUE O app.py IMPORTA: "bp"
bp = Blueprint("usuarios", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    # Se já está logado, manda pro painel
    if current_user.is_authenticated:
        return redirect(url_for("painel_operacao.painel_operacao"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        if not username or not password:
            flash("Preencha usuário e senha.", "warning")
            return redirect(url_for("usuarios.login"))

        with SessionLocal() as s:
            user = s.query(Usuario).filter(Usuario.username == username).one_or_none()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash("Login feito com sucesso!", "success")
                return redirect(url_for("painel_operacao.painel_operacao"))
            else:
                flash("Usuário ou senha inválidos.", "danger")
                return redirect(url_for("usuarios.login"))

    # Tela de login (usa o index.html como landing de login)
    return render_template("index.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua sessão.", "info")
    return redirect(url_for("usuarios.login"))