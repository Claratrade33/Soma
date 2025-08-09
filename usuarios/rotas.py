import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from db import SessionLocal, init_db
from models import UserCredential
from services.crypto import enc, dec
from services.binance_client import (
    make_client, test_account, get_symbol_price, place_market_order, place_limit_order, get_free_usdt
)
from inteligencia.ai_client import sugerir_quantidade

bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")
init_db()

def _get_cred(user_id: str, exchange: str) -> UserCredential | None:
    with SessionLocal() as s:
        return s.execute(
            select(UserCredential).where(UserCredential.user_id == user_id, UserCredential.exchange == exchange)
        ).scalar_one_or_none()

@bp_api.route("/configurar-api", methods=["GET", "POST"])
def configurar_api():
    user_id = "demo-user"
    exchange = request.values.get("exchange", "binance")

    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        api_secret = request.form.get("api_secret", "").strip()
        if not api_key or not api_secret:
            flash("Preencha API Key e Secret.", "danger")
            return redirect(url_for(".configurar_api", exchange=exchange))

        with SessionLocal() as s:
            cred = _get_cred(user_id, exchange)
            if cred is None:
                cred = UserCredential(user_id=user_id, exchange=exchange,
                                      api_key_enc=enc(api_key), api_secret_enc=enc(api_secret))
                s.add(cred)
            else:
                cred.api_key_enc = enc(api_key)
                cred.api_secret_enc = enc(api_secret)
            s.commit()

        flash("Credenciais salvas.", "success")
        return redirect(url_for(".testar_api", exchange=exchange))

    has_cred = _get_cred(user_id, exchange) is not None
    return render_template("usuarios/config_api.html", exchange=exchange, has_cred=has_cred)

@bp_api.route("/testar-api")
def testar_api():
    user_id = "demo-user"
    exchange = request.args.get("exchange", "binance")
    symbol = request.args.get("symbol", "BTCUSDT")

    cred = _get_cred(user_id, exchange)
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api", exchange=exchange))

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))
    result = test_account(client)
    price = get_symbol_price(client, symbol)
    free_usdt = get_free_usdt(client)

    sug_text = request.args.get("sug_text")  # opcional (quando vier da IA)
    sug_qty = request.args.get("sug_qty")

    return render_template(
        "usuarios/teste_api.html",
        exchange=exchange, result=result, price=price, symbol=symbol, free_usdt=free_usdt,
        sug_text=sug_text, sug_qty=sug_qty
    )

@bp_api.route("/sugestao-ia", methods=["POST"])
def sugestao_ia():
    user_id = "demo-user"
    exchange = "binance"
    symbol = request.form.get("symbol", "BTCUSDT")
    risco = request.form.get("risco", "conservador")

    cred = _get_cred(user_id, exchange)
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api", exchange=exchange))

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))
    price = get_symbol_price(client, symbol) or 0.0
    free_usdt = get_free_usdt(client)

    sug = sugerir_quantidade(symbol, price, free_usdt, risco)
    # Redireciona de volta com sugestão preenchida
    return redirect(url_for(".testar_api", exchange=exchange, symbol=symbol, sug_text=sug["texto"], sug_qty=(sug["qty"] or "")))

@bp_api.route("/ordem-enviar", methods=["POST"])
def ordem_enviar():
    user_id = "demo-user"
    exchange = "binance"
    cred = _get_cred(user_id, exchange)
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api", exchange=exchange))

    symbol = request.form.get("symbol", "BTCUSDT")
    side = request.form.get("side", "BUY")
    tipo = request.form.get("tipo", "MARKET")
    qty = float(request.form.get("qty", "0.001") or "0.001")
    price = request.form.get("price", "")
    price = float(price) if price else 0.0

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))

    if tipo == "LIMIT":
        resp = place_limit_order(client, symbol=symbol, side=side, qty=qty, price=price)
    else:
        resp = place_market_order(client, symbol=symbol, side=side, qty=qty)

    return render_template("usuarios/ordem_resultado.html", symbol=symbol, side=side, qty=qty, resp=resp, tipo=tipo, price=price)