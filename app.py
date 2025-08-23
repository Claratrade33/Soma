# app.py
from __future__ import annotations

import os
from decimal import Decimal
from flask import (
    Flask, render_template, render_template_string,
    request, redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    current_user, login_required
)
from flask import Blueprint

# -------- Binance ----------
try:
    from binance.client import Client  # python-binance
except Exception:
    Client = None  # se a lib não estiver disponível no build

# Exceções da Binance (com fallback para não quebrar o import)
try:
    from binance.exceptions import BinanceAPIException, BinanceRequestException
except Exception:
    BinanceAPIException = Exception
    BinanceRequestException = Exception

# -----------------------------------------------------------------------------
# App & Login
# -----------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

login_manager = LoginManager(app)
login_manager.login_view = "usuarios.login"

# -----------------------------------------------------------------------------
# Usuário em memória (admin fixo)
# -----------------------------------------------------------------------------
class AdminUser(UserMixin):
    def __init__(self) -> None:
        self.id = "admin"
        self.username = "admin"
        self.password = "Claraverse2025"

    def get_id(self) -> str:  # type: ignore[override]
        return self.id

ADMIN = AdminUser()

@login_manager.user_loader
def load_user(user_id: str):
    return ADMIN if user_id == ADMIN.id else None

# -----------------------------------------------------------------------------
# Helpers Binance
# -----------------------------------------------------------------------------
def get_binance_client() -> Client | None:
    """Cria o client se as variáveis de ambiente existirem."""
    if Client is None:
        return None
    key = os.getenv("BINANCE_API_KEY")
    sec = os.getenv("BINANCE_API_SECRET")
    if not key or not sec:
        return None
    try:
        return Client(api_key=key, api_secret=sec)
    except Exception:
        return None

def safe_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")

# -----------------------------------------------------------------------------
# Blueprints
# -----------------------------------------------------------------------------
bp_usuarios = Blueprint("usuarios", __name__, url_prefix="/usuario")
bp_painel = Blueprint("painel", __name__, url_prefix="/painel")
bp_auto = Blueprint("operacoes_automatico", __name__, url_prefix="/operacoes_automatico")

# ------------------------- USUÁRIOS ------------------------------------------
@bp_usuarios.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN.username and password == ADMIN.password:
            login_user(ADMIN)
            flash("Login efetuado com sucesso.", "success")
            return redirect(url_for("painel.dashboard"))
        flash("Credenciais inválidas.", "danger")
    # reaproveita o index como tela de login
    return render_template("index.html")

@bp_usuarios.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("index"))

