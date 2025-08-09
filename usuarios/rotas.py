from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from db import SessionLocal
from models import Usuario

bp = Blueprint("usuarios", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        with SessionLocal() as s:
            user = s.query(Usuario).filter(Usuario.username == username).one_or_none()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Usuário ou senha inválidos.", "danger")
                return redirect(url_for(".login"))
        login_user(user, remember=True)
        return redirect(url_for("painel_operacao.painel_operacao"))
    return render_template("index.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sessão.", "info")
    return redirect(url_for(".login"))