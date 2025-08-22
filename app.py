from __future__ import annotations
import os
from decimal import Decimal
from typing import Optional, Dict, Any

from flask import (
    Flask, render_template, render_template_string,
    request, redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required
)

# -------------------------------------------------------------------
# Binance (python-binance)
# -------------------------------------------------------------------
try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException, BinanceRequestException
except Exception:
    Client = None
    BinanceAPIException = Exception
    BinanceRequestException = Exception


# -------------------------------------------------------------------
# App & Login
# -------------------------------------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

login_manager = LoginManager(app)
login_manager.login_view = "usuarios.login"


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


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def get_binance_client() -> Optional[Client]:
    """Cria um cliente Binance baseado em variáveis de ambiente.
    Lê tanto de 'Environment Variables' quanto de 'Secret Files' (.env) do Render.
    """
    if Client is None:
        return None

    # 1) Variáveis de ambiente
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # 2) (Opcional) Secret Files: /etc/secrets/.env
    #    Se você guardou lá, o Render injeta no ambiente automaticamente;
    #    então o passo 1 já cobre. Este bloco é só redundância segura.
    if not api_key or not api_secret:
        env_path = "/etc/secrets/.env"
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k == "BINANCE_API_KEY" and not api_key:
                            api_key = v
                        if k == "BINANCE_API_SECRET" and not api_secret:
                            api_secret = v
            except Exception:
                pass

    if not api_key or not api_secret:
        return None

    # Se quiser usar testnet, defina BINANCE_TESTNET=true
    use_testnet = os.getenv("BINANCE_TESTNET", "").lower() in {"1", "true", "yes"}

    try:
        client = Client(api_key=api_key, api_secret=api_secret, testnet=use_testnet)
        # Uma chamada leve pra validar rapidamente as credenciais:
        _ = client.get_server_time()
        return client
    except Exception:
        return None


def safe_decimal(x: Any) -> Decimal:
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")


# -------------------------------------------------------------------
# Blueprints
# -------------------------------------------------------------------
from flask import Blueprint

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
    # usa templates/index.html se existir; senão, form inline
    try:
        return render_template("index.html")
    except Exception:
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Entrar — ClaraVerse{% endblock %}
        {% block content %}
          <div class="row justify-content-center">
            <div class="col-md-6">
              <h3 class="mb-3">Entrar</h3>
              <form method="post">
                <div class="mb-3">
                  <label class="form-label">Usuário</label>
                  <input name="username" class="form-control" value="admin">
                </div>
                <div class="mb-3">
                  <label class="form-label">Senha</label>
                  <input type="password" name="password" class="form-control" value="Claraverse2025">
                </div>
                <button class="btn btn-primary w-100">Entrar</button>
              </form>
            </div>
          </div>
        {% endblock %}
        """)


@bp_usuarios.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("index"))


@bp_usuarios.route("/configurar-api")
@login_required
def configurar_api():
    has_keys = bool(os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_API_SECRET"))
    # tenta validar também com uma chamada real
    client = get_binance_client()
    valid = client is not None
    try:
        return render_template("painel/corretora.html", has_keys=has_keys and valid)
    except Exception:
        # fallback
        msg = ("✅ As variáveis de ambiente estão OK e a conexão valida."
               if (has_keys and valid) else
               "⚠️ Defina BINANCE_API_KEY e BINANCE_API_SECRET em Settings → Environment ou Secret Files.")
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Corretora — Configurar API{% endblock %}
        {% block content %}
          <h3 class="mb-3">Configurar API da Corretora (Binance)</h3>
          <div class="alert {{ 'alert-success' if has else 'alert-warning' }}">{{ msg }}</div>
          <a class="btn btn-primary" href="{{ url_for('painel.dashboard') }}">Ir para o Painel</a>
        {% endblock %}
        """, has=(has_keys and valid), msg=msg)


@bp_usuarios.route("/ordens")
@login_required
def ordens():
    symbol = (request.args.get("symbol") or "BTCUSDT").upper()
    error = None
    orders: list[Dict[str, Any]] = []
    client = get_binance_client()
    if client is None:
        error = "Credenciais ausentes ou inválidas. Confira as permissões da chave no painel da Binance."
    else:
        try:
            orders = client.get_all_orders(symbol=symbol, limit=20) or []
        except (BinanceAPIException, BinanceRequestException) as e:
            error = f"Erro Binance: {e}"
        except Exception as e:
            error = f"Erro inesperado: {e}"

    try:
        return render_template("painel/ordens.html", symbol=symbol, orders=orders, error=error)
    except Exception:
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Ordens{% endblock %}
        {% block content %}
          <h3 class="mb-3">Ordens — {{ symbol }}</h3>
          {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
          {% elif not orders %}
            <div class="alert alert-info">Nenhuma ordem encontrada.</div>
          {% else %}
            <pre class="bg-dark text-white p-3 rounded">{{ orders|tojson(indent=2) }}</pre>
          {% endif %}
        {% endblock %}
        """, symbol=symbol, orders=orders, error=error)


@bp_usuarios.route("/historico")
@login_required
def historico():
    try:
        return render_template("painel/historico.html")
    except Exception:
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Histórico{% endblock %}
        {% block content %}
          <h3 class="mb-3">Histórico</h3>
          <p class="text-muted">Seu histórico de operações aparecerá aqui.</p>
        {% endblock %}
        """)