@bp_usuarios.route("/configurar-api")
@login_required
def configurar_api():
    # Só instruções/checagem; nesta versão usamos variáveis de ambiente
    has_keys = bool(os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_API_SECRET"))
    return render_template("painel/corretora.html", has_keys=has_keys)

@bp_usuarios.route("/ordens")
@login_required
def ordens():
    """
    Mostra últimas ordens para um símbolo:
    1) tenta Spot (get_all_orders)
    2) se não houver, tenta Futuros USD-M (futures_get_open_orders)
    """
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    client = get_binance_client()
    error = None
    orders = []
    fonte = "spot"

    if client is None:
        error = "Defina BINANCE_API_KEY e BINANCE_API_SECRET no Render (Environment)."
    else:
        # Spot
        try:
            orders = client.get_all_orders(symbol=symbol, limit=15) or []
        except Exception as e:
            error = f"Spot: {e}"

        # Se não achou nada em Spot, tenta Futuros (USD-M)
        if not orders:
            try:
                fonte = "futuros"
                orders = client.futures_get_open_orders(symbol=symbol) or []
                error = None  # sucesso em futuros
            except Exception as e:
                error = (error + f" | Futuros: {e}") if error else f"Futuros: {e}"

    return render_template(
        "painel/ordens.html",
        symbol=symbol, orders=orders, error=error, fonte=fonte
    )

@bp_usuarios.route("/historico")
@login_required
def historico():
    return render_template("painel/historico.html")

# ------------------------- PAINEL (OPERACAO) ---------------------------------
@bp_painel.route("/operacao")
@login_required
def dashboard():
    """
    Dashboard que soma saldo de USDT em Spot + Futuros USD-M
    e conta ordens abertas (Spot + Futuros). O lucro_24h fica placeholder (0).
    """
    saldo = Decimal("0")
    abertas = 0
    lucro_24h = Decimal("0")
    alert_msgs = []

    client = get_binance_client()
    if client is None:
        alert_msgs.append(
            "Defina BINANCE_API_KEY e BINANCE_API_SECRET em Settings → Environment (no Render)."
        )
        return render_template(
            "painel/dashboard.html",
            saldo=str(saldo), lucro_24h=str(lucro_24h), abertas=abertas,
            alert="<br>".join(alert_msgs)
        )

    # ------- SPOT -------
    try:
        bal = client.get_asset_balance(asset="USDT") or {}
        spot_free = safe_decimal(bal.get("free", "0"))
        saldo += spot_free
        try:
            abertas_spot = client.get_open_orders() or []
            abertas += len(abertas_spot)
        except Exception as e:
            alert_msgs.append(f"Falha ao buscar ordens Spot ({e}).")
    except Exception as e:
        alert_msgs.append(f"Falha ao buscar saldo Spot ({e}).")

    # ------- FUTUROS USD-M -------
    try:
        f_balances = client.futures_account_balance() or []
        usdt_row = next((r for r in f_balances if r.get("asset") == "USDT"), None)
        if usdt_row:
            saldo += safe_decimal(usdt_row.get("balance", "0"))
        try:
            f_open = client.futures_get_open_orders() or []
            abertas += len(f_open)
        except Exception as e:
            alert_msgs.append(f"Falha ao buscar ordens Futuros ({e}).")
    except Exception as e:
        alert_msgs.append(f"Falha ao buscar saldo Futuros ({e}).")

    return render_template(
        "painel/dashboard.html",
        saldo=str(saldo),
        lucro_24h=str(lucro_24h),   # placeholder por enquanto
        abertas=abertas,
        alert="<br>".join(alert_msgs) if alert_msgs else None
    )

# Alias /painel → /painel/operacao
@bp_painel.route("/")
@login_required
def painel_root():
    return redirect(url_for("painel.dashboard"))

# ------------------------- AUTOMÁTICO ----------------------------------------
@bp_auto.route("/painel")
@login_required
def painel_automatico():
    return render_template("painel/automatico.html")

# ------------------------- DEBUG BINANCE -------------------------------------
@app.get("/debug/binance")
@login_required
def debug_binance():
    """
    Página de diagnóstico: mostra ping, horário do servidor,
    saldos spot (ativos com quantidade > 0), saldo de futuros (linhas),
    contagem de ordens abertas em Spot e Futuros.
    Em erros, exibe mensagens cruas da API.
    """
    client = get_binance_client()
    if client is None:
        return render_template_string(
            "<pre>Sem cliente Binance. Verifique BINANCE_API_KEY e BINANCE_API_SECRET.</pre>"
        )

    info = {"ok": True, "errors": []}

    # Ping e server time
    try:
        info["ping"] = client.ping()
        info["server_time"] = client.get_server_time()
    except Exception as e:
        info["errors"].append(f"Ping/ServerTime: {e}")

    # Spot balances (todos > 0)
    try:
        account = client.get_account() or {}
        balances = account.get("balances", [])
        non_zero = [
            b for b in balances
            if (Decimal(b.get("free", "0")) > 0) or (Decimal(b.get("locked", "0")) > 0)
        ]
        info["spot_balances"] = non_zero[:50]
    except (BinanceAPIException, BinanceRequestException) as e:
        info["errors"].append(f"Spot balances: {e}")
    except Exception as e:
        info["errors"].append(f"Spot balances (gen): {e}")

    # Spot open orders
    try:
        info["spot_open_orders_count"] = len(client.get_open_orders() or [])
    except (BinanceAPIException, BinanceRequestException) as e:
        info["errors"].append(f"Spot open orders: {e}")
    except Exception as e:
        info["errors"].append(f"Spot open orders (gen): {e}")

    # Futuros: saldo/ordens
    try:
        info["futures_account_balance"] = client.futures_account_balance()
    except (BinanceAPIException, BinanceRequestException) as e:
        info["errors"].append(f"Futures balance: {e}")
    except Exception as e:
        info["errors"].append(f"Futures balance (gen): {e}")

    try:
        info["futures_open_orders_count"] = len(client.futures_get_open_orders() or [])
    except (BinanceAPIException, BinanceRequestException) as e:
        info["errors"].append(f"Futures open orders: {e}")
    except Exception as e:
        info["errors"].append(f"Futures open orders (gen): {e}")

    return render_template_string("<pre>{{ info | tojson(indent=2) }}</pre>", info=info)

# -----------------------------------------------------------------------------
# Rotas principais
# -----------------------------------------------------------------------------
@app.get("/")
def index():
    return render_template("index.html")

@app.get("/healthz")
def healthz():
    return {"ok": True}

# -----------------------------------------------------------------------------
# Registro dos blueprints
# -----------------------------------------------------------------------------
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_painel)
app.register_blueprint(bp_auto)

# -----------------------------------------------------------------------------
# Execução local
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)