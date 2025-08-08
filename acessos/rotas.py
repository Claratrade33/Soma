"""Rotas de autenticação e registro de usuários.

Centraliza as views relacionadas a login, logout e criação de contas.
Utiliza Flask-Login para gerenciamento de sessão.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Usuario

from . import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Exibe formulário de login e autentica o usuário."""
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            return redirect(url_for("painel_operacao"))
        flash("Credenciais inválidas.", "error")
    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Permite criação de novos usuários."""
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if Usuario.query.filter_by(usuario=usuario).first():
            flash("Usuário já existe.", "error")
        else:
            senha_hash = generate_password_hash(senha)
            novo_user = Usuario(usuario=usuario, senha_hash=senha_hash)
            db.session.add(novo_user)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("acessos.login"))
    return render_template("usuarios/novo_usuario.html")


@bp.route("/logout")
@login_required
def logout():
    """Finaliza a sessão do usuário atual."""
    logout_user()
    return redirect(url_for("acessos.login"))

