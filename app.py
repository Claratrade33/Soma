# app.py
from __future__ import annotations
import os
import json
from pathlib import Path
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
    Client = None  # se a lib não estiver instalada no runtime

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
# Armazenamento simples das credenciais (arquivo em disco do container)
# Obs.: em novo deploy do Render esse arquivo é recriado (não persistente).
# -----------------------------------------------------------------------------
CREDS_PATH = Path("./storage/keys.json")
CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_creds() -> dict:
    if CREDS_PATH.exists():
        try:
            return json.loads(CREDS_PATH.read_text())
        except Exception:
            return {}
    return {}

def save_creds(api_key: str, api_secret: str) -> None:
    CREDS_PATH.write_text(json.dumps({"api_key": api_key, "api_secret": api_secret}))

# -----------------------------------------------------------------------------
# Helpers Binance
# -----------------------------------------------------------------------------
def safe_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")

def client_from_env() -> Client | None:
    """Client usando variáveis de ambiente (se existirem)."""
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

def client_from_saved() -> Client | None:
    """Client usando as credenciais salvas no arquivo (se existirem)."""
    if Client is None:
        return None
    creds = load_creds()
    key = creds.get("api_key")
    sec = creds.get("api_secret")
    if not key or not sec:
        return None
    try:
        return Client(api_key=key, api_secret=sec)
    except Exception:
        return None

def get_binance_client() -> Client | None:
    """
    Preferir as credenciais salvas no painel; se não houver, tentar env vars.
    """
    return client_from_saved() or client_from_env()

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

# ---- Corretora: formulário no painel para inserir/testar/salvar chaves ------
@bp_usuarios.route("/configurar-api", methods=["GET", "POST"])
@login_required
def configurar_api():
    status, msg = None, None
    creds = load_creds()
    api_key = creds.get("api_key", "")
    api_secret = creds.get("api_secret", "")

    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        api_secret = request.form.get("api_secret", "").strip()

        if not api_key or not api_secret:
            status, msg = "erro", "Preencha API Key e API Secret."
        else:
            try:
                if Client is None:
                    raise RuntimeError("Biblioteca python-binance indisponível.")
                # testa conexão rápida
                manual = Client(api_key=api_key, api_secret=api_secret)
                manual.ping()
                manual.get_account()
                save_creds(api_key, api_secret)
                status, msg = "ok", "Credenciais salvas com sucesso. ✅ Conectado!"
                flash(msg, "success")
                return redirect(url_for("usuarios.configurar_api"))
            except Exception as e:
                status, msg = "erro", f"Falha ao conectar: {e}"
                flash(msg, "danger")

    # visão rápida se houver credenciais válidas
    quick = {"usdt": "0", "abertas": 0}
    try:
        c = get_binance_client()
        if c:
            bal = c.get_asset_balance(asset="USDT") or {}
            quick["usdt"] = str(bal.get("free", "0"))
            quick["abertas"] = len(c.get_open_orders() or [])
    except Exception:
        pass

    return render_template(
        "painel/corretora.html",
        api_key=api_key,
        api_secret=api_secret,
        status=status,
        msg=msg,
        quick=quick,
    )

@bp_usuarios.route("/ordens")
@login_required
def ordens():
    """Lista últimas ordens de um símbolo (padrão BTCUSDT)."""
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    orders = []
    error = None
    client = get_binance_client()
    if client is None:
        error = (
            "Defina as chaves em /usuario/configurar-api ou nas variáveis "
            "de ambiente BINANCE_API_KEY / BINANCE_API_SECRET."
        )
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
    lucro_24h = Decimal("0")  # spot não tem PnL 24h simples; deixamos 0 por ora
    alert = None

    client = get_binance_client()
    if client is None:
        alert = (
            "Para ver dados reais, cadastre suas chaves em "
            "Corretora ou defina BINANCE_API_KEY e BINANCE_API_SECRET."
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