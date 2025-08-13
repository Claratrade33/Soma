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

# -------- Binance (python-binance) ----------
try:
    from binance.client import Client  # pip install python-binance
except Exception:
    Client = None  # se a lib não vier por algum motivo, não quebra o app

# -----------------------------------------------------------------------------
# App & Login
# -----------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

login_manager = LoginManager(app)
login_manager.login_view = "usuarios.login"

# -----------------------------------------------------------------------------
# Usuário único em memória (admin fixo)
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
    """Cria o client da Binance se as variáveis de ambiente existirem."""
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
    """
    POST: autentica admin / Claraverse2025 e redireciona para o painel.
    GET: renderiza a home (index) com o form embutido.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN.username and password == ADMIN.password:
            login_user(ADMIN)
            flash("Login efetuado com sucesso.", "success")
            return redirect(url_for("painel.dashboard"))
        flash("Credenciais inválidas.", "danger")
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
    """
    Tela de instruções: nesta versão as chaves são lidas de variáveis de ambiente:
    BINANCE_API_KEY / BINANCE_API_SECRET (Render → Settings → Environment).
    """
    has_keys = bool(os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_API_SECRET"))
    return render_template("painel/corretora.html", has_keys=has_keys)

@bp_usuarios.route("/ordens")
@login_required
def ordens():
    """
    Lista as últimas ordens (abertas/fechadas) do símbolo informado.
    OBS: para ordens abertas especificamente, usamos client.get_open_orders().
    """
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    orders = []
    error = None
    client = get_binance_client()
    if client is None:
        error = "Defina BINANCE_API_KEY e BINANCE_API_SECRET no Render (Environment)."
    else:
        try:
            orders = client.get_all_orders(symbol=symbol, limit=15) or []
        except Exception as e:
            error = f"Não foi possível carregar ordens ({e})."
    return render_template("painel/ordens.html", symbol=symbol, orders=orders, error=error)

@bp_usuarios.route("/historico")
@login_required
def historico():
    """
    Histórico automático: usa get_my_trades para trazer as últimas operações executadas.
    """
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    trades = []
    error = None
    client = get_binance_client()
    if client is None:
        error = "Defina BINANCE_API_KEY e BINANCE_API_SECRET no Render (Environment)."
    else:
        try:
            # até 50 últimas negociações do símbolo
            trades = client.get_my_trades(symbol=symbol, limit=50) or []
            # normaliza timestamp em string amigável no próprio template (ou aqui se preferir)
            # deixaremos o timestamp bruto e o template mostra direto
        except Exception as e:
            error = f"Não foi possível carregar histórico ({e})."
    return render_template("painel/historico.html", symbol=symbol, trades=trades, error=error)

# ------------------------- PAINEL (OPERAÇÃO) ---------------------------------
@bp_painel.route("/operacao")
@login_required
def dashboard():
    """
    Painel com saldo USDT, ordens abertas e lucro 24h (placeholder).
    """
    saldo = Decimal("0")
    abertas = 0
    lucro_24h = Decimal("0")
    alert = None

    client = get_binance_client()
    if client is None:
        alert = (
            "Para ver dados reais, defina as variáveis BINANCE_API_KEY e "
            "BINANCE_API_SECRET no Render → Settings → Environment."
        )
    else:
        try:
            bal = client.get_asset_balance(asset="USDT") or {}
            saldo = safe_decimal(bal.get("free", "0"))
        except Exception as e:
            alert = f"Falha ao buscar saldo ({e})."
        try:
            open_orders = client.get_open_orders() or []
            abertas = len(open_orders)
        except Exception as e:
            alert = f"Falha ao buscar ordens abertas ({e})."

    return render_template(
        "painel/dashboard.html",
        saldo=str(saldo), lucro_24h=str(lucro_24h), abertas=abertas, alert=alert
    )

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