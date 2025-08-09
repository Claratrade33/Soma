import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from db import SessionLocal, init_db
from models import UserCredential, OrderLog
from services.crypto import enc, dec
from services.binance_client import (
    make_client, test_account, get_symbol_price, get_free_usdt,
    place_market_order, place_limit_order,
    place_stop_loss_limit, place_take_profit_limit, place_oco_order
)
from inteligencia.ai_client import sugerir_quantidade

bp_api = Blueprint("usuario_api", __name__, url_prefix="/usuario")
init_db()  # garante as tabelas

# ---------- helpers ----------
def _get_cred(user_id: str, exchange: str) -> UserCredential | None:
    with SessionLocal() as s:
        return s.execute(
            select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.exchange == exchange
            )
        ).scalar_one_or_none()

def _log_order(user_id, exchange, symbol, side, tipo, qty, price, resp):
    with SessionLocal() as s:
        s.add(OrderLog(
            user_id=user_id, exchange=exchange, symbol=symbol, side=side,
            tipo=tipo, qty=qty, price=price,
            status="ok" if resp.get("ok") else "error",
            resp_json=json.dumps(resp)
        ))
        s.commit()

# ---------- rotas ----------
@bp_api.route("/configurar-api", methods=["GET", "POST"])
def configurar_api():
    """
    Form para o usuário cadastrar a própria API/Secret da corretora.
    Armazenamos criptografado (Fernet) no SQLite.
    """
    user_id = "demo-user"                 # em produção, pegue do login
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
                    user_id=user_id, exchange=exchange,
                    api_key_enc=enc(api_key), api_secret_enc=enc(api_secret)
                )
                s.add(cred)
            else:
                cred.api_key_enc = enc(api_key)
                cred.api_secret_enc = enc(api_secret)
            s.commit()

        flash("Credenciais salvas com sucesso. ✅", "success")
        return redirect(url_for(".testar_api", exchange=exchange))

    has_cred = _get_cred(user_id, exchange) is not None
    return render_template("usuarios/config_api.html", exchange=exchange, has_cred=has_cred)

@bp_api.route("/testar-api")
def testar_api():
    """
    Mostra status da conexão, preço do símbolo, saldo USDT (ou simulado),
    e formulário para ordens + sugestão via IA.
    """
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

    # se vier redirecionado da sugestão de IA
    sug_text = request.args.get("sug_text")
    sug_qty = request.args.get("sug_qty")

    return render_template(
        "usuarios/teste_api.html",
        exchange=exchange, result=result, price=price, symbol=symbol, free_usdt=free_usdt,
        sug_text=sug_text, sug_qty=sug_qty
    )

@bp_api.route("/sugestao-ia", methods=["POST"])
def sugestao_ia():
    """
    IA sugere quantidade (baseado em risco, saldo e preço atual).
    """
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
    return redirect(url_for(".testar_api",
                            exchange=exchange, symbol=symbol,
                            sug_text=sug["texto"], sug_qty=(sug["qty"] or "")))

@bp_api.route("/ordem-enviar", methods=["POST"])
def ordem_enviar():
    """
    Envia ordem MARKET/LIMIT/STOP_LOSS_LIMIT/TAKE_PROFIT_LIMIT/OCO.
    Paper trading é respeitado dentro do services.binance_client (PAPER_TRADING=true).
    """
    user_id = "demo-user"
    exchange = "binance"
    cred = _get_cred(user_id, exchange)
    if not cred:
        flash("Cadastre sua API primeiro.", "warning")
        return redirect(url_for(".configurar_api", exchange=exchange))

    symbol = request.form.get("symbol", "BTCUSDT")
    side = request.form.get("side", "BUY")
    tipo = request.form.get("tipo", "MARKET").upper()

    qty = float(request.form.get("qty", "0.001") or "0.001")
    price = float(request.form.get("price", "0") or "0")

    stop_price = float(request.form.get("stop_price", "0") or "0")
    stop_limit_price = float(request.form.get("stop_limit_price", "0") or "0")
    take_profit_price = float(request.form.get("take_profit_price", "0") or "0")

    client = make_client(dec(cred.api_key_enc), dec(cred.api_secret_enc))

    if tipo == "LIMIT":
        resp = place_limit_order(client, symbol=symbol, side=side, qty=qty, price=price)
    elif tipo == "STOP_LOSS_LIMIT":
        resp = place_stop_loss_limit(client, symbol=symbol, side=side, qty=qty,
                                     stop_price=stop_price, limit_price=price or stop_limit_price)
    elif tipo == "TAKE_PROFIT_LIMIT":
        resp = place_take_profit_limit(client, symbol=symbol, side=side, qty=qty,
                                       stop_price=take_profit_price, limit_price=price)
    elif tipo == "OCO":
        # Normalmente OCO é SELL (alvo + stop) quando já tem posição comprada
        resp = place_oco_order(client, symbol=symbol, side=side, qty=qty,
                               price=price, stop_price=stop_price, stop_limit_price=stop_limit_price or stop_price)
    else:
        resp = place_market_order(client, symbol=symbol, side=side, qty=qty)

    _log_order(user_id, exchange, symbol, side, tipo, qty, price, resp)
    return render_template("usuarios/ordem_resultado.html",
                           symbol=symbol, side=side, qty=qty, resp=resp, tipo=tipo, price=price)

@bp_api.route("/historico")
def historico():
    """
    Lista o histórico de ordens (paper/real) gravado no SQLite.
    """
    user_id = "demo-user"
    with SessionLocal() as s:
        logs = s.execute(
            select(OrderLog).where(OrderLog.user_id == user_id).order_by(OrderLog.id.desc())
        ).scalars().all()
    return render_template("usuarios/historico.html", logs=logs)