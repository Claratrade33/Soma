from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from db import SessionLocal, init_db
from models import UserCredential, OrderLog
from services.crypto import enc, dec
from services.binance_client import (
    make_client, test_account, get_symbol_price, get_free_usdt,
    place_market_order, place_limit_order, place_stop_loss_limit,
    place_take_profit_limit, place_oco_order
)
from inteligencia.ai_client import sugerir_quantidade

# Blueprint correto
bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")
init_db()

@bp_api.route("/configurar-api", methods=["GET", "POST"])
def configurar_api():
    user_id = "demo-user"
    exchange = request.values.get("exchange", "binance")
    session = SessionLocal()

    if request.method == "POST":
        api_key = request.form.get("api_key")
        api_secret = request.form.get("api_secret")
        if not api_key or not api_secret:
            flash("Preencha todas as chaves", "danger")
            return redirect(url_for("usuario_api.configurar_api"))
        cred = session.get(UserCredential, user_id)
        if not cred:
            cred = UserCredential(id=user_id, exchange=exchange)
        cred.api_key_enc = enc(api_key)
        cred.api_secret_enc = enc(api_secret)
        session.add(cred)
        session.commit()
        flash("Credenciais salvas com sucesso!", "success")
        return redirect(url_for("usuario_api.configurar_api"))

    cred = session.get(UserCredential, user_id)
    api_key_dec = dec(cred.api_key_enc) if cred else ""
    return render_template("configurar_api.html", api_key=api_key_dec, exchange=exchange)

@bp_api.route("/testar-api")
def testar_api():
    user_id = "demo-user"
    session = SessionLocal()
    cred = session.get(UserCredential, user_id)
    if not cred:
        flash("Configure suas credenciais primeiro.", "danger")
        return redirect(url_for("usuario_api.configurar_api"))

    api_key = dec(cred.api_key_enc)
    api_secret = dec(cred.api_secret_enc)
    ok, msg = test_account(api_key, api_secret)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("usuario_api.configurar_api"))

@bp_api.route("/historico")
def historico():
    session = SessionLocal()
    ordens = session.scalars(select(OrderLog).order_by(OrderLog.data.desc())).all()
    return render_template("historico.html", ordens=ordens)