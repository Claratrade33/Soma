# app.py
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
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
# Helpers
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


def to_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except (InvalidOperation, Exception):
        return Decimal("0")


def fmt_decimal(d: Decimal, places: int = 8) -> str:
    # corta zeros à direita de forma amigável
    q = d.quantize(Decimal(10) ** -places)
    s = f"{q:.{places}f}".rstrip("0").rstrip(".")
    return s if s else "0"


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
    Dashboard agora lista os principais saldos do usuário (Spot) por ativo
    e também mostra o balanço de USDT dos Futuros USD-M (se houver).
    Também somamos as ordens abertas de Spot + Futuros.
    """
    alert_msgs: list[str] = []
    spot_rows: list[dict] = []     # [{asset, free, locked, total}]
    futures_usdt_balance = Decimal("0")
    abertas_total = 0
    lucro_24h = Decimal("0")       # placeholder

    client = get_binance_client()
    if client is None:
        alert_msgs.append(
            "Defina BINANCE_API_KEY e BINANCE_API_SECRET em Settings → Environment (no Render)."
        )
        return render_template(
            "painel/dashboard.html",
            alert="<br>".join(alert_msgs),
            abertas=abertas_total,
            lucro_24h=fmt_decimal(lucro_24h, 2),
            saldo_total_usdt="0",
            spot_rows=[],
            futures_usdt="0"
        )

    # ----------------- SPOT: todos os ativos com saldo -----------------
    try:
        acct = client.get_account() or {}
        balances = acct.get("balances", [])
        # somamos free + locked e filtramos quem tem algo (>0)
        for b in balances:
            asset = b.get("asset")
            free = to_decimal(b.get("free", "0"))
            locked = to_decimal(b.get("locked", "0"))
            total = free + locked
            if total > 0:
                spot_rows.append(
                    {
                        "asset": asset,
                        "free": free,
                        "locked": locked,
                        "total": total,
                        "free_str": fmt_decimal(free),
                        "locked_str": fmt_decimal(locked),
                        "total_str": fmt_decimal(total),
                    }
                )
    except Exception as e:
        alert_msgs.append(f"Falha ao buscar saldos Spot ({e}).")

    # ordena decrescente por total
    spot_rows.sort(key=lambda r: r["total"], reverse=True)

    # saldo “principal”: se houver USDT no spot, usamos; caso contrário 0
    saldo_usdt_spot = next((r["total"] for r in spot_rows if r["asset"] == "USDT"), Decimal("0"))

    # ----------------- SPOT: ordens abertas -----------------
    try:
        abertas_spot = client.get_open_orders() or []
        abertas_total += len(abertas_spot)
    except Exception as e:
        alert_msgs.append(f"Falha ao buscar ordens Spot ({e}).")

    # ----------------- FUTUROS USD-M: balanço USDT + ordens -----------------
    try:
        f_balances = client.futures_account_balance() or []
        usdt_row = next((r for r in f_balances if r.get("asset") == "USDT"), None)
        if usdt_row:
            futures_usdt_balance = to_decimal(usdt_row.get("balance", "0"))
        try:
            f_open = client.futures_get_open_orders() or []
            abertas_total += len(f_open)
        except Exception as e:
            alert_msgs.append(f"Falha ao buscar ordens Futuros ({e}).")
    except Exception as e:
        # pode falhar se a conta não tiver futuros habilitado
        alert_msgs.append(f"Falha ao buscar saldo Futuros ({e}).")

    # total “USDT” combinando Spot(USDT) + Futuros(USDT)
    saldo_total_usdt = saldo_usdt_spot + futures_usdt_balance

    return render_template(
        "painel/dashboard.html",
        alert="<br>".join(alert_msgs) if alert_msgs else None,
        abertas=abertas_total,
        lucro_24h=fmt_decimal(lucro_24h, 2),
        saldo_total_usdt=fmt_decimal(saldo_total_usdt, 2),
        spot_rows=spot_rows,
        futures_usdt=fmt_decimal(futures_usdt_balance, 2),
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