# usuarios/rotas_api.py
from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, flash
from sqlalchemy import select, desc
from db import SessionLocal, init_db
from models import UserCredential, OrderLog
from services.crypto import enc, dec
from services.binance_client import (
    make_client, test_account, get_symbol_price, get_free_usdt,
    place_market_order, place_limit_order, place_stop_loss_limit,
    place_take_profit_limit, place_oco_order
)
from inteligencia.ai_client import sugerir_quantidade

# Blueprint CORRETO
bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")
init_db()

# helper pra pegar cred por user_id
def _get_cred(session, user_id: str) -> UserCredential | None:
    return session.execute(
        select(UserCredential).where(UserCredential.user_id == user_id)
    ).scalar_one_or_none()

@bp_api.route("/configurar-api", methods=["GET", "POST"])
def configurar_api():
    session = SessionLocal()
    user_id = "demo-user"
    exchange = (request.values.get("exchange") or "binance").lower()

    if request.method == "POST":
        api_key = (request.form.get("api_key") or "").strip()
        api_secret = (request.form.get("api_secret") or "").strip()
        if not api_key or not api_secret:
            flash("Preencha API Key e Secret.", "danger")
            return redirect("/usuario/configurar-api")

        cred = _get_cred(session, user_id)
        if not cred:
            cred = UserCredential(user_id=user_id, exchange=exchange,
                                  api_key_enc=enc(api_key), api_secret_enc=enc(api_secret))
        else:
            cred.exchange = exchange
            cred.api_key_enc = enc(api_key)
            cred.api_secret_enc = enc(api_secret)
        session.add(cred); session.commit()
        flash("Credenciais salvas com sucesso!", "success")
        return redirect("/usuario/configurar-api")

    cred = _get_cred(session, user_id)
    has_cred = bool(cred)
    return render_template("usuarios/config_api.html", has_cred=has_cred)

@bp_api.route("/testar-api", methods=["GET"])
def testar_api():
    session = SessionLocal()
    user_id = "demo-user"
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()

    cred = _get_cred(session, user_id)
    if not cred:
        flash("Configure suas credenciais primeiro.", "warning")
        return redirect("/usuario/configurar-api")

    api_key = dec(cred.api_key_enc)
    api_secret = dec(cred.api_secret_enc)

    client = make_client(api_key, api_secret)
    acc = test_account(client)
    price = get_symbol_price(client, symbol) or 0.0
    free_usdt = get_free_usdt(client)

    return render_template(
        "usuarios/teste_api.html",
        result=acc, price=price, free_usdt=free_usdt, symbol=symbol,
        sug_text=None, sug_qty=None
    )

@bp_api.route("/sugestao-ia", methods=["POST"])
def sugestao_ia():
    session = SessionLocal()
    user_id = "demo-user"
    symbol = (request.form.get("symbol") or "BTCUSDT").upper()
    risco = (request.form.get("risco") or "conservador").lower()

    cred = _get_cred(session, user_id)
    if not cred:
        flash("Configure suas credenciais primeiro.", "warning")
        return redirect("/usuario/configurar-api")

    api_key = dec(cred.api_key_enc)
    api_secret = dec(cred.api_secret_enc)

    client = make_client(api_key, api_secret)
    price = get_symbol_price(client, symbol) or 0.0
    free_usdt = get_free_usdt(client)

    sug = sugerir_quantidade(symbol, price, free_usdt, risco=risco)
    return render_template(
        "usuarios/teste_api.html",
        result=test_account(client), price=price, free_usdt=free_usdt, symbol=symbol,
        sug_text=sug.get("texto"), sug_qty=sug.get("qty")
    )

@bp_api.route("/ordem-enviar", methods=["POST"])
def ordem_enviar():
    session = SessionLocal()
    user_id = "demo-user"

    symbol = (request.form.get("symbol") or "BTCUSDT").upper()
    side = (request.form.get("side") or "BUY").upper()
    tipo = (request.form.get("tipo") or "MARKET").upper()
    qty = float(request.form.get("qty") or 0) or 0.0
    price = float(request.form.get("price") or 0) or 0.0
    stop_price = float(request.form.get("stop_price") or 0) or 0.0
    stop_limit_price = float(request.form.get("stop_limit_price") or 0) or 0.0

    cred = _get_cred(session, user_id)
    if not cred:
        flash("Configure suas credenciais primeiro.", "warning")
        return redirect("/usuario/configurar-api")

    api_key = dec(cred.api_key_enc)
    api_secret = dec(cred.api_secret_enc)
    client = make_client(api_key, api_secret)

    # envia
    if tipo == "MARKET":
        resp = place_market_order(client, symbol=symbol, side=side, qty=qty)
    elif tipo == "LIMIT":
        resp = place_limit_order(client, symbol=symbol, side=side, qty=qty, price=price)
    elif tipo == "STOP_LOSS_LIMIT":
        resp = place_stop_loss_limit(client, symbol=symbol, side=side, qty=qty,
                                     stop_price=stop_price, limit_price=price or stop_limit_price)
    elif tipo == "TAKE_PROFIT_LIMIT":
        resp = place_take_profit_limit(client, symbol=symbol, side=side, qty=qty,
                                       stop_price=stop_price, limit_price=price or stop_limit_price)
    elif tipo == "OCO":
        resp = place_oco_order(client, symbol=symbol, side=side, qty=qty,
                               price=price, stop_price=stop_price, stop_limit_price=stop_limit_price)
    else:
        resp = {"ok": False, "error": f"Tipo de ordem não suportado: {tipo}"}

    # log
    log = OrderLog(
        user_id=user_id, exchange=cred.exchange, symbol=symbol, side=side,
        tipo=tipo, qty=qty, price=price or 0.0,
        status="ok" if resp.get("ok") else "error",
        resp_json=str(resp)
    )
    session.add(log); session.commit()

    return render_template("usuarios/ordem_resultado.html",
                           symbol=symbol, side=side, tipo=tipo, qty=qty, price=price, resp=resp)

@bp_api.route("/historico", methods=["GET"])
def historico():
    session = SessionLocal()
    rows = session.execute(
        select(OrderLog).order_by(desc(OrderLog.created_at))
    ).scalars().all()
    return render_template("usuarios/historico.html", logs=rows)