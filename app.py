# app.py
from __future__ import annotations

import os
import logging
from decimal import Decimal
from flask import (
    Flask, render_template, render_template_string,
    request, redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required
)
from flask import Blueprint

# -------- Binance (python-binance) ----------
try:
    from binance.client import Client  # type: ignore
except Exception:
    Client = None  # se a lib não estiver disponível

# -----------------------------------------------------------------------------
# App & Login
# -----------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

login_manager = LoginManager(app)
login_manager.login_view = "usuarios.login"

logging.basicConfig(level=logging.INFO)
SECRETS_DIR = "/etc/secrets"  # Secret Files do Render

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
# Helpers gerais
# -----------------------------------------------------------------------------
def _read_secret_file(varname: str) -> str | None:
    """Lê um Secret File com o mesmo nome da env var (Render monta em /etc/secrets)."""
    try:
        path = os.path.join(SECRETS_DIR, varname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                value = f.read().strip()
                return value or None
    except Exception:
        pass
    return None

def get_env_or_secret(varname: str) -> str | None:
    """Pega primeiro de ENV; se ausente, tenta Secret Files."""
    v = os.getenv(varname)
    if v and v.strip():
        return v.strip()
    return _read_secret_file(varname)

def safe_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")

# -------- Binance helpers ----------
def get_binance_client() -> Client | None:
    """Cria o client se as variáveis existirem (ENV ou Secret Files)."""
    if Client is None:
        logging.warning("python-binance não disponível (Client=None)")
        return None

    key = get_env_or_secret("BINANCE_API_KEY")
    sec = get_env_or_secret("BINANCE_API_SECRET")

    logging.info(
        "Binance keys? BINANCE_API_KEY=%s, BINANCE_API_SECRET=%s",
        "present" if key else "absent",
        "present" if sec else "absent",
    )

    if not key or not sec:
        return None
    try:
        return Client(api_key=key, api_secret=sec)
    except Exception as e:
        logging.exception("Falha ao criar Client da Binance: %s", e)
        return None

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
    # verifica ENV e/ou Secret Files
    has_key = bool(get_env_or_secret("BINANCE_API_KEY"))
    has_sec = bool(get_env_or_secret("BINANCE_API_SECRET"))
    has_keys = has_key and has_sec
    return render_template("painel/corretora.html", has_keys=has_keys)

@bp_usuarios.route("/ordens")
@login_required
def ordens():
    """Lista últimas ordens de um símbolo (padrão BTCUSDT)."""
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    orders = []
    error = None
    client = get_binance_client()
    if client is None:
        error = "Defina BINANCE_API_KEY e BINANCE_API_SECRET nas Environment Variables (ou Secret Files)."
    else:
        try:
            orders = client.get_all_orders(symbol=symbol, limit=15)
        except Exception as e:
            error = f"Não foi possível carregar ordens ({e})."
    return render_template("painel/ordens.html", symbol=symbol, orders=orders, error=error)

@bp_usuarios.route("/historico")
@login_required
def historico():
    return render_template("painel/historico.html")

# ------------------------- PAINEL (OPERACAO) ---------------------------------
@bp_painel.route("/operacao")
@login_required
def dashboard():
    """Preenche cards com saldo USDT, ordens abertas e (placeholder) lucro 24h."""
    saldo = Decimal("0")
    abertas = 0
    lucro_24h = Decimal("0")
    alert = None

    client = get_binance_client()
    if client is None:
        alert = (
            "Para ver dados reais, defina BINANCE_API_KEY e BINANCE_API_SECRET "
            "em Settings → Environment (ou como Secret Files)."
        )
    else:
        try:
            bal = client.get_asset_balance(asset="USDT") or {}
            saldo = safe_decimal(bal.get("free", "0"))
        except Exception as e:
            alert = f"Falha ao buscar saldo ({e})."
        try:
            abertas = len(client.get_open_orders() or [])
        except Exception as e:
            alert = f"Falha ao buscar ordens abertas ({e})."

    return render_template(
        "painel/dashboard.html",
        saldo=str(saldo), lucro_24h=str(lucro_24h), abertas=abertas, alert=alert
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

# --- diagnóstico: não vaza valores, só presença/ausência ---
@app.get("/debug/env")
def debug_env():
    info = {
        "BINANCE_API_KEY": "present" if get_env_or_secret("BINANCE_API_KEY") else "absent",
        "BINANCE_API_SECRET": "present" if get_env_or_secret("BINANCE_API_SECRET") else "absent",
    }
    return info, 200

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