# ------------------------- PAINEL (FORÇAR DADOS REAIS) -----------------------
@bp_painel.route("/operacao")
@login_required
def dashboard():
    """Busca SEMPRE na Binance. Se falhar, mostra erro e zera os cards."""
    saldo = Decimal("0")
    abertas = 0
    lucro_24h = Decimal("0")  # placeholder
    alert = None

    client = get_binance_client()
    if client is None:
        alert = ("Credenciais ausentes/invalidas OU sem permissão. "
                 "Na Binance, marque 'Enable Reading' e 'Enable Spot & Margin Trading'.")
    else:
        try:
            bal = client.get_asset_balance(asset="USDT") or {}
            saldo = safe_decimal(bal.get("free") or bal.get("total") or "0")
        except (BinanceAPIException, BinanceRequestException) as e:
            alert = f"Erro ao buscar saldo na Binance: {e}"
        except Exception as e:
            alert = f"Erro inesperado ao buscar saldo: {e}"

        try:
            oo = client.get_open_orders() or []
            abertas = len(oo)
        except (BinanceAPIException, BinanceRequestException) as e:
            alert = f"Erro ao buscar ordens abertas: {e}"
        except Exception as e:
            alert = f"Erro inesperado ao buscar ordens: {e}"

    # Tenta usar o template real; senão, fallback com o mesmo conteúdo
    try:
        return render_template(
            "painel/dashboard.html",
            saldo=str(saldo), lucro_24h=str(lucro_24h), abertas=abertas, alert=alert
        )
    except Exception:
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Dashboard — Operações{% endblock %}
        {% block content %}
          <h2 class="mb-3">Dashboard</h2>
          {% if alert %}<div class="alert alert-warning">{{ alert }}</div>{% endif %}
          <div class="row g-3 mb-4">
            <div class="col-md-4"><div class="card p-3 h-100">
              <h6 class="text-muted">Saldo</h6>
              <div class="display-6">{{ saldo }} <small class="text-muted">USDT</small></div>
            </div></div>
            <div class="col-md-4"><div class="card p-3 h-100">
              <h6 class="text-muted">Lucro (24h)</h6>
              <div class="display-6">{{ lucro_24h }} <small class="text-muted">USDT</small></div>
            </div></div>
            <div class="col-md-4"><div class="card p-3 h-100">
              <h6 class="text-muted">Operações Abertas</h6>
              <div class="display-6">{{ abertas }}</div>
            </div></div>
          </div>
          <div class="card p-3">
            <h5>Destaques</h5>
            <ul class="mb-0">
              <li>BTC/USDT — exemplo</li>
              <li>ETH/USDT — exemplo</li>
            </ul>
          </div>
        {% endblock %}
        """, saldo=str(saldo), lucro_24h=str(lucro_24h), abertas=abertas, alert=alert)


@bp_painel.route("/")
@login_required
def painel_root():
    return redirect(url_for("painel.dashboard"))


# ------------------------- AUTOMÁTICO (placeholder) --------------------------
@bp_auto.route("/painel")
@login_required
def painel_automatico():
    try:
        return render_template("painel/automatico.html")
    except Exception:
        return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Operações Automáticas{% endblock %}
        {% block content %}
          <h3 class="mb-3">Painel — Automático</h3>
          <p class="text-muted">Aqui ficará o controle das estratégias automáticas.</p>
        {% endblock %}
        """)


# -------------------------------------------------------------------
# Raiz & health
# -------------------------------------------------------------------
@app.get("/")
def index():
    try:
        return render_template("index.html")
    except Exception:
        # fallback simples de boas-vindas
        return render_template_string("""
        <!doctype html>
        <title>ClaraVerse</title>
        <div class="container py-5">
          <h1 class="mb-3">Bem-vinda 👋</h1>
          <p class="text-muted">Use usuário <b>admin</b> e senha <b>Claraverse2025</b>.</p>
          <a class="btn btn-primary" href="{{ url_for('usuarios.login') }}">Entrar</a>
        </div>
        """)


@app.get("/healthz")
def healthz():
    return {"ok": True}


# -------------------------------------------------------------------
# Registra blueprints
# -------------------------------------------------------------------
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_painel)
app.register_blueprint(bp_auto)


# -------------------------------------------------------------------
# Run local
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)