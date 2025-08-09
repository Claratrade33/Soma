# usuarios/rotas_api.py
from __future__ import annotations
import os, time
from typing import Optional

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException

from services.crypto import enc, dec

# ==== modelos (compatível com seus nomes) ====================================
from db import SessionLocal
try:
    # novo nome sugerido
    from models import UserCredential
except Exception:
    UserCredential = None  # type: ignore

try:
    # nome antigo visto em alguns commits
    from models import BinanceKey
except Exception:
    BinanceKey = None  # type: ignore

try:
    from models import OrderHistory
except Exception:
    OrderHistory = None  # type: ignore
# ============================================================================

bp_api = Blueprint("usuario_api", __name__, template_folder="../templates")

def _get_cred(s) -> Optional[object]:
    """Carrega credencial do usuário (UserCredential ou BinanceKey)."""
    uid = int(current_user.id)
    if UserCredential is not None:
        return s.query(UserCredential).filter(UserCredential.user_id == uid).one_or_none()
    if BinanceKey is not None:
        return s.query(BinanceKey).filter(BinanceKey.user_id == uid).one_or_none()
    return None

def _ensure_cred_model():
    if not (UserCredential or BinanceKey):
        raise RuntimeError("Nenhum modelo de credencial encontrado no models.py (UserCredential / BinanceKey).")

def _save_cred(api_key: str, api_secret: str, testnet: bool):
    _ensure_cred_model()
    with SessionLocal() as s:
        row = _get_cred(s)
        if row is None:
            if UserCredential is not None:
                row = UserCredential(user_id=int(current_user.id))
            else:
                row = BinanceKey(user_id=int(current_user.id))  # type: ignore
            s.add(row)

        row.api_key_enc = enc(api_key)    # bytes
        row.api_secret_enc = enc(api_secret)  # bytes
        # alguns schemas usam flag testnet, outros campo base_url; tratamos os dois
        if hasattr(row, "testnet"):
            row.testnet = bool(testnet)
        if hasattr(row, "api_base"):
            row.api_base = "https://testnet.binance.vision" if testnet else "https://api.binance.com"
        s.commit()

def _load_plain_credentials():
    _ensure_cred_model()
    with SessionLocal() as s:
        row = _get_cred(s)
        if row is None:
            return None
        api_key = dec(row.api_key_enc)
        api_secret = dec(row.api_secret_enc)
        testnet = getattr(row, "testnet", False)
        api_base = getattr(row, "api_base", None)
        return {"api_key": api_key, "api_secret": api_secret, "testnet": testnet, "api_base": api_base}

def _make_binance_client(creds):
    testnet = bool(creds.get("testnet"))
    api_base = creds.get("api_base")
    # prioridade: o que está salvo; depois ENV; fallback mainnet
    if not api_base:
        if testnet or os.getenv("BINANCE_TESTNET", "false").lower() in ("1", "true", "yes"):
            api_base = "https://testnet.binance.vision"
        else:
            api_base = "https://api.binance.com"

    client = BinanceClient(creds["api_key"], creds["api_secret"])
    client.API_URL = api_base.rstrip("/")
    return client, api_base

# -------------------------- ROTAS --------------------------------------------

@bp_api.route("/usuario/configurar-api", methods=["GET", "POST"])
@login_required
def configurar_api():
    """Tela p/ salvar API/Secret da Binance (criptografado)."""
    msg_ok = None
    existing = None
    try:
        existing = _load_plain_credentials()
    except Exception as e:
        flash(f"Erro ao carregar credenciais: {e}", "danger")

    if request.method == "POST":
        api_key = (request.form.get("api_key") or "").strip()
        api_secret = (request.form.get("api_secret") or "").strip()
        testnet = request.form.get("testnet") == "on"
        if not api_key or not api_secret:
            flash("Preencha API Key e Secret.", "warning")
            return redirect(url_for("usuario_api.configurar_api"))
        try:
            _save_cred(api_key, api_secret, testnet)
            msg_ok = "Credenciais salvas com sucesso!"
            existing = _load_plain_credentials()
        except Exception as e:
            flash(f"Erro ao salvar: {e}", "danger")

    return render_template(
        "usuario/configurar_api.html",
        saved=existing is not None,
        existing=existing,
        msg_ok=msg_ok
    )

@bp_api.route("/usuario/testar-api", methods=["GET", "POST"])
@login_required
def testar_api():
    """Testa conexão, mostra saldo USDT e permite enviar uma ordem de MARKET."""
    creds = _load_plain_credentials()
    if not creds:
        flash("Salve suas credenciais primeiro.", "warning")
        return redirect(url_for("usuario_api.configurar_api"))

    client, api_base = _make_binance_client(creds)

    # Info de conta
    status = {"conectado": False, "api_base": api_base, "usdt_free": None, "price": None, "symbol": "BTCUSDT"}
    try:
        account = client.get_account()
        status["conectado"] = True
        balances = {b["asset"]: float(b["free"]) for b in account.get("balances", [])}
        status["usdt_free"] = balances.get("USDT", 0.0)
        status["price"] = float(client.get_symbol_ticker(symbol=status["symbol"])["price"])
    except Exception as e:
        flash(f"Falha ao consultar conta: {e}", "danger")

    order_result = None
    if request.method == "POST":
        symbol = (request.form.get("symbol") or "BTCUSDT").upper()
        side = (request.form.get("side") or "BUY").upper()
        qty = request.form.get("qty") or "0.001"
        try:
            order_result = client.create_order(symbol=symbol, side=side, type="MARKET", quantity=qty)
            flash("Ordem enviada!", "success")
        except BinanceAPIException as e:
            flash(f"Erro Binance: {e.message}", "danger")
        except Exception as e:
            flash(f"Falha ao enviar ordem: {e}", "danger")

    return render_template(
        "usuario/testar_api.html",
        st=status,
        order_result=order_result
    )

@bp_api.route("/usuario/historico")
@login_required
def historico():
    """Lista histórico local (se existir a tabela) ou mostra dica."""
    rows = []
    if OrderHistory is not None:
        with SessionLocal() as s:
            try:
                rows = (
                    s.query(OrderHistory)
                    .filter(OrderHistory.user_id == int(current_user.id))
                    .order_by(OrderHistory.created_at.desc())
                    .limit(200)
                    .all()
                )
            except Exception:
                rows = []
    return render_template("usuario/historico.html", rows=rows, has_local=OrderHistory is not None)