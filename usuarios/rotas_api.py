# usuarios/rotas_api.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.binance_client import get_test_client
from models import UserCredential, OrderHistory, db

bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")

@bp_api.route("/configurar-api", methods=["GET", "POST"])
@login_required
def configurar_api():
    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        api_secret = request.form.get("api_secret", "").strip()
        cred = UserCredential.upsert(user_id=current_user.id, api_key=api_key, api_secret=api_secret)
        db.session.add(cred)
        db.session.commit()
        flash("Credenciais salvas com sucesso.", "success")
        return redirect(url_for("usuario_api.configurar_api"))
    cred = UserCredential.query.filter_by(user_id=current_user.id).first()
    return render_template("usuarios/configurar_api.html", cred=cred)

@bp_api.route("/testar-api")
@login_required
def testar_api():
    client = get_test_client(current_user.id)
    ok, data = client.ping()
    if ok:
        flash("Conectado!", "success")
    else:
        flash(f"Erro: {data}", "danger")
    return render_template("usuarios/testar_api.html", data=data)

@bp_api.route("/historico")
@login_required
def historico():
    ordens = OrderHistory.query.filter_by(user_id=current_user.id).order_by(OrderHistory.created_at.desc()).all()
    return render_template("usuarios/historico.html", ordens=ordens)