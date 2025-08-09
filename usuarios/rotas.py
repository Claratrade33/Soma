import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from db import SessionLocal, init_db
from models import UserCredential
from services.crypto import enc, dec
from services.binance_client import make_client, test_account, get_symbol_price, place_market_order

bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")
init_db()  # garante tabelas

def _get_cred(user_id: str, exchange: str) -> UserCredential | None:
    with SessionLocal() as s:
        row = s.execute(select(UserCredential).where(
            UserCredential.user_id == user_id, UserCredential.exchange == exchange
        )).scalar_one_or_none()
        return row

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
                cred = UserCredential(
                    user_id=user_id,
                    exchange=exchange,
                    api_key_enc=enc(api_key),
                    api_secret_enc=enc(api_secret),
                )
                s.add(cred)
            else:
                cred.api_key_enc = enc(api_key)
                cred.api_secret_enc = enc(api_secret)
            s.commit()

        flash("Credenciais salvas.", "success")
        return redirect(url_for(".testar_api", exchange=exchange))

    # GET
    has_cred = _get_cred(user_id, exchange) is not None
    return render_template("usuarios/config_api.html", exchange=exchange, has_cred=has_cred)

@bp_api.route("/testar-api")
def testar_api():
    user_id = "demo-user"
    exchange = request.args.get("exchange", "binance")
    cred = _get_cred(user_id, exchange)
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api", exchange=exchange))

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))
    result = test_account(client)
    price = get_symbol_price(client, "BTCUSDT")

    return render_template("usuarios/teste_api.html", exchange=exchange, result=result, price=price)

@bp_api.route("/ordem-teste", methods=["POST"])
def ordem_teste():
    """
    Coloca uma ordem de mercado pequenininha (TESTNET).
    """
    user_id = "demo-user"
    symbol = request.form.get("symbol", "BTCUSDT")
    side = request.form.get("side", "BUY")
    qty = float(request.form.get("qty", "0.001"))

    cred = _get_cred(user_id, "binance")
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api"))

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))
    resp = place_market_order(client, symbol=symbol, side=side, qty=qty)

    return render_template("usuarios/ordem_resultado.html", symbol=symbol, side=side, qty=qty, resp=resp